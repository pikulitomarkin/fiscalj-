"""
Repositório de acesso a dados (Data Access Layer).
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import json

from src.database.models import NFSeEmissao, LogProcessamento, Usuario
from src.models.schemas import ProcessingResult
from src.utils.logger import app_logger
from config.database import get_db_session


class NFSeRepository:
    """Repositório para operações de NFS-e."""
    
    async def save_nfse(self, nfse_data: Dict[str, Any], usuario: str = "admin") -> int:
        """
        Salva uma NFS-e emitida no banco.
        
        Args:
            nfse_data: Dicionário com dados da NFS-e
            usuario: Nome do usuário que executou
            
        Returns:
            ID do registro criado
        """
        async with get_db_session() as session:
            # Verificar se já existe
            chave = nfse_data.get('chave_acesso')
            if chave:
                stmt = select(NFSeEmissao).where(NFSeEmissao.chave_acesso == chave)
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    app_logger.debug(f"NFS-e já existe no banco: {chave[:20]}...")
                    return existing.id
            
            emissao = NFSeEmissao(
                chave_acesso=nfse_data.get('chave_acesso'),
                numero_nfse=nfse_data.get('numero'),
                cpf_tomador=nfse_data.get('tomador_cpf', '').replace('.', '').replace('-', '').replace('/', ''),
                nome_tomador=nfse_data.get('tomador_nome'),
                status='sucesso',
                valor_servico=nfse_data.get('valor'),
                valor_iss=nfse_data.get('iss'),
                xml_path=nfse_data.get('xml_path'),
                pdf_path=nfse_data.get('pdf_path'),
                resultado_json=json.dumps(nfse_data.get('resultado_completo', {}), default=str),
                data_emissao=datetime.now(),
                data_processamento=datetime.now(),
                usuario=usuario
            )
            
            session.add(emissao)
            await session.flush()
            
            app_logger.info(f"NFS-e salva no banco: ID={emissao.id}, Chave={chave[:20] if chave else 'N/A'}...")
            
            return emissao.id
    
    async def save_batch_nfse(self, nfse_list: List[Dict[str, Any]], usuario: str = "admin") -> List[int]:
        """
        Salva múltiplas NFS-e em lote.
        
        Args:
            nfse_list: Lista de dicionários com dados das NFS-e
            usuario: Nome do usuário
            
        Returns:
            Lista de IDs criados
        """
        ids = []
        
        for nfse_data in nfse_list:
            try:
                id = await self.save_nfse(nfse_data, usuario)
                ids.append(id)
            except Exception as e:
                app_logger.error(f"Erro ao salvar NFS-e: {e}")
        
        app_logger.info(f"{len(ids)} NFS-e salvas no banco")
        
        return ids
    
    async def get_all_nfse(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retorna todas as NFS-e do banco.
        
        Args:
            limit: Limite de registros
            
        Returns:
            Lista de dicionários com dados das NFS-e
        """
        async with get_db_session() as session:
            stmt = (
                select(NFSeEmissao)
                .where(NFSeEmissao.status == 'sucesso')
                .order_by(desc(NFSeEmissao.created_at))
                .limit(limit)
            )
            result = await session.execute(stmt)
            emissoes = result.scalars().all()
            
            return [e.to_dict() for e in emissoes]
    
    async def save_emissao(self, result: ProcessingResult, usuario: str = "admin") -> int:
        """
        Salva resultado de emissão no banco.
        
        Args:
            result: Resultado do processamento
            usuario: Nome do usuário que executou
            
        Returns:
            ID do registro criado
        """
        async with get_db_session() as session:
            emissao = NFSeEmissao(
                hash_transacao=result.hash_transacao,
                numero_nfse=result.numero_nfse,
                protocolo=result.protocolo,
                cpf_tomador=result.cpf_tomador,
                nome_tomador=result.nome_tomador,
                status=result.status,
                mensagem=result.mensagem,
                data_processamento=result.timestamp,
                usuario=usuario
            )
            
            session.add(emissao)
            await session.flush()
            
            app_logger.debug(f"Emissão salva: ID={emissao.id}, Hash={result.hash_transacao[:8]}...")
            
            return emissao.id
    
    async def save_batch_results(
        self,
        results: List[ProcessingResult],
        usuario: str = "admin"
    ) -> List[int]:
        """
        Salva múltiplos resultados em lote.
        
        Args:
            results: Lista de resultados
            usuario: Nome do usuário
            
        Returns:
            Lista de IDs criados
        """
        ids = []
        
        async with get_db_session() as session:
            for result in results:
                emissao = NFSeEmissao(
                    hash_transacao=result.hash_transacao,
                    numero_nfse=result.numero_nfse,
                    protocolo=result.protocolo,
                    cpf_tomador=result.cpf_tomador,
                    nome_tomador=result.nome_tomador,
                    status=result.status,
                    mensagem=result.mensagem,
                    data_processamento=result.timestamp,
                    usuario=usuario
                )
                
                session.add(emissao)
            
            await session.flush()
            
            ids = [e.id for e in session.new]
        
        app_logger.info(f"{len(ids)} emissões salvas no banco")
        
        return ids
    
    async def get_emissao_by_hash(self, hash_transacao: str) -> Optional[NFSeEmissao]:
        """Busca emissão por hash de transação."""
        async with get_db_session() as session:
            stmt = select(NFSeEmissao).where(NFSeEmissao.hash_transacao == hash_transacao)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_emissoes_by_cpf(self, cpf: str, limit: int = 100) -> List[NFSeEmissao]:
        """Busca emissões por CPF do tomador."""
        async with get_db_session() as session:
            stmt = (
                select(NFSeEmissao)
                .where(NFSeEmissao.cpf_tomador == cpf)
                .order_by(NFSeEmissao.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def get_estatisticas(self, dias: int = 30) -> Dict[str, Any]:
        """
        Retorna estatísticas de emissões.
        
        Args:
            dias: Número de dias para considerar
            
        Returns:
            Dicionário com estatísticas
        """
        data_inicio = datetime.utcnow() - timedelta(days=dias)
        
        async with get_db_session() as session:
            # Total de emissões
            stmt_total = select(func.count(NFSeEmissao.id)).where(
                NFSeEmissao.created_at >= data_inicio
            )
            total = await session.scalar(stmt_total)
            
            # Sucessos
            stmt_sucesso = select(func.count(NFSeEmissao.id)).where(
                and_(
                    NFSeEmissao.created_at >= data_inicio,
                    NFSeEmissao.status == 'sucesso'
                )
            )
            sucessos = await session.scalar(stmt_sucesso)
            
            # Erros
            stmt_erro = select(func.count(NFSeEmissao.id)).where(
                and_(
                    NFSeEmissao.created_at >= data_inicio,
                    NFSeEmissao.status == 'erro'
                )
            )
            erros = await session.scalar(stmt_erro)
            
            return {
                'total_emissoes': total or 0,
                'sucessos': sucessos or 0,
                'erros': erros or 0,
                'taxa_sucesso': (sucessos / total * 100) if total else 0,
                'periodo_dias': dias
            }


class LogRepository:
    """Repositório para logs de processamento."""
    
    async def create_log(
        self,
        total_registros: int,
        nome_arquivo: str,
        usuario: str = "admin"
    ) -> str:
        """
        Cria um novo log de processamento.
        
        Args:
            total_registros: Total de registros a processar
            nome_arquivo: Nome do arquivo processado
            usuario: Usuário que executou
            
        Returns:
            Batch ID (UUID)
        """
        batch_id = str(uuid.uuid4())
        
        async with get_db_session() as session:
            log = LogProcessamento(
                batch_id=batch_id,
                total_registros=total_registros,
                nome_arquivo=nome_arquivo,
                usuario=usuario,
                status='processando'
            )
            
            session.add(log)
        
        app_logger.info(f"Log criado: Batch={batch_id}")
        
        return batch_id
    
    async def update_log(
        self,
        batch_id: str,
        sucessos: int,
        erros: int,
        status: str = 'concluido'
    ):
        """
        Atualiza log com resultados do processamento.
        
        Args:
            batch_id: ID do lote
            sucessos: Número de sucessos
            erros: Número de erros
            status: Status final
        """
        async with get_db_session() as session:
            stmt = select(LogProcessamento).where(LogProcessamento.batch_id == batch_id)
            result = await session.execute(stmt)
            log = result.scalar_one_or_none()
            
            if log:
                log.sucessos = sucessos
                log.erros = erros
                log.status = status
                log.fim_processamento = datetime.utcnow()
                
                # Calcula duração
                if log.inicio_processamento:
                    duracao = (log.fim_processamento - log.inicio_processamento).total_seconds()
                    log.duracao_segundos = int(duracao)
                
                app_logger.info(f"Log atualizado: {batch_id} - {sucessos}/{erros}")

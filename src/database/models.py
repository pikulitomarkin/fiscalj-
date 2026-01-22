"""
Modelos ORM do banco de dados usando SQLAlchemy.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, Text, LargeBinary
from sqlalchemy.sql import func
from datetime import datetime

from config.database import Base


class NFSeEmissao(Base):
    """Registro de emissões de NFS-e."""
    
    __tablename__ = 'nfse_emissoes'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação
    hash_transacao = Column(String(64), index=True)
    chave_acesso = Column(String(100), unique=True, index=True)
    numero_nfse = Column(String(20), index=True)
    protocolo = Column(String(50), index=True)
    codigo_verificacao = Column(String(20))
    
    # Tomador
    cpf_tomador = Column(String(14), index=True)  # CPF ou CNPJ
    nome_tomador = Column(String(150))
    
    # Status
    status = Column(String(20), nullable=False, index=True)  # sucesso, erro, pendente
    mensagem = Column(Text)
    
    # Dados do serviço
    valor_servico = Column(Numeric(10, 2))
    valor_iss = Column(Numeric(10, 2))
    descricao_servico = Column(Text)
    
    # Caminhos dos arquivos
    xml_path = Column(String(500))
    pdf_path = Column(String(500))
    
    # Conteúdo dos arquivos (armazenado no banco)
    xml_content = Column(Text)  # Conteúdo XML
    pdf_content = Column(LargeBinary)  # Conteúdo PDF em binário
    
    # Resultado completo (JSON)
    resultado_json = Column(Text)  # JSON string com resultado completo
    
    # Timestamps
    data_emissao = Column(DateTime, default=datetime.utcnow)
    data_processamento = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())
    
    # Metadata
    url_nfse = Column(String(255))
    usuario = Column(String(50))
    
    def __repr__(self):
        return f"<NFSeEmissao(id={self.id}, chave={self.chave_acesso[:20] if self.chave_acesso else 'N/A'}..., status={self.status})>"
    
    def to_dict(self):
        """Converte para dicionário compatível com session_state."""
        return {
            'id': self.id,
            'chave_acesso': self.chave_acesso,
            'numero': self.numero_nfse,
            'data_emissao': self.data_emissao.strftime("%d/%m/%Y %H:%M:%S") if self.data_emissao else None,
            'tomador_nome': self.nome_tomador,
            'tomador_cpf': self.cpf_tomador,
            'valor': float(self.valor_servico) if self.valor_servico else 0,
            'iss': float(self.valor_iss) if self.valor_iss else 0,
            'xml_path': self.xml_path,
            'pdf_path': self.pdf_path,
            'xml_content': self.xml_content,
            'pdf_content': self.pdf_content,
            'status': self.status
        }


class LogProcessamento(Base):
    """Log de processamentos em lote."""
    
    __tablename__ = 'logs_processamento'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação do lote
    batch_id = Column(String(36), unique=True, index=True)  # UUID
    
    # Estatísticas
    total_registros = Column(Integer, nullable=False)
    sucessos = Column(Integer, default=0)
    erros = Column(Integer, default=0)
    
    # Arquivos processados
    nome_arquivo = Column(String(255))
    tamanho_arquivo = Column(Integer)  # bytes
    
    # Timing
    inicio_processamento = Column(DateTime, default=datetime.utcnow)
    fim_processamento = Column(DateTime)
    duracao_segundos = Column(Integer)
    
    # Usuário
    usuario = Column(String(50))
    
    # Status
    status = Column(String(20), default='processando')  # processando, concluido, erro
    
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    
    def __repr__(self):
        return f"<LogProcessamento(id={self.id}, batch={self.batch_id}, total={self.total_registros})>"


class Usuario(Base):
    """Usuários do sistema (para autenticação)."""
    
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, index=True)
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Perfil
    nome_completo = Column(String(150))
    email = Column(String(100), unique=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now())
    last_login = Column(DateTime)
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, username={self.username})>"

"""
Script de migração do banco de dados PostgreSQL
Adiciona colunas xml_content e pdf_content à tabela nfse_emissoes
"""

import asyncio
import os
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

import asyncpg
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL não está definida")
    print("   Configure a variável de ambiente DATABASE_URL")
    sys.exit(1)

# Converter DATABASE_URL de SQLAlchemy para asyncpg se necessário
if DATABASE_URL.startswith('postgresql+asyncpg://'):
    # Remover o driver asyncpg
    DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')
elif DATABASE_URL.startswith('postgresql+psycopg2://'):
    # Converter de psycopg2 para asyncpg
    DATABASE_URL = DATABASE_URL.replace('postgresql+psycopg2://', 'postgresql://')


async def run_migration():
    """Executa migração para adicionar colunas de conteúdo de arquivos."""
    
    try:
        # Conectar ao banco de dados
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Conectado ao banco de dados")
        
        # Verificar se as colunas já existem
        check_xml = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name='nfse_emissoes' 
            AND column_name='xml_content'
        """)
        
        check_pdf = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name='nfse_emissoes' 
            AND column_name='pdf_content'
        """)
        
        # Migração 1: Adicionar coluna xml_content
        if check_xml == 0:
            print("📝 Adicionando coluna xml_content...")
            await conn.execute("""
                ALTER TABLE nfse_emissoes 
                ADD COLUMN xml_content TEXT
            """)
            print("✅ Coluna xml_content adicionada com sucesso")
        else:
            print("ℹ️ Coluna xml_content já existe")
        
        # Migração 2: Adicionar coluna pdf_content
        if check_pdf == 0:
            print("📝 Adicionando coluna pdf_content...")
            await conn.execute("""
                ALTER TABLE nfse_emissoes 
                ADD COLUMN pdf_content BYTEA
            """)
            print("✅ Coluna pdf_content adicionada com sucesso")
        else:
            print("ℹ️ Coluna pdf_content já existe")
        
        # Verificar quantos registros existem
        total = await conn.fetchval("SELECT COUNT(*) FROM nfse_emissoes")
        print(f"📊 Total de registros na tabela: {total}")
        
        # Fechar conexão
        await conn.close()
        print("✅ Migração concluída com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        
        # Mensagem customizada para erro de conexão
        if "recusou" in str(e) or "Connection refused" in str(e) or "refused" in str(e).lower():
            print("\n⚠️ Banco de dados não está acessível neste momento")
            print("   Possíveis causas:")
            print("   1. Banco está em outro servidor (Railway/Cloud)")
            print("   2. DATABASE_URL está incorreta")
            print("   3. Firewall está bloqueando a conexão")
            print("\n💡 A migração será executada automaticamente no Railway!")
            return False
        
        import traceback
        traceback.print_exc()
        return False


async def populate_existing_files():
    """
    Popula as colunas xml_content e pdf_content para registros existentes
    que possuem arquivos no filesystem.
    """
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Conectado ao banco de dados para popular arquivos existentes")
        
        # Buscar registros com paths mas sem conteúdo
        registros = await conn.fetch("""
            SELECT id, xml_path, pdf_path, chave_acesso
            FROM nfse_emissoes
            WHERE (xml_path IS NOT NULL OR pdf_path IS NOT NULL)
            AND (xml_content IS NULL OR pdf_content IS NULL)
        """)
        
        print(f"📊 Encontrados {len(registros)} registros para popular")
        
        updated_xml = 0
        updated_pdf = 0
        
        for reg in registros:
            reg_id = reg['id']
            xml_path = reg['xml_path']
            pdf_path = reg['pdf_path']
            chave = reg['chave_acesso']
            
            # Tentar ler XML
            if xml_path and Path(xml_path).exists():
                try:
                    xml_content = Path(xml_path).read_text(encoding='utf-8')
                    await conn.execute("""
                        UPDATE nfse_emissoes 
                        SET xml_content = $1
                        WHERE id = $2
                    """, xml_content, reg_id)
                    updated_xml += 1
                    print(f"  ✅ XML populado para NFS-e {chave or reg_id}")
                except Exception as e:
                    print(f"  ⚠️ Erro ao ler XML {xml_path}: {e}")
            
            # Tentar ler PDF
            if pdf_path and Path(pdf_path).exists():
                try:
                    pdf_content = Path(pdf_path).read_bytes()
                    await conn.execute("""
                        UPDATE nfse_emissoes 
                        SET pdf_content = $1
                        WHERE id = $2
                    """, pdf_content, reg_id)
                    updated_pdf += 1
                    print(f"  ✅ PDF populado para NFS-e {chave or reg_id}")
                except Exception as e:
                    print(f"  ⚠️ Erro ao ler PDF {pdf_path}: {e}")
        
        await conn.close()
        print(f"✅ População concluída: {updated_xml} XMLs e {updated_pdf} PDFs")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao popular arquivos: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Função principal de migração."""
    # Verificar se está rodando no Railway (não interativo)
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT') is not None
    
    print("=" * 60)
    print("🔧 MIGRAÇÃO DO BANCO DE DADOS")
    print("   Adicionando suporte para armazenamento de arquivos")
    print("=" * 60)
    print()
    
    # Executar migração
    success = await run_migration()
    
    if not success:
        print("\n❌ Migração falhou. Verifique os logs.")
        return
    
    print("\n" + "=" * 60)
    
    # No Railway, não popular arquivos automaticamente (pode ser lento)
    if is_railway:
        print("\n⏭️ Modo Railway detectado - população de arquivos pulada")
        print("   Os novos arquivos serão salvos automaticamente nas próximas emissões")
    else:
        # Perguntar se deseja popular arquivos existentes (apenas local)
        print("\n📁 Deseja popular os arquivos XML/PDF existentes no banco?")
        print("   (Isso irá ler os arquivos do filesystem e salvá-los no banco)")
        resposta = input("\n   Digite 'sim' para popular ou pressione Enter para pular: ").strip().lower()
        
        if resposta in ['sim', 's', 'yes', 'y']:
            print("\n📦 Populando arquivos existentes...")
            await populate_existing_files()
        else:
            print("\n⏭️ População de arquivos existentes pulada")
            print("   Os novos arquivos serão salvos automaticamente nas próximas emissões")
    
    print("\n" + "=" * 60)
    print("✅ PROCESSO CONCLUÍDO")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

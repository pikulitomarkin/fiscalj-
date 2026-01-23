#!/usr/bin/env python3
"""Railway startup script - replaces bash to avoid CRLF issues."""
import os
import subprocess
import sys
import shutil
from pathlib import Path

print("🚀 Iniciando NFS-e Automation System...")
print(f"Python: {sys.version}")
print(f"Working Directory: {os.getcwd()}")
print(f"Build: v2.6 - Inline cache clear")  # Versão para forçar rebuild

# Get PORT from environment
port = os.environ.get("PORT", "8501")
print(f"PORT={port}")

# LIMPAR CACHE PYTHON INLINE
print("🧹 Limpando cache Python...")
print("="*60)
removed_count = 0
base_dir = Path.cwd()

# Remover arquivos .pyc
for pyc_file in base_dir.rglob("*.pyc"):
    try:
        pyc_file.unlink()
        removed_count += 1
        print(f"  🗑️ {pyc_file.relative_to(base_dir)}")
    except Exception as e:
        print(f"  ⚠️ Erro: {e}")

# Remover diretórios __pycache__
for pycache_dir in base_dir.rglob("__pycache__"):
    try:
        shutil.rmtree(pycache_dir)
        removed_count += 1
        print(f"  🗑️ {pycache_dir.relative_to(base_dir)}/")
    except Exception as e:
        print(f"  ⚠️ Erro: {e}")

print(f"✅ Cache limpo! {removed_count} itens removidos")
print("="*60)
print()

# Run database migration (adicionar colunas xml_content e pdf_content)
print("🔧 Executando migração do banco de dados...")
print("="*60)
try:
    result = subprocess.run([sys.executable, "migrate_database.py"], timeout=60, input=b'\n')
    print("="*60)
    if result.returncode == 0:
        print(f"✅ Migração do banco concluída com sucesso")
    else:
        print(f"⚠️ Migração retornou código {result.returncode}")
        print("   Continuando mesmo assim...")
except Exception as e:
    print("="*60)
    print(f"⚠️ Erro na migração do banco: {e}")
    print("   Continuando sem migração...")
print()

# Run certificate initialization (não bloqueia se falhar)
print("📜 Inicializando certificados...")
print("="*60)
try:
    result = subprocess.run([sys.executable, "railway_init.py"], timeout=30)
    print("="*60)
    print(f"✅ Inicialização de certificados concluída (exit code: {result.returncode})")
except Exception as e:
    print("="*60)
    print(f"⚠️ Erro na inicialização de certificados: {e}")
    print("   Continuando sem certificados...")
print()

# Start Streamlit
print(f"🌐 Iniciando Streamlit na porta {port}...")
print("="*60)

try:
    os.execvp(
        sys.executable,
        [
            sys.executable, "-m", "streamlit", "run",
            "app_nfse_enhanced.py",
            "--server.port", port,
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]
    )
except Exception as e:
    print(f"❌ Erro ao iniciar Streamlit: {e}")
    sys.exit(1)

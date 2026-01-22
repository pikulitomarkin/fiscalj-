#!/usr/bin/env python3
"""Railway startup script - replaces bash to avoid CRLF issues."""
import os
import subprocess
import sys

print("🚀 Iniciando NFS-e Automation System...")
print(f"Python: {sys.version}")
print(f"Working Directory: {os.getcwd()}")
print(f"Build: v2.4 - Tubarão/SC CNPJ 58645846000169 IM 93442")  # Versão para forçar rebuild

# Get PORT from environment
port = os.environ.get("PORT", "8501")
print(f"PORT={port}")

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

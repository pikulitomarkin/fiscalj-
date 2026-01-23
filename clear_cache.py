"""
Script para limpar cache Python antes de iniciar a aplicação.
"""
import os
import sys
import shutil
from pathlib import Path

def clear_python_cache():
    """Remove todos os arquivos .pyc e diretórios __pycache__."""
    base_dir = Path(__file__).parent
    removed_count = 0
    
    print("=" * 60)
    print("🧹 LIMPANDO CACHE PYTHON")
    print("=" * 60)
    
    # Remover arquivos .pyc
    for pyc_file in base_dir.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            removed_count += 1
            print(f"  🗑️ Removido: {pyc_file.relative_to(base_dir)}")
        except Exception as e:
            print(f"  ⚠️ Erro ao remover {pyc_file}: {e}")
    
    # Remover diretórios __pycache__
    for pycache_dir in base_dir.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
            removed_count += 1
            print(f"  🗑️ Removido: {pycache_dir.relative_to(base_dir)}")
        except Exception as e:
            print(f"  ⚠️ Erro ao remover {pycache_dir}: {e}")
    
    print(f"✅ Cache limpo! {removed_count} itens removidos")
    print("=" * 60)

if __name__ == "__main__":
    clear_python_cache()

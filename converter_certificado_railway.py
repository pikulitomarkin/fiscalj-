"""
Script para converter certificado .pfx para Base64 (Railway)
VSB Serviços Médicos LTDA
"""
import base64
from pathlib import Path

def converter_pfx_para_base64():
    """Converte certificado .pfx para Base64 para uso no Railway"""
    
    print("\n" + "="*60)
    print("  Conversão de Certificado para Railway (Base64)")
    print("="*60 + "\n")
    
    # Caminho do certificado
    pfx_path = r"c:\Users\marco\Downloads\VSBSERVICOSMEDICOSLTDA_58645846000169.pfx"
    output_path = "certificado_base64.txt"
    
    # Verificar se o certificado existe
    if not Path(pfx_path).exists():
        print(f" Certificado não encontrado em: {pfx_path}")
        return False
    
    try:
        print(f" Lendo certificado: {pfx_path}")
        
        # Ler arquivo .pfx
        with open(pfx_path, 'rb') as f:
            pfx_bytes = f.read()
        
        print(f" Tamanho do arquivo: {len(pfx_bytes)} bytes")
        
        # Converter para Base64
        print(" Convertendo para Base64...")
        base64_content = base64.b64encode(pfx_bytes).decode('utf-8')
        
        # Salvar em arquivo
        with open(output_path, 'w') as f:
            f.write(base64_content)
        
        print(f" Arquivo Base64 salvo: {output_path}")
        print(f" Tamanho Base64: {len(base64_content)} caracteres")
        
        # Mostrar preview
        preview_length = 80
        print(f"\n Preview (primeiros {preview_length} caracteres):")
        print("-" * 60)
        print(base64_content[:preview_length] + "...")
        print("-" * 60)
        
        print("\n" + "="*60)
        print("   Conversão concluída com sucesso!")
        print("="*60 + "\n")
        
        print(" Próximos passos:")
        print("  1. Abra o arquivo: certificado_base64.txt")
        print("  2. Copie TODO o conteúdo")
        print("  3. No Railway, adicione variável de ambiente:")
        print("     Nome: CERTIFICATE_PFX_BASE64")
        print("     Valor: <cole o conteúdo copiado>")
        print("  4. Adicione também:")
        print("     Nome: CERTIFICATE_PASSWORD")
        print("     Valor: KLP4klp4")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n Erro ao converter certificado: {e}")
        return False

if __name__ == "__main__":
    import sys
    sucesso = converter_pfx_para_base64()
    sys.exit(0 if sucesso else 1)

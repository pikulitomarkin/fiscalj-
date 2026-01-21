# ⚙️ Railway - Variáveis de Ambiente

## 📋 Lista Completa de Variáveis

### 🔐 OBRIGATÓRIAS (Para Emissão de NFS-e)

```bash
# Certificado Digital (Base64)
CERTIFICATE_CERT_PEM=<conteudo_base64_do_cert.pem>
CERTIFICATE_KEY_PEM=<conteudo_base64_do_key.pem>
```

---

### 🌐 AUTOMÁTICAS (Railway Define)

```bash
# Porta do servidor (Railway define automaticamente)
PORT=8080  # Exemplo, pode ser qualquer porta

# URL do banco de dados PostgreSQL (se adicionar PostgreSQL)
DATABASE_URL=postgresql://user:pass@host:port/db
```

---

### ⚙️ OPCIONAIS (Configurações Avançadas)

```bash
# Ambiente da API NFS-e
NFSE_API_AMBIENTE=PRODUCAO  # ou HOMOLOGACAO

# URLs das APIs (padrão já configurado)
NFSE_API_BASE_URL=https://sefin.nfse.gov.br
ADN_API_BASE_URL=https://adn.nfse.gov.br

# Debug
DEBUG=false

# Configurações de segurança
SECRET_KEY=seu-secret-key-super-secreto-aqui

# Configurações de processamento
MAX_BATCH_SIZE=600
CONCURRENT_REQUESTS=10
```

---

## 🔧 Como Configurar no Railway

### Via Dashboard:

1. Acesse seu projeto no Railway
2. Clique na aba **"Variables"**
3. Clique em **"+ New Variable"**
4. Adicione cada variável:
   - **Key**: Nome da variável (ex: `CERTIFICATE_CERT_PEM`)
   - **Value**: Valor da variável (ex: Base64 do certificado)
5. Clique em **"Add"**
6. Repita para todas as variáveis

### Via Railway CLI:

```bash
# Instalar Railway CLI (se não tiver)
npm install -g @railway/cli

# Login
railway login

# Linkar ao projeto
railway link

# Adicionar variáveis
railway variables set CERTIFICATE_CERT_PEM="<base64>"
railway variables set CERTIFICATE_KEY_PEM="<base64>"
railway variables set NFSE_API_AMBIENTE="PRODUCAO"
```

---

## 📝 Como Gerar os Certificados em Base64

### Windows (PowerShell):

```powershell
# Navegue até a pasta do projeto
cd c:\VSB_NFSE

# Gerar Base64 do cert.pem
[Convert]::ToBase64String([IO.File]::ReadAllBytes("certificados\cert.pem")) | Out-File -Encoding ASCII cert_b64.txt

# Gerar Base64 do key.pem
[Convert]::ToBase64String([IO.File]::ReadAllBytes("certificados\key.pem")) | Out-File -Encoding ASCII key_b64.txt

# Abrir arquivos para copiar
notepad cert_b64.txt
notepad key_b64.txt
```

### Linux/Mac:

```bash
# Navegue até a pasta do projeto
cd /caminho/para/VSB_NFSE

# Gerar Base64 do cert.pem (sem quebras de linha)
base64 -w 0 certificados/cert.pem > cert_b64.txt

# Gerar Base64 do key.pem (sem quebras de linha)
base64 -w 0 certificados/key.pem > key_b64.txt

# Ver conteúdo para copiar
cat cert_b64.txt
cat key_b64.txt
```

### Usando Python (Qualquer OS):

```python
import base64
from pathlib import Path

# Ler e converter cert.pem
cert_content = Path("certificados/cert.pem").read_bytes()
cert_b64 = base64.b64encode(cert_content).decode('ascii')
Path("cert_b64.txt").write_text(cert_b64)
print(f"✅ cert.pem convertido: {len(cert_b64)} caracteres")

# Ler e converter key.pem
key_content = Path("certificados/key.pem").read_bytes()
key_b64 = base64.b64encode(key_content).decode('ascii')
Path("key_b64.txt").write_text(key_b64)
print(f"✅ key.pem convertido: {len(key_b64)} caracteres")
```

---

## ✅ Validação dos Certificados

### Verificar se o Base64 está correto:

```python
import base64

# Cole o Base64 aqui
cert_b64 = "SEU_BASE64_AQUI"

# Decodificar
try:
    cert_content = base64.b64decode(cert_b64)
    
    # Verificar se começa com -----BEGIN
    if cert_content.startswith(b'-----BEGIN'):
        print("✅ Base64 válido!")
        print(f"Tamanho: {len(cert_content)} bytes")
        print(f"Primeiros 50 chars: {cert_content[:50]}")
    else:
        print("❌ Base64 decodificado mas não é um certificado PEM")
except Exception as e:
    print(f"❌ Erro ao decodificar: {e}")
```

---

## 🎯 Template de Variáveis

Copie e preencha:

```bash
# ====================================
# 🔐 CERTIFICADOS (OBRIGATÓRIO)
# ====================================
CERTIFICATE_CERT_PEM=MIIEpAIBAAKCAQEA...
CERTIFICATE_KEY_PEM=MIIJKAIBAAKCAgEA...

# ====================================
# 🌐 AMBIENTE API (OPCIONAL)
# ====================================
NFSE_API_AMBIENTE=PRODUCAO

# ====================================
# 🔒 SEGURANÇA (RECOMENDADO)
# ====================================
SECRET_KEY=sua-chave-secreta-muito-longa-e-aleatoria-aqui

# ====================================
# 🐛 DEBUG (OPCIONAL)
# ====================================
DEBUG=false
```

---

## 🧪 Testar Localmente com Variáveis

### Windows (PowerShell):

```powershell
# Definir variáveis temporariamente
$env:CERTIFICATE_CERT_PEM = (Get-Content cert_b64.txt -Raw)
$env:CERTIFICATE_KEY_PEM = (Get-Content key_b64.txt -Raw)
$env:PORT = "8501"

# Testar railway_init.py
python railway_init.py

# Testar railway_start.py
python railway_start.py
```

### Linux/Mac:

```bash
# Definir variáveis temporariamente
export CERTIFICATE_CERT_PEM=$(cat cert_b64.txt)
export CERTIFICATE_KEY_PEM=$(cat key_b64.txt)
export PORT=8501

# Testar railway_init.py
python railway_init.py

# Testar railway_start.py
python railway_start.py
```

---

## ⚠️ Segurança

### ❌ NÃO FAÇA:

- ❌ Não commite certificados no Git
- ❌ Não compartilhe os Base64 publicamente
- ❌ Não exponha as variáveis de ambiente em logs
- ❌ Não use certificados de teste em produção

### ✅ FAÇA:

- ✅ Guarde os certificados em local seguro
- ✅ Use `.gitignore` para excluir certificados
- ✅ Configure as variáveis apenas no Railway
- ✅ Use certificados válidos e não expirados
- ✅ Faça backup dos certificados

---

## 📊 Checklist de Configuração

Antes de fazer deploy, confirme:

- [ ] Certificado cert.pem convertido para Base64
- [ ] Certificado key.pem convertido para Base64
- [ ] Base64 testado e validado
- [ ] Variável `CERTIFICATE_CERT_PEM` configurada no Railway
- [ ] Variável `CERTIFICATE_KEY_PEM` configurada no Railway
- [ ] Ambiente (`PRODUCAO` ou `HOMOLOGACAO`) definido
- [ ] Outras variáveis opcionais configuradas (se necessário)

---

## 🆘 Problemas Comuns

### Erro: "Certificados não configurados"

**Causa**: Variáveis de ambiente não definidas ou incorretas

**Solução**:
1. Verifique se as variáveis estão no Railway
2. Confirme que os nomes estão corretos (case-sensitive)
3. Recarregue o deploy

### Erro: "Invalid PEM data"

**Causa**: Base64 incorreto ou corrompido

**Solução**:
1. Regere o Base64 usando os comandos acima
2. Confirme que não há espaços ou quebras de linha
3. Use `-w 0` no Linux para evitar quebras

### Erro: "Certificate expired"

**Causa**: Certificado digital expirado

**Solução**:
1. Renove o certificado digital
2. Gere novos arquivos Base64
3. Atualize as variáveis no Railway

---

**✅ Configuração completa!**

Com as variáveis configuradas corretamente, o sistema estará pronto para emitir NFS-e no Railway.

# 🚀 Railway Deploy - Correções Aplicadas

## ❌ Problemas Identificados

### 1. **Conflito de Builder**
- **Problema**: `railway.json` estava configurado para usar DOCKERFILE, mas também existia `nixpacks.toml` e `Procfile`
- **Impacto**: Railway não sabia qual builder usar
- **Solução**: Alterado para usar NIXPACKS (mais simples e eficiente)

### 2. **Inicialização de Certificados Travando**
- **Problema**: `railway_start.py` executava `railway_init.py` sem timeout ou tratamento de erro
- **Impacto**: Se a inicialização de certificados falhasse, o app não iniciava
- **Solução**: Adicionado timeout de 30s e tratamento de exceção (continua sem certificados se falhar)

### 3. **Falta de Healthcheck**
- **Problema**: Railway não tinha forma de verificar se o app estava rodando
- **Impacto**: Deploy podia parecer OK mas app não estar respondendo
- **Solução**: Adicionado `healthcheckPath: "/"` no railway.json

## ✅ Correções Aplicadas

### Arquivo: `railway.json`
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"  // ← Mudado de DOCKERFILE para NIXPACKS
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 5,
    "healthcheckPath": "/",  // ← NOVO: Healthcheck
    "healthcheckTimeout": 100
  }
}
```

### Arquivo: `nixpacks.toml`
```toml
[start]
cmd = 'python railway_start.py'  // ← Usa Python script ao invés de bash
```

### Arquivo: `railway_start.py`
- ✅ Adicionado timeout de 30s para inicialização de certificados
- ✅ Adicionado tratamento de exceção (não bloqueia se certificados falharem)
- ✅ Adicionado logs mais detalhados para debugging
- ✅ Melhor tratamento de erro na execução do Streamlit

## 📋 Variáveis de Ambiente Necessárias no Railway

Configure estas variáveis no painel do Railway:

### Obrigatórias (para emissão de NFS-e):
```bash
CERTIFICATE_CERT_PEM=<base64_do_cert.pem>
CERTIFICATE_KEY_PEM=<base64_do_key.pem>
```

### Opcionais:
```bash
PORT=<definida_automaticamente_pelo_railway>
DATABASE_URL=<postgresql://...>  # Se usar PostgreSQL
NFSE_API_AMBIENTE=PRODUCAO  # ou HOMOLOGACAO
DEBUG=false
```

## 🔧 Como Gerar os Certificados Base64

1. Converta seus certificados para Base64:
```bash
# No Linux/Mac:
base64 -w 0 certificados/cert.pem > cert_b64.txt
base64 -w 0 certificados/key.pem > key_b64.txt

# No Windows (PowerShell):
[Convert]::ToBase64String([IO.File]::ReadAllBytes("certificados\cert.pem")) | Out-File -Encoding ASCII cert_b64.txt
[Convert]::ToBase64String([IO.File]::ReadAllBytes("certificados\key.pem")) | Out-File -Encoding ASCII key_b64.txt
```

2. Copie o conteúdo dos arquivos `cert_b64.txt` e `key_b64.txt`

3. Cole nas variáveis de ambiente do Railway:
   - `CERTIFICATE_CERT_PEM` = conteúdo de cert_b64.txt
   - `CERTIFICATE_KEY_PEM` = conteúdo de key_b64.txt

## 🚀 Deploy no Railway

### Opção 1: Via GitHub (Recomendado)
1. Faça commit das alterações:
   ```bash
   git add .
   git commit -m "fix: corrigir configuração Railway"
   git push
   ```

2. O Railway fará deploy automaticamente

### Opção 2: Via Railway CLI
```bash
railway up
```

## 🔍 Verificando Logs

No Railway Dashboard:
1. Acesse seu projeto
2. Clique em "Deployments"
3. Clique no deployment ativo
4. Veja os logs em tempo real

### Logs Esperados:
```
🚀 Iniciando NFS-e Automation System...
Python: 3.11.x
Working Directory: /app
PORT=xxxx
📜 Inicializando certificados...
============================================================
🚀 NFS-e Automation System - Inicialização Railway
============================================================
✅ Certificado válido: CN=...
✅ Certificate Manager carregado com sucesso
============================================================
✅ Inicialização de certificados concluída
🌐 Iniciando Streamlit na porta xxxx...
============================================================
```

## ⚠️ Troubleshooting

### App não inicia
- **Verifique** se as variáveis de ambiente estão configuradas
- **Verifique** os logs de build no Railway
- **Confirme** que `requirements.txt` tem todas as dependências

### Certificados não carregam
- **Verifique** se as variáveis `CERTIFICATE_CERT_PEM` e `CERTIFICATE_KEY_PEM` estão corretas
- **Teste** decodificar localmente:
  ```python
  import base64
  cert = base64.b64decode("sua_string_base64")
  print(cert[:50])  # Deve começar com -----BEGIN CERTIFICATE-----
  ```

### Streamlit não responde
- **Verifique** se a porta está correta (Railway define automaticamente)
- **Confirme** que o healthcheck está passando
- **Teste** acessar via URL pública fornecida pelo Railway

## 📊 Status do Sistema

Após o deploy, acesse a URL fornecida pelo Railway. Você deverá ver:
- ✅ Página de login
- ✅ Dashboard operacional
- ✅ Sistema de emissão funcionando

## 🎯 Próximos Passos

1. Configurar variáveis de ambiente de certificados
2. Fazer deploy
3. Testar emissão de NFS-e
4. Configurar domínio personalizado (opcional)
5. Configurar PostgreSQL para persistência (opcional)

---

**Última atualização**: Janeiro 2026
**Versão**: 2.0

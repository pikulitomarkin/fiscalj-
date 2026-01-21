#  Deploy no Railway - VSB Serviços Médicos LTDA

##  Guia Completo de Deploy

Este guia explica como fazer deploy do sistema NFS-e da VSB no Railway.

---

##  Pré-requisitos

1.  Conta no Railway (https://railway.app)
2.  Repositório no GitHub (https://github.com/pikulitomarkin/fiscalj-.git)
3.  Certificado Digital convertido (.pem)
4.  Dados da VSB configurados

---

##  Passo 1: Preparar Variáveis de Ambiente

O Railway precisa das seguintes variáveis de ambiente:

### Variáveis Obrigatórias

```env
# Ambiente
NFSE_API_AMBIENTE=PRODUCAO
NFSE_API_BASE_URL=https://nfse.producao.sefin.nfse.gov.br
NFSE_API_TIMEOUT=120

# Certificado Digital (Base64)
CERTIFICATE_PFX_BASE64=<conteúdo_do_certificado_em_base64>
CERTIFICATE_PASSWORD=KLP4klp4

# Dados VSB
PRESTADOR_CNPJ=58645846000169
PRESTADOR_INSCRICAO_MUNICIPAL=93442
PRESTADOR_RAZAO_SOCIAL=VSB SERVICOS MEDICOS LTDA
PRESTADOR_NOME_FANTASIA=VS BOEGER
PRESTADOR_LOGRADOURO=R Luiz Martins Collaco
PRESTADOR_NUMERO=1175
PRESTADOR_BAIRRO=Centro
PRESTADOR_MUNICIPIO=Tubarao
PRESTADOR_UF=SC
PRESTADOR_CEP=88701330
PRESTADOR_CODIGO_MUNICIPIO=4218707
PRESTADOR_EMAIL=vinisilv@hotmail.com
PRESTADOR_TELEFONE=48991501444

# Serviço
SERVICO_CODIGO_TRIBUTACAO=040191
SERVICO_NBS=123019900
SERVICO_DESCRICAO=Servicos medicos
SERVICO_ALIQUOTA_ISSQN=3.00
SERVICO_MUNICIPIO_INCIDENCIA=4218707

# Database (Railway PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Autenticação
AUTH_SECRET_KEY=vsb_railway_secret_key_2026_prod
AUTH_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_EXPIRE_HOURS=8
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Processamento
MAX_BATCH_SIZE=50
MAX_CONCURRENT_REQUESTS=10
RETRY_MAX_ATTEMPTS=3
RETRY_BACKOFF_FACTOR=2

# Logs
LOG_LEVEL=INFO
```

---

##  Passo 2: Converter Certificado para Base64

Execute no PowerShell:

```powershell
# Converter .pfx para Base64
$pfxPath = "c:\Users\marco\Downloads\VSBSERVICOSMEDICOSLTDA_58645846000169.pfx"
$bytes = [System.IO.File]::ReadAllBytes($pfxPath)
$base64 = [System.Convert]::ToBase64String($bytes)
$base64 | Set-Content "certificado_base64.txt"
Write-Host "Certificado convertido! Copie o conteúdo de certificado_base64.txt"
```

---

##  Passo 3: Deploy no Railway

### 3.1 Criar Novo Projeto

1. Acesse https://railway.app/dashboard
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Escolha: **pikulitomarkin/fiscalj-**

### 3.2 Adicionar PostgreSQL

1. No projeto, clique em **"+ New"**
2. Selecione **"Database"**  **"PostgreSQL"**
3. Railway criará automaticamente a variável `DATABASE_URL`

### 3.3 Configurar Variáveis de Ambiente

1. Clique no serviço principal
2. Vá em **"Variables"**
3. Adicione todas as variáveis listadas acima
4. Cole o certificado Base64 em `CERTIFICATE_PFX_BASE64`

### 3.4 Deploy

1. Railway fará deploy automaticamente
2. Aguarde a build terminar (~3-5 minutos)
3. Acesse o domínio gerado: `https://seu-projeto.railway.app`

---

##  Passo 4: Configurar Domínio Customizado (Opcional)

1. No serviço, clique em **"Settings"**
2. Role até **"Domains"**
3. Clique em **"Generate Domain"** ou adicione domínio próprio
4. Exemplo: `vsb-nfse.railway.app`

---

##  Passo 5: Verificar Deploy

### Checklist de Verificação

- [ ] Build concluída com sucesso
- [ ] PostgreSQL conectado
- [ ] Aplicação acessível via URL
- [ ] Login funcionando (admin/admin123)
- [ ] Certificado validado no sistema
- [ ] Dados da VSB aparecendo corretamente

### Testes Básicos

1. **Acesse a URL do Railway**
2. **Faça login** com admin/admin123
3. **Verifique certificado** no menu lateral
4. **Teste emissão** de uma NFS-e
5. **Baixe XML e PDF** gerados

---

##  Troubleshooting

### Problema: Certificado Inválido

**Solução:**
1. Verifique se `CERTIFICATE_PFX_BASE64` está correto
2. Verifique se `CERTIFICATE_PASSWORD` está correta
3. Reconverta o certificado:
```powershell
python converter_certificado.py
```

### Problema: Erro de Conexão com API

**Solução:**
1. Verifique `NFSE_API_BASE_URL`
2. Produção: `https://nfse.producao.sefin.nfse.gov.br`
3. Homologação: `https://nfse.homologacao.sefin.nfse.gov.br`

### Problema: Erro de Database

**Solução:**
1. Verifique se PostgreSQL está rodando
2. Verifique `DATABASE_URL` nas variáveis
3. Formato: `postgresql+asyncpg://user:pass@host:port/db`

### Problema: Build Falhou

**Solução:**
1. Verifique logs no Railway
2. Verifique se `requirements.txt` está correto
3. Verifique se todos os arquivos foram enviados ao Git

---

##  Monitoramento

### Logs em Tempo Real

No Railway:
1. Clique no serviço
2. Vá em **"Deployments"**
3. Clique no deploy ativo
4. Veja logs em tempo real

### Métricas

Railway mostra automaticamente:
- CPU usage
- Memory usage
- Network traffic
- Response times

---

##  Atualizações

### Deploy Automático

Railway monitora o repositório GitHub. Para atualizar:

```bash
cd c:\VSB_NFSE
git add .
git commit -m "Descrição da atualização"
git push origin main
```

Railway fará deploy automaticamente!

### Deploy Manual

1. No Railway, vá em **"Deployments"**
2. Clique em **"Redeploy"**

---

##  Custos Estimados

Railway oferece:
- **Starter Plan:** $5/mês + uso
- **PostgreSQL:** Incluído
- **500 horas grátis** para novos usuários

Estimativa para VSB:
- Uso leve: ~$10-15/mês
- Uso moderado: ~$20-30/mês
- Uso intenso: ~$40-50/mês

---

##  Segurança

### Boas Práticas

1.  **Nunca** exponha o certificado
2.  **Troque** a senha admin padrão
3.  Use `AUTH_SECRET_KEY` forte em produção
4.  Mantenha `CERTIFICATE_PASSWORD` segura
5.  Ative logs apenas em desenvolvimento

### Variáveis Sensíveis

Estas variáveis NUNCA devem ser compartilhadas:
- `CERTIFICATE_PFX_BASE64`
- `CERTIFICATE_PASSWORD`
- `AUTH_SECRET_KEY`
- `DATABASE_URL`
- `ADMIN_PASSWORD`

---

##  Suporte

### Documentação

- Railway: https://docs.railway.app
- Projeto: Ver `README_VSB.md`

### Contato

- Email: vinisilv@hotmail.com
- GitHub: https://github.com/pikulitomarkin/fiscalj-

---

##  Checklist Final de Deploy

- [ ] Repositório no GitHub atualizado
- [ ] Certificado convertido para Base64
- [ ] Projeto criado no Railway
- [ ] PostgreSQL adicionado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy concluído com sucesso
- [ ] URL funcionando
- [ ] Login testado
- [ ] NFS-e teste emitida
- [ ] Senha admin alterada
- [ ] Domínio customizado configurado (opcional)

---

**Deploy concluído! Sistema VSB rodando no Railway! **

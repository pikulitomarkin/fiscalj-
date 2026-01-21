# 🏥 Sistema de Automação NFS-e - VSB Serviços Médicos LTDA

> Sistema customizado para emissão automatizada de NFS-e Nacional

## 📋 Informações da Empresa

- **Razão Social:** VSB SERVIÇOS MÉDICOS LTDA
- **Nome Fantasia:** VS BOEGER
- **CNPJ:** 58.645.846/0001-69
- **Inscrição Municipal:** 93442
- **Município:** Tubarão/SC (Código: 4218707)

### 📍 Endereço
- **Logradouro:** R Luiz Martins Collaco, 1175
- **Bairro:** Centro
- **CEP:** 88.701-330
- **Cidade/UF:** Tubarão/SC

### 📞 Contato
- **Email:** vinisilv@hotmail.com
- **Telefone:** (48) 9150-1444

## ⚙️ Configurações de Serviço

### Tributação
- **Código de Tributação Nacional:** 04.01.91 - Medicina
- **NBS:** 123019900 - Outros serviços de saúde humana não classificados
- **Alíquota ISSQN:** 3,00%
- **Regime Tributário:** Operação Tributável
- **Município de Incidência:** Tubarão/SC

## 🔐 Certificado Digital

- **Arquivo:** `VSBSERVICOSMEDICOSLTDA_58645846000169.pfx`
- **Localização:** `c:\Users\marco\Downloads\`
- **Tipo:** A1 (arquivo)

### Conversão do Certificado

Antes de usar o sistema, converta o certificado .pfx para .pem:

```powershell
# Extrair certificado
openssl pkcs12 -in c:\Users\marco\Downloads\VSBSERVICOSMEDICOSLTDA_58645846000169.pfx -clcerts -nokeys -out c:\Users\marco\Downloads\vsbcert.pem

# Extrair chave privada
openssl pkcs12 -in c:\Users\marco\Downloads\VSBSERVICOSMEDICOSLTDA_58645846000169.pfx -nocerts -nodes -out c:\Users\marco\Downloads\vsbkey.pem
```

## 🚀 Como Usar

### 1. Configuração Inicial

```powershell
# 1. Navegue até o diretório
cd c:\VSB_NFSE

# 2. Crie ambiente virtual
python -m venv venv

# 3. Ative o ambiente
.\venv\Scripts\activate

# 4. Instale dependências
pip install -r requirements.txt

# 5. Configure o arquivo .env
# Edite o arquivo .env e adicione a senha do certificado em CERTIFICATE_PASSWORD
```

### 2. Converter Certificado

Execute o script PowerShell para converter o certificado:

```powershell
.\setup.ps1
```

### 3. Iniciar Sistema

```powershell
streamlit run app_nfse_enhanced.py
```

### 4. Acessar Dashboard

Abra o navegador em: `http://localhost:8501`

**Credenciais padrão:**
- Usuário: `admin`
- Senha: `admin123`

## 📊 Funcionalidades

### ✅ Emissão de NFS-e
- Emissão individual com formulário completo
- Emissão em lote via PDF
- Download automático de XML e PDF (DANFSE)
- Validação de dados em tempo real

### ✅ Gestão de Notas
- Listagem de NFS-e emitidas
- Consulta por data, tomador ou valor
- Visualização de XML completo
- Reemissão de PDF

### ✅ Relatórios
- Métricas de emissão
- Valor total faturado
- Taxa de sucesso
- Logs detalhados

## 🔧 Configurações Importantes

### Ambiente de Produção

O sistema está configurado para **PRODUÇÃO**. Para usar em **HOMOLOGAÇÃO**:

1. Edite o arquivo `.env`
2. Altere: `NFSE_API_AMBIENTE=HOMOLOGACAO`
3. Altere: `NFSE_API_BASE_URL=https://nfse.homologacao.sefin.nfse.gov.br`

### Banco de Dados

O sistema usa PostgreSQL. Para configurar:

```sql
-- Criar banco de dados
CREATE DATABASE vsb_nfse;

-- Criar usuário (opcional)
CREATE USER vsb_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE vsb_nfse TO vsb_user;
```

Atualize a conexão no `.env`:
```env
DATABASE_URL=postgresql+asyncpg://vsb_user:sua_senha@localhost:5432/vsb_nfse
```

## 📝 Exemplos de Uso

### Emissão Individual

1. Acesse o dashboard
2. Clique em "📤 Emitir NFS-e"
3. Preencha os dados do tomador
4. Informe o valor do serviço
5. Clique em "Emitir NFS-e"
6. Baixe XML e PDF gerados

### Emissão em Lote

1. Prepare um PDF com os dados dos tomadores
2. Acesse "📤 Emissão em Lote"
3. Faça upload do PDF
4. Revise os dados extraídos
5. Configure o valor padrão
6. Clique em "Processar Lote"

## 🛠️ Manutenção

### Logs

Os logs do sistema ficam em:
- `logs/vsb_nfse.log` - Log principal
- Rotação automática a cada 100 MB
- Retenção de 30 dias

### Backup

Recomenda-se backup regular de:
- Banco de dados PostgreSQL
- Arquivos XML e PDF gerados
- Certificado digital (.pfx)

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs em `logs/vsb_nfse.log`
2. Consulte a documentação técnica em `docs/`
3. Entre em contato com o suporte técnico

## 🔒 Segurança

- ⚠️ **NUNCA** compartilhe o certificado digital
- ⚠️ **NUNCA** comite o arquivo `.env` no Git
- ⚠️ Troque as senhas padrão em produção
- ⚠️ Use HTTPS em produção
- ⚠️ Mantenha o sistema atualizado

## 📄 Licença

Sistema proprietário customizado para VSB Serviços Médicos LTDA.

---

**Versão:** 2.0.0 - VSB Custom
**Data:** Janeiro 2026
**Status:** ✅ Operacional

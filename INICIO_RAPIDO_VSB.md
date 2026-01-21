# 🚀 Guia Rápido - VSB Serviços Médicos

## ✅ Certificado Convertido com Sucesso!

Os arquivos foram gerados em:
- 📄 **Certificado:** `c:\Users\marco\Downloads\vsbcert.pem`
- 🔑 **Chave privada:** `c:\Users\marco\Downloads\vsbkey.pem`

---

## 📋 Próximos Passos

### 1️⃣ Instalar Dependências

```powershell
cd c:\VSB_NFSE
python -m pip install -r requirements.txt
```

### 2️⃣ Iniciar o Sistema

```powershell
python -m streamlit run app_nfse_enhanced.py
```

### 3️⃣ Acessar Dashboard

Abra o navegador em: **http://localhost:8501**

**Login:**
- Usuário: `admin`
- Senha: `admin123`

---

## 🏥 Configurações da VSB

### ✅ Dados já Configurados:

- **Empresa:** VSB SERVIÇOS MÉDICOS LTDA
- **CNPJ:** 58.645.846/0001-69
- **Inscrição Municipal:** 93442
- **Município:** Tubarão/SC
- **Certificado:** ✅ Convertido e configurado
- **Ambiente:** Produção

### 📊 Serviço Padrão:

- **Código:** 04.01.91 - Medicina
- **NBS:** 123019900
- **Alíquota ISSQN:** 3,00%
- **Regime:** Operação Tributável

---

## 🎯 Como Emitir NFS-e

### Emissão Individual

1. Clique em **"📤 Emitir NFS-e"**
2. Preencha dados do **Tomador** (CPF/CNPJ, Nome)
3. Informe o **Valor** do serviço
4. Adicione **Descrição** (opcional)
5. Clique em **"Emitir NFS-e"**
6. **Baixe XML e PDF** gerados

### Emissão em Lote

1. Prepare um **PDF** com lista de tomadores
2. Vá em **"📤 Emissão em Lote"**
3. Faça **upload** do PDF
4. Revise os dados extraídos
5. Configure valor padrão
6. Clique em **"Processar Lote"**

---

## 📁 Estrutura de Arquivos

```
c:\VSB_NFSE\
├── .env                    # ✅ Configurações (já configurado)
├── README_VSB.md           # Documentação completa
├── converter_certificado.py # Script de conversão (já executado)
├── app_nfse_enhanced.py    # Dashboard principal
├── requirements.txt        # Dependências Python
├── config/                 # Configurações do sistema
├── src/                    # Código-fonte
└── docs/                   # Documentação técnica
```

---

## ⚠️ Importante

### Segurança

- ✅ Certificado convertido com sucesso
- ✅ Senha configurada no .env
- ⚠️ Nunca compartilhe o certificado ou chave privada
- ⚠️ Não commite o arquivo .env no Git

### Produção

O sistema está configurado para **PRODUÇÃO**. As NFS-e emitidas são **REAIS** e têm validade fiscal.

Para testar em **HOMOLOGAÇÃO**, edite `.env`:
```env
NFSE_API_AMBIENTE=HOMOLOGACAO
```

---

## 🆘 Resolução de Problemas

### Erro de Certificado

Se aparecer erro de certificado:
```powershell
python converter_certificado.py
```

### Erro de Banco de Dados

O sistema usa PostgreSQL. Se não tiver instalado:
```powershell
# Instale PostgreSQL ou use SQLite temporariamente
# Edite .env e altere DATABASE_URL
```

### Porta 8501 em Uso

Se a porta estiver ocupada:
```powershell
python -m streamlit run app_nfse_enhanced.py --server.port 8502
```

---

## 📞 Suporte

- **Logs:** `logs/vsb_nfse.log`
- **Documentação:** `README_VSB.md`
- **Email:** vinisilv@hotmail.com

---

## ✅ Checklist Final

- [x] Projeto criado em `c:\VSB_NFSE`
- [x] Certificado convertido
- [x] Configurações da VSB aplicadas
- [x] Arquivo .env configurado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Sistema iniciado (`streamlit run app_nfse_enhanced.py`)
- [ ] Primeira NFS-e emitida!

---

**Tudo pronto! Execute os comandos acima e comece a emitir NFS-e! 🚀**

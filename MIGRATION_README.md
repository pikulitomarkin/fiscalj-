# 🔧 Migração Automática do Banco de Dados

## 📋 O que faz?

O script `migrate_database.py` adiciona automaticamente as colunas necessárias para armazenamento de arquivos XML/PDF no banco PostgreSQL:

- `xml_content` (TEXT) - Conteúdo do XML em formato texto
- `pdf_content` (BYTEA) - Conteúdo do PDF em formato binário

## 🚀 Execução Automática no Railway

A migração é executada **automaticamente em cada deploy** através do `railway_start.py`:

```
1. 🔧 Migração do banco (migrate_database.py)
2. 📜 Inicialização de certificados (railway_init.py)
3. 🌐 Início do Streamlit (app_nfse_enhanced.py)
```

### Comportamento no Railway

- ✅ Executa automaticamente no startup
- ✅ Modo não-interativo (sem prompts)
- ✅ Não bloqueia se falhar
- ✅ Idempotente (pode rodar múltiplas vezes com segurança)
- ✅ Não popula arquivos existentes (apenas adiciona colunas)

## 💻 Execução Manual Local

Para executar localmente e popular arquivos existentes:

```bash
python migrate_database.py
```

O script irá:
1. Verificar se as colunas já existem
2. Adicionar as colunas se necessário
3. Perguntar se deseja popular arquivos existentes do filesystem

### Popular Arquivos Existentes

Se você responder "sim", o script irá:
- Buscar todas as NFS-e com `xml_path` ou `pdf_path` preenchidos
- Ler os arquivos do filesystem
- Salvar o conteúdo no banco de dados

## 📊 Verificação Manual

Após a migração, você pode verificar no PostgreSQL:

```sql
-- Verificar se as colunas existem
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'nfse_emissoes' 
AND column_name IN ('xml_content', 'pdf_content');

-- Verificar quantos registros têm conteúdo
SELECT 
    COUNT(*) as total,
    COUNT(xml_content) as com_xml,
    COUNT(pdf_content) as com_pdf
FROM nfse_emissoes;

-- Ver tamanho médio dos arquivos
SELECT 
    AVG(LENGTH(xml_content)) as media_xml_bytes,
    AVG(LENGTH(pdf_content)) as media_pdf_bytes
FROM nfse_emissoes
WHERE xml_content IS NOT NULL OR pdf_content IS NOT NULL;
```

## 🔄 Rollback (se necessário)

Caso precise reverter a migração:

```sql
-- Remover as colunas
ALTER TABLE nfse_emissoes DROP COLUMN IF EXISTS xml_content;
ALTER TABLE nfse_emissoes DROP COLUMN IF EXISTS pdf_content;
```

## ⚠️ Importante

### Railway
- A migração roda a cada deploy
- É seguro rodar múltiplas vezes (idempotente)
- Não remove dados existentes
- Timeout de 60 segundos

### Local
- Pode popular arquivos existentes manualmente
- Requer arquivos no filesystem
- Útil para migrar dados históricos

## 🐛 Troubleshooting

### Erro: `UndefinedColumnError: column nfse_emissoes.xml_content does not exist`

**Solução**: Execute a migração manualmente:
```bash
python migrate_database.py
```

### Migração não executou no Railway

**Verificar logs do Railway**:
1. Procure por "🔧 Executando migração do banco"
2. Verifique se houve timeout ou erro
3. Se necessário, execute manualmente via Railway CLI

### Banco em outro servidor

Ajuste a `DATABASE_URL` no Railway ou `.env`:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/database
```

## 📚 Arquivos Relacionados

- `migrate_database.py` - Script de migração
- `railway_start.py` - Startup com migração automática
- `docs/database_setup.sql` - DDL completo com migrações
- `STORAGE_DATABASE.md` - Documentação do sistema de storage
- `src/database/models.py` - Model com as novas colunas
- `src/database/repository.py` - Métodos de acesso aos arquivos

---

**Versão**: 2.4  
**Data**: Janeiro 2026

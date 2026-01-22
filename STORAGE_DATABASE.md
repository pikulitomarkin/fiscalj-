# 📦 Armazenamento de Arquivos XML/PDF no Banco de Dados

## 📋 Visão Geral

A partir da versão 2.1, o sistema armazena o conteúdo completo dos arquivos XML e PDF das NFS-e no banco de dados PostgreSQL, garantindo persistência total e disponibilidade dos arquivos mesmo após reinicializações do sistema ou perda de arquivos do filesystem.

## 🎯 Objetivo

Resolver o problema de persistência de arquivos em ambientes de cloud (como Railway) onde o filesystem é efêmero e pode ser resetado entre deployments.

## 🔧 Implementação

### 1. Modelo de Dados

Foram adicionadas duas novas colunas na tabela `nfse_emissoes`:

```python
# src/database/models.py
class NFSeEmissao(Base):
    # ... campos existentes ...
    xml_content = Column(Text, nullable=True)        # Conteúdo do XML em texto
    pdf_content = Column(LargeBinary, nullable=True) # Conteúdo do PDF em binário
```

### 2. Migração do Banco

Execute o seguinte SQL para atualizar bancos existentes:

```sql
-- Adicionar colunas para conteúdo dos arquivos
ALTER TABLE nfse_emissoes ADD COLUMN IF NOT EXISTS xml_content TEXT;
ALTER TABLE nfse_emissoes ADD COLUMN IF NOT EXISTS pdf_content BYTEA;
```

Estas linhas já estão incluídas em `docs/database_setup.sql`.

### 3. Salvamento Automático

Quando uma NFS-e é emitida, o sistema automaticamente:

1. Salva os arquivos XML e PDF no filesystem (se disponível)
2. Lê o conteúdo dos arquivos
3. Armazena no banco de dados:
   - XML: como texto UTF-8
   - PDF: como dados binários

```python
# src/database/repository.py
async def save_nfse(self, nfse_data: Dict[str, Any], usuario: str = "admin") -> int:
    # ... código de salvamento ...
    
    # Armazenar conteúdo dos arquivos
    if xml_path and Path(xml_path).exists():
        nfse.xml_content = Path(xml_path).read_text(encoding='utf-8')
    
    if pdf_path and Path(pdf_path).exists():
        nfse.pdf_content = Path(pdf_path).read_bytes()
```

### 4. Recuperação de Arquivos

Três estratégias de fallback para garantir disponibilidade:

1. **Arquivo Local**: Tenta ler do filesystem primeiro
2. **Session State**: Usa dados em memória se disponíveis
3. **Banco de Dados**: Busca do PostgreSQL como último recurso

```python
# Exemplo: Download de PDF
pdf_content = None

# Estratégia 1: Arquivo local
if pdf_path and Path(pdf_path).exists():
    pdf_content = Path(pdf_path).read_bytes()

# Estratégia 2: Session state
elif nota.get('pdf_content'):
    pdf_content = nota.get('pdf_content')

# Estratégia 3: Banco de dados
elif nota.get('chave_acesso'):
    pdf_content = await nfse_repository.get_nfse_pdf(nota['chave_acesso'])
```

## 📥 Métodos de Download

### Downloads Individuais

A função `download_file_button()` foi atualizada para aceitar parâmetros adicionais:

```python
download_file_button(
    file_path='path/to/file.xml',      # Caminho local (opcional)
    label='📄 Baixar XML',               # Texto do botão
    key='unique_key',                    # Chave única do Streamlit
    chave_acesso='ABC123...',            # Chave de acesso da NFS-e
    file_type='xml'                      # Tipo: 'xml' ou 'pdf'
)
```

Se o arquivo local não existir, o sistema busca automaticamente do banco usando a `chave_acesso`.

### Downloads em Massa (ZIP)

Os botões de download em massa também foram atualizados:

- **Download de Todos os PDFs**: Cria ZIP com todos os PDFs disponíveis
- **Download de Todos os XMLs**: Cria ZIP com todos os XMLs disponíveis

Ambos tentam:
1. Ler arquivos locais
2. Buscar do `session_state`
3. Consultar banco de dados via `chave_acesso`

## 🔐 Segurança e Desempenho

### Tamanho dos Arquivos

- **XML**: Geralmente < 50 KB (armazenado como TEXT)
- **PDF**: Geralmente < 500 KB (armazenado como BYTEA)

### Considerações

- ✅ **Vantagem**: Persistência garantida independente do filesystem
- ✅ **Vantagem**: Backups incluem os arquivos automaticamente
- ⚠️ **Desvantagem**: Aumento do tamanho do banco de dados
- ⚠️ **Mitigação**: Implementar política de arquivamento/limpeza após X meses

### Índices Recomendados

```sql
-- Índice para busca rápida por chave de acesso
CREATE INDEX IF NOT EXISTS idx_nfse_chave_acesso ON nfse_emissoes(chave_acesso);
```

## 🧪 Testando a Funcionalidade

### 1. Emitir uma NFS-e

```python
# O sistema salvará automaticamente XML e PDF no banco
resultado = await emitir_nfse_completo(dados_tomador, dados_servico)
```

### 2. Verificar no Banco

```sql
SELECT 
    chave_acesso,
    LENGTH(xml_content) as tamanho_xml,
    LENGTH(pdf_content) as tamanho_pdf,
    xml_path,
    pdf_path
FROM nfse_emissoes
WHERE chave_acesso = 'SUA_CHAVE_AQUI';
```

### 3. Testar Download

No dashboard Streamlit:
1. Acesse "NFS-e Emitidas"
2. Clique em "📄 Baixar XML" ou "📑 Baixar PDF"
3. O arquivo deve baixar mesmo que não exista localmente

### 4. Simular Perda de Arquivos

```bash
# Deletar arquivos locais (para teste)
rm -rf pdfs/ xmls/

# Acessar dashboard e testar downloads
# Deve funcionar normalmente, buscando do banco
```

## 📊 Monitoramento

### Verificar Tamanho do Banco

```sql
-- Tamanho total da tabela nfse_emissoes
SELECT 
    pg_size_pretty(pg_total_relation_size('nfse_emissoes')) as tamanho_total,
    pg_size_pretty(pg_relation_size('nfse_emissoes')) as tamanho_dados,
    pg_size_pretty(pg_indexes_size('nfse_emissoes')) as tamanho_indices;
```

### Estatísticas de Armazenamento

```sql
-- Estatísticas de arquivos armazenados
SELECT 
    COUNT(*) as total_nfse,
    COUNT(xml_content) as com_xml,
    COUNT(pdf_content) as com_pdf,
    AVG(LENGTH(xml_content)) as media_tamanho_xml,
    AVG(LENGTH(pdf_content)) as media_tamanho_pdf
FROM nfse_emissoes;
```

## 🔄 Manutenção

### Limpeza de Arquivos Antigos (Opcional)

Se o banco crescer muito, considere arquivar ou remover conteúdo de notas antigas:

```sql
-- Remover conteúdo de arquivos de notas com mais de 1 ano
UPDATE nfse_emissoes 
SET 
    xml_content = NULL,
    pdf_content = NULL
WHERE created_at < NOW() - INTERVAL '1 year'
AND xml_content IS NOT NULL OR pdf_content IS NOT NULL;
```

### Backup Seletivo

```bash
# Backup apenas dos metadados (sem arquivos)
pg_dump nfse_db \
    --exclude-table-data=nfse_emissoes \
    > metadados_backup.sql

# Backup completo (inclui arquivos)
pg_dump nfse_db > backup_completo.sql
```

## 🚀 Próximos Passos

1. ✅ Implementar salvamento automático no banco
2. ✅ Criar métodos de recuperação com fallback
3. ✅ Atualizar botões de download individual
4. ✅ Atualizar downloads em massa (ZIP)
5. ⏳ Implementar política de arquivamento
6. ⏳ Criar dashboard de estatísticas de armazenamento
7. ⏳ Adicionar compressão para arquivos grandes

## 📚 Referências

- [PostgreSQL Binary Data Types](https://www.postgresql.org/docs/current/datatype-binary.html)
- [SQLAlchemy LargeBinary](https://docs.sqlalchemy.org/en/14/core/type_basics.html#sqlalchemy.types.LargeBinary)
- [Streamlit File Downloads](https://docs.streamlit.io/library/api-reference/widgets/st.download_button)

## 💡 Dicas

### Railway Deployment

No Railway, os volumes montados são persistentes, mas o código e environment podem ser resetados. Com esta implementação:

- ✅ Arquivos no banco sobrevivem a deploys
- ✅ Não depende de volumes montados
- ✅ Backups automáticos do PostgreSQL incluem os arquivos

### Desenvolvimento Local

Para desenvolvimento local, os arquivos continuam disponíveis no filesystem também, proporcionando:

- ✅ Facilidade de visualização durante debug
- ✅ Backup duplo (filesystem + banco)
- ✅ Compatibilidade com ferramentas externas

---

**Versão**: 2.1  
**Data**: 2024  
**Autor**: Sistema NFS-e VSB Tubarão

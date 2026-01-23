# 📋 Estrutura XML ADN v1.01 - Tributos Federais

## 🎯 Resumo

Documentação da estrutura correta do XML NFS-e no padrão ADN (Ambiente de Disponibilização Nacional) versão 1.01 com suporte completo aos tributos federais (PIS, COFINS, INSS, IR, CSLL).

---

## 🔧 Implementação Atual

### Localização
- **Arquivo**: `src/utils/xml_generator.py`
- **Método**: `_add_valores_v101()`
- **Linhas**: 232-329

### Tributos Suportados

| Tributo | Campo XML | Alíquota Padrão | Calculado |
|---------|-----------|-----------------|-----------|
| **PIS** | `piscofins/vPIS` | 0.65% | ✅ Sim |
| **COFINS** | `piscofins/vCOFINS` | 3.00% | ✅ Sim |
| **CP (INSS)** | `vRetCP` | 0.00% | ✅ Sim |
| **IRRF** | `vRetIRRF` | 0.00% | ✅ Sim |
| **CSLL** | `vRetCSLL` | 0.00% | ✅ Sim |
| **ISS** | `tribISSQN` | 3.00% | ✅ Sim |

---

## 📐 Estrutura XML Completa

### Exemplo Prático

```xml
<?xml version="1.0" encoding="UTF-8"?>
<DPS xmlns="http://www.sped.fazenda.gov.br/nfse" versao="1.01">
  <infDPS Id="DPS4218707258645846000169000011234567890123456">
    <tpAmb>2</tpAmb>
    <dhEmi>2026-01-22T15:30:00-03:00</dhEmi>
    <verAplic>1.0.0</verAplic>
    <serie>00001</serie>
    <nDPS>1</nDPS>
    <dCompet>2026-01-22</dCompet>
    <tpEmit>1</tpEmit>
    <cLocEmi>4218707</cLocEmi>
    
    <prest>
      <CNPJ>58645846000169</CNPJ>
      <IM>93442</IM>
      <regTrib>
        <opSimpNac>1</opSimpNac>
        <regEspTrib>0</regEspTrib>
      </regTrib>
    </prest>
    
    <toma>
      <CPF>12345678901</CPF>
      <xNome>João da Silva</xNome>
    </toma>
    
    <serv>
      <locPrest>
        <cLocPrestacao>4218707</cLocPrestacao>
      </locPrest>
      <cServ>
        <cTribNac>040101</cTribNac>
        <xDescServ>Serviços médicos especializados - teleconsulta</xDescServ>
      </cServ>
    </serv>
    
    <!-- ========================================== -->
    <!-- VALORES E TRIBUTOS (FOCO PRINCIPAL)       -->
    <!-- ========================================== -->
    <valores>
      <!-- Valor do Serviço -->
      <vServPrest>
        <vServ>89.00</vServ>
      </vServPrest>
      
      <!-- Desconto (Opcional) -->
      <vDescIncond>0.00</vDescIncond>
      
      <!-- Tributos -->
      <trib>
        <!-- Tributos Municipais -->
        <tribMun>
          <tribISSQN>1</tribISSQN>
          <tpRetISSQN>1</tpRetISSQN>
        </tribMun>
        
        <!-- ⭐ TRIBUTOS FEDERAIS (NOVO) ⭐ -->
        <tribFed>
          <!-- PIS e COFINS combinados em um único elemento -->
          <piscofins>
            <!-- PIS: 0.65% de R$ 89,00 = R$ 0,58 -->
            <vPIS>0.58</vPIS>
            
            <!-- COFINS: 3.00% de R$ 89,00 = R$ 2,67 -->
            <vCOFINS>2.67</vCOFINS>
          </piscofins>
          
          <!-- CP (Contribuição Previdenciária/INSS): 0.00% (opcional) -->
          <vRetCP>0.00</vRetCP>
          
          <!-- IRRF (Imposto de Renda Retido na Fonte): 0.00% (opcional) -->
          <vRetIRRF>0.00</vRetIRRF>
          
          <!-- CSLL: 0.00% (opcional) -->
          <vRetCSLL>0.00</vRetCSLL>
        </tribFed>
        
        <!-- Total de Tributos -->
        <totTrib>
          <!-- Percentual Total: ISS(3%) + PIS(0.65%) + COFINS(3%) = 6.65% -->
          <pTotTribSN>6.65</pTotTribSN>
        </totTrib>
      </trib>
    </valores>
  </infDPS>
  
  <!-- Assinatura Digital (quando aplicável) -->
  <Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
    <!-- ... -->
  </Signature>
</DPS>
```

---

## 💻 Uso no Código Python

### 1. Configurar Tributos Federais

```python
from decimal import Decimal
from src.models.schemas import Servico, PrestadorServico, TomadorServico, NFSeRequest
from src.utils.xml_generator import NFSeXMLGenerator

# Criar serviço com tributos federais
servico = Servico(
    descricao="Serviços médicos especializados - teleconsulta",
    valor_servico=Decimal("89.00"),
    aliquota_iss=Decimal("3.00"),      # ISS: 3%
    aliquota_pis=Decimal("0.65"),      # PIS: 0.65%
    aliquota_cofins=Decimal("3.00"),   # COFINS: 3%
    aliquota_inss=Decimal("0.00"),     # INSS: não aplicável
    aliquota_ir=Decimal("0.00"),       # IR: não aplicável
    aliquota_csll=Decimal("0.00"),     # CSLL: não aplicável
    item_lista_servico="04.01.01"
)

# Criar prestador
prestador = PrestadorServico(
    cnpj="58645846000169",
    inscricao_municipal="93442",
    razao_social="VSB SERVICOS MEDICOS LTDA"
)

# Criar tomador
tomador = TomadorServico(
    cpf="12345678901",
    nome="João da Silva"
)

# Montar requisição
nfse_request = NFSeRequest(
    prestador=prestador,
    tomador=tomador,
    servico=servico
)

# Gerar XML
generator = NFSeXMLGenerator()
xml = generator.gerar_xml_nfse(nfse_request)

print(xml)
```

### 2. Valores Calculados Automaticamente

O sistema calcula automaticamente os valores de retenção:

```python
# Base de Cálculo
base_calculo = valor_servico - valor_deducoes
# 89.00 - 0.00 = 89.00

# PIS (0.65%)
v_ret_pis = base_calculo * (aliquota_pis / 100)
# 89.00 * 0.0065 = 0.58

# COFINS (3.00%)
v_ret_cofins = base_calculo * (aliquota_cofins / 100)
# 89.00 * 0.03 = 2.67

# Percentual Total
percentual_total = iss + pis + cofins + inss + ir + csll
# 3.00 + 0.65 + 3.00 + 0.00 + 0.00 + 0.00 = 6.65%
```

---

## 📊 Casos de Uso

### Caso 1: Apenas PIS e COFINS (Padrão)

```python
servico = Servico(
    descricao="Consultoria técnica",
    valor_servico=Decimal("1000.00"),
    aliquota_iss=Decimal("3.00"),
    aliquota_pis=Decimal("0.65"),    # ✅ Enviado
    aliquota_cofins=Decimal("3.00"),  # ✅ Enviado
    item_lista_servico="01.01"
)
```

**Resultado XML:**
```xml
<tribFed>
  <piscofins>
    <vPIS>6.50</vPIS>          <!-- 0.65% de 1000 -->
    <vCOFINS>30.00</vCOFINS>   <!-- 3.00% de 1000 -->
  </piscofins>
</tribFed>
```

### Caso 2: Todos os Tributos Federais

```python
servico = Servico(
    descricao="Serviços profissionais",
    valor_servico=Decimal("5000.00"),
    aliquota_iss=Decimal("5.00"),
    aliquota_pis=Decimal("0.65"),
    aliquota_cofins=Decimal("3.00"),
    aliquota_inss=Decimal("11.00"),   # ✅ INSS 11%
    aliquota_ir=Decimal("1.50"),      # ✅ IR 1.5%
    aliquota_csll=Decimal("1.00"),    # ✅ CSLL 1%
    item_lista_servico="17.05"
)
```

**Resultado XML:**
```piscofins>
    <vPIS>32.50</vPIS>         <!-- 0.65% de 5000 -->
    <vCOFINS>150.00</vCOFINS>  <!-- 3.00% de 5000 -->
  </piscofins>
  <vRetCP>550.00</vRetCP>      <!-- 11.00% de 5000 (INSS) -->
  <vRetIRRF>75.00</vRetIRRF>   <!-- 1.50% de 5000 (IR) -->
  <vRetCSLL>50.00</vRetCSLL>   <!-- 11.00% de 5000 -->
  <vRetIR>75.00</vRetIR>         <!-- 1.50% de 5000 -->
  <vRetCSLL>50.00</vRetCSLL>     <!-- 1.00% de 5000 -->
</tribFed>
<totTrib>
  <pTotTribSN>22.15</pTotTribSN> <!-- 5+0.65+3+11+1.5+1 -->
</totTrib>
```

### Caso 3: Sem Tributos Federais

```python
servico = Servico(
    descricao="Serviço simples",
    valor_servico=Decimal("100.00"),
    aliquota_iss=Decimal("2.00"),
    aliquota_pis=Decimal("0.00"),     # Zero
    aliquota_cofins=Decimal("0.00"),  # Zero
    item_lista_servico="01.01"
)
```

**Resultado XML:** (elemento `tribFed` **NÃO** será incluído)
```xml
<trib>
  <tribMun>
    <tribISSQN>1</tribISSQN>
    <tpRetISSQN>1</tpRetISSQN>
  </tribMun>
  <!-- tribFed omitido -->
  <totTrib>
    <pTotTribSN>2.00</pTotTribSN>
  </totTrib>
</trib>
```

---

## 🔍 Elementos do XML - Referência Rápida

### Elemento `<valores>`

| Elemento | Obrigatório | Descrição |
|----------|-------------|-----------|
| `vServPrest` | ✅ Sim | Container para valores do serviço |
| `vServPrest/vServ` | ✅ Sim | Valor total do serviço |
| `vDescIncond` | ❌ Não | Desconto incondicional |
| `trib` | ✅ Sim | Container para tributos |

### Elemento `<trib>`

| Elemento | Obrigatório | Descrição |
|----------|-------------|-----------|
| `tribMun` | ✅ Sim | Tributos municipais (ISS) |
| `tribFed` | ❌ Não | Tributos federais (PIS/COFINS/INSS/IR/CSLL) |
| `totTrib` | ✅ Sim | Total de tributos |

### Elemento `<tribFed>` ⭐ NOVO

| Elemento | Obrigatório | Descrição | Exemplo |
|----------|-------------|-----------|---------|
| `piscofins` | ❌ Não | Container para PIS e COFINS | - |
| `piscofins/vPIS` | ❌ Não | Valor do PIS | `0.58` |
| `piscofins/vCOFINS` | ❌ Não | Valor do COFINS | `2.67` |
| `vRetCP` | ❌ Não | Contribuição Previdenciária (INSS) | `0.00` |
| `vRetIRRF` | ❌ Não | Imposto de Renda Retido na Fonte | `0.00` |
| `vRetCSLL` | ❌ Não | CSLL Retido | `0.00` |

> **Nota**: O elemento `tribFed` só é incluído se **pelo menos um** dos tributos federais for maior que zero.

---

## ✅ Validação

### Verificar XML Gerado

```python
import xml.etree.ElementTree as ET

# Parse do XML
tree = ET.fromstring(xml)
ns = {'nfse': 'http://www.sped.fazenda.gov.br/nfse'}

# Verificar tributos federais
trib_fed = tree.find('.//nfse:tribFed', ns)

if trib_fed is not None:
    print("✅ Tributos federais encontrados:")
    
    pis = trib_fed.findtext('nfse:vRetPIS', namespaces=ns)
    cofins = trib_fed.findtext('nfse:vRetCOFINS', namespaces=ns)
    
    print(f"  PIS: R$ {pis}")
    print(f"  COFINS: R$ {cofins}")
else:
    print("⚠️  Nenhum tributo federal configurado")
```

---

## 📌 Observações Importantes

1. **Cálculo Automático**: Os valores são calculados automaticamente com base nas alíquotas e no valor do serviço
2. **Base de Cálculo**: `base_calculo = valor_servico - valor_deducoes`
3. **Formato**: Valores sempre com 2 casas decimais (ex: `0.58`, `2.67`)
4. **Omissão**: Se todas as alíquotas federais forem zero ou None, o elemento `<tribFed>` não é incluído
5. **Namespace**: Sempre usar o namespace oficial: `http://www.sped.fazenda.gov.br/nfse`
6. **Versão**: Esta estrutura é válida para ADN v1.01

---

## 🆘 Troubleshooting

### Problema: tribFed não aparece no XML

**Causa**: Todas as alíquotas federais estão zeradas ou None.

**Solução**: Definir pelo menos uma alíquota maior que zero:
```python
servico.aliquota_pis = Decimal("0.65")
servico.aliquota_cofins = Decimal("3.00")
```

### Problema: Valores incorretos

**Causa**: Alíquotas configuradas em valores absolutos em vez de percentuais.

**Solução**: Usar valores percentuais (0.65 = 0.65%, não 65%):
```python
# ❌ ERRADO
aliquota_pis = Decimal("65")  # 65% (incorreto)

# ✅ CORRETO
aliquota_pis = Decimal("0.65")  # 0.65% (correto)
```

### Problema: pTotTribSN não corresponde ao esperado

**Causa**: O percentual total agora soma TODOS os tributos (ISS + federais).

**Solução**: Verificar se está considerando todos os tributos:
```python
# Cálculo correto
percentual_total = (
    aliquota_iss +      # 3.00
    aliquota_pis +      # 0.65
    aliquota_cofins +   # 3.00
    aliquota_inss +     # 0.00
    aliquota_ir +       # 0.00
    aliquota_csll       # 0.00
)  # Total: 6.65%
```

---

## 📚 Referências

- **Padrão Nacional**: Ambiente de Disponibilização Nacional (ADN) v1.01
- **Namespace**: `http://www.sped.fazenda.gov.br/nfse`
- **Arquivo**: [src/utils/xml_generator.py](src/utils/xml_generator.py)
- **Schema**: [src/models/schemas.py](src/models/schemas.py)
- **Documentação API**: [docs/api_adn_reference.json](docs/api_adn_reference.json)

---

**✅ Implementação concluída em 22/01/2026**

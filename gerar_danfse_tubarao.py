"""
Gera DANFSE (Documento Auxiliar da NFS-e) em PDF
Layout oficial baseado no modelo da Prefeitura de Tubarão/SC
Versão DANFSe v1.0
"""

from pathlib import Path
from lxml import etree
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
from decimal import Decimal
import qrcode
from io import BytesIO
import os


class GeradorDANFSETubarao:
    """Gerador de DANFSE no padrão Prefeitura de Tubarão/SC."""
    
    def __init__(self, xml_path: str = None, dados_nfse: dict = None):
        """
        Inicializa gerador.
        
        Args:
            xml_path: Caminho do XML da NFS-e autorizada (opcional)
            dados_nfse: Dicionário com dados da NFS-e (alternativa ao XML)
        """
        self.xml_path = Path(xml_path) if xml_path else None
        self.ns = {'nfse': 'http://www.sped.fazenda.gov.br/nfse'}
        
        if xml_path and Path(xml_path).exists():
            # Carregar e parsear XML
            xml_content = self.xml_path.read_text(encoding='utf-8')
            self.root = etree.fromstring(xml_content.encode('utf-8'))
            self._extrair_dados_xml()
        elif dados_nfse:
            self._carregar_dados_dict(dados_nfse)
        else:
            raise ValueError("Forneça xml_path ou dados_nfse")
    
    def _carregar_dados_dict(self, dados: dict):
        """Carrega dados de um dicionário."""
        self.chave_acesso = dados.get('chave_acesso', '')
        self.numero_nfse = dados.get('numero', '')
        self.numero_dps = dados.get('numero_dps', '')
        self.serie_dps = dados.get('serie_dps', '900')
        self.competencia = dados.get('competencia', datetime.now().strftime('%m/%Y'))
        self.data_emissao = dados.get('data_emissao', datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
        
        # Prestador
        self.prestador = {
            'cnpj': dados.get('prestador_cnpj', '58.645.846/0001-69'),
            'im': dados.get('prestador_im', '93442'),
            'razao_social': dados.get('prestador_razao', 'VSB SERVICOS MEDICOS LTDA'),
            'endereco': dados.get('prestador_endereco', 'RUA LUIZ MARTINS COLLACO, 1175, CENTRO'),
            'municipio': dados.get('prestador_municipio', 'Tubarão - SC'),
            'cep': dados.get('prestador_cep', '88701-330'),
            'telefone': dados.get('prestador_telefone', '(48) 9150-1441'),
            'email': dados.get('prestador_email', 'VINISILV@HOTMAIL.COM'),
            'simples_nacional': dados.get('simples_nacional', 'Não optante'),
            'regime_apuracao': dados.get('regime_apuracao', '-'),
        }
        
        # Tomador
        self.tomador = {
            'documento': dados.get('tomador_cpf', dados.get('tomador_cnpj', '')),
            'nome': dados.get('tomador_nome', ''),
            'endereco': dados.get('tomador_endereco', '-'),
            'municipio': dados.get('tomador_municipio', '-'),
            'cep': dados.get('tomador_cep', '-'),
            'email': dados.get('tomador_email', '-'),
            'telefone': dados.get('tomador_telefone', '-'),
            'im': dados.get('tomador_im', '-'),
        }
        
        # Serviço
        self.servico = {
            'codigo_nacional': dados.get('codigo_servico', '04.01.01 - Medicina.'),
            'codigo_municipal': dados.get('codigo_municipal', '-'),
            'descricao': dados.get('descricao_servico', 'teleconsulta'),
            'local_prestacao': dados.get('local_prestacao', 'Tubarão - SC'),
            'pais_prestacao': dados.get('pais_prestacao', '-'),
            'nbs': dados.get('nbs', '123019900'),
        }
        
        # Valores
        valor = Decimal(str(dados.get('valor', '89.00')))
        aliquota = Decimal(str(dados.get('aliquota_iss', '3.00')))
        iss = valor * (aliquota / 100)
        
        self.valores = {
            'valor_servico': valor,
            'base_calculo': valor,
            'aliquota_iss': aliquota,
            'valor_iss': iss,
            'iss_retido': dados.get('iss_retido', False),
            'valor_liquido': valor,
            'deducoes': Decimal('0.00'),
            'desconto_incondicionado': Decimal('0.00'),
            'desconto_condicionado': Decimal('0.00'),
        }
        
        # Tributação Federal (aproximada)
        self.tributos_federais = {
            'irrf': Decimal('0.00'),
            'pis': valor * Decimal('0.0065'),  # 0.65%
            'cofins': valor * Decimal('0.03'),  # 3%
            'csll': Decimal('0.00'),
            'cp': Decimal('0.00'),
            'inss': Decimal('0.00'),
        }
        
        # Tributação
        self.tributacao = {
            'operacao_tributavel': True,
            'municipio_incidencia': 'Tubarão - SC',
            'regime_especial': 'Nenhum',
            'imunidade': '-',
            'suspensao_exigibilidade': 'Não',
            'numero_processo': '-',
            'beneficio_municipal': '-',
        }
    
    def _extrair_dados_xml(self):
        """Extrai dados do XML."""
        inf_nfse = self.root.find('.//nfse:infNFSe', self.ns)
        
        # Chave e número
        id_nfse = inf_nfse.get('Id', '')
        self.chave_acesso = id_nfse.replace('NFS', '') if id_nfse.startswith('NFS') else id_nfse
        self.numero_nfse = inf_nfse.findtext('.//nfse:nNFSe', namespaces=self.ns, default='')
        self.numero_dps = inf_nfse.findtext('.//nfse:nDPS', namespaces=self.ns, default='')
        self.serie_dps = inf_nfse.findtext('.//nfse:serie', namespaces=self.ns, default='900')
        
        dh_proc = inf_nfse.findtext('.//nfse:dhProc', namespaces=self.ns, default='')
        if dh_proc:
            try:
                dt = datetime.fromisoformat(dh_proc.replace('Z', '+00:00'))
                self.data_emissao = dt.strftime('%d/%m/%Y %H:%M:%S')
                self.competencia = dt.strftime('%d/%m/%Y')
            except:
                self.data_emissao = dh_proc
                self.competencia = dh_proc[:10]
        else:
            self.data_emissao = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            self.competencia = datetime.now().strftime('%d/%m/%Y')
        
        # Carregar dados básicos dos elementos
        self._carregar_dados_dict({
            'chave_acesso': self.chave_acesso,
            'numero': self.numero_nfse,
        })
    
    def _formatar_cnpj(self, cnpj: str) -> str:
        """Formata CNPJ com pontuação."""
        cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
    
    def _formatar_cpf(self, cpf: str) -> str:
        """Formata CPF com pontuação."""
        cpf = cpf.replace('.', '').replace('-', '')
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    def _formatar_moeda(self, valor) -> str:
        """Formata valor em moeda brasileira."""
        if valor is None:
            return "R$ 0,00"
        try:
            v = Decimal(str(valor))
            return f"R$ {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return f"R$ {valor}"
    
    def _gerar_qrcode(self) -> Image:
        """Gera QR Code com a chave de acesso."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=3,
            border=1,
        )
        
        url_consulta = f"https://www.nfse.gov.br/consultapublica?chave={self.chave_acesso}"
        qr.add_data(url_consulta)
        qr.make(fit=True)
        
        img_qr = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img_qr.save(buffer, format='PNG')
        buffer.seek(0)
        
        img = Image(buffer, width=2.2*cm, height=2.2*cm)
        return img
    
    def gerar_pdf(self, output_path: str):
        """Gera PDF no layout da Prefeitura de Tubarão."""
        
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4
        
        # Cores
        azul_escuro = colors.HexColor('#003366')
        cinza_claro = colors.HexColor('#F5F5F5')
        cinza_borda = colors.HexColor('#CCCCCC')
        
        # Margens
        margin_left = 1.2*cm
        margin_right = 1.2*cm
        margin_top = 1*cm
        content_width = width - margin_left - margin_right
        
        y = height - margin_top
        
        # =====================================================================
        # CABEÇALHO
        # =====================================================================
        header_height = 2.5*cm
        
        # Caixa do cabeçalho
        c.setStrokeColor(cinza_borda)
        c.setLineWidth(1)
        c.rect(margin_left, y - header_height, content_width, header_height)
        
        # Logo NFS-e (texto simulado)
        c.setFillColor(colors.HexColor('#006600'))
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin_left + 0.3*cm, y - 1.2*cm, "NFS")
        c.setFillColor(colors.HexColor('#FF6600'))
        c.drawString(margin_left + 1.5*cm, y - 1.2*cm, "e")
        c.setFillColor(colors.grey)
        c.setFont("Helvetica", 6)
        c.drawString(margin_left + 0.3*cm, y - 1.6*cm, "Nota Fiscal de")
        c.drawString(margin_left + 0.3*cm, y - 1.9*cm, "Serviço eletrônica")
        
        # Título central
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, y - 1*cm, "DANFSe v1.0")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, y - 1.5*cm, "Documento Auxiliar da NFS-e")
        
        # Prefeitura (direita)
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(width - margin_right - 0.3*cm, y - 0.8*cm, "PREFEITURA MUNICIPAL DE")
        c.drawRightString(width - margin_right - 0.3*cm, y - 1.2*cm, "TUBARÃO")
        c.setFont("Helvetica", 7)
        c.drawRightString(width - margin_right - 0.3*cm, y - 1.6*cm, "(48)3621-9832")
        c.drawRightString(width - margin_right - 0.3*cm, y - 1.9*cm, "fazenda@tubarao.sc.gov.br")
        
        y -= header_height + 0.2*cm
        
        # =====================================================================
        # CHAVE DE ACESSO
        # =====================================================================
        c.setFont("Helvetica", 7)
        c.drawString(margin_left, y - 0.4*cm, "Chave de Acesso da NFS-e")
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, y - 0.8*cm, self.chave_acesso)
        
        y -= 1*cm
        
        # =====================================================================
        # DADOS DA NFS-e (com QR Code)
        # =====================================================================
        dados_height = 2.5*cm
        
        # Colunas de dados
        col1_x = margin_left
        col2_x = margin_left + 4*cm
        col3_x = margin_left + 8*cm
        col4_x = margin_left + 12*cm
        
        # Linha 1: Número, Competência, Data Emissão
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(col1_x, y - 0.3*cm, "Número da NFS-e")
        c.drawString(col2_x, y - 0.3*cm, "Competência da NFS-e")
        c.drawString(col3_x, y - 0.3*cm, "Data e Hora da emissão da NFS-e")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(col1_x, y - 0.7*cm, str(self.numero_nfse))
        c.drawString(col2_x, y - 0.7*cm, self.competencia)
        c.drawString(col3_x, y - 0.7*cm, self.data_emissao)
        
        # Linha 2: Número DPS, Série DPS, Data DPS
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(col1_x, y - 0.3*cm, "Número da DPS")
        c.drawString(col2_x, y - 0.3*cm, "Série da DPS")
        c.drawString(col3_x, y - 0.3*cm, "Data e Hora da emissão da DPS")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(col1_x, y - 0.7*cm, str(self.numero_dps) if self.numero_dps else "-")
        c.drawString(col2_x, y - 0.7*cm, self.serie_dps)
        c.drawString(col3_x, y - 0.7*cm, self.data_emissao)
        
        # QR Code (lado direito)
        qr_img = self._gerar_qrcode()
        qr_img.drawOn(c, width - margin_right - 2.5*cm, y - 1*cm)
        
        # Texto do QR Code
        c.setFont("Helvetica", 5)
        c.setFillColor(colors.grey)
        qr_text_x = width - margin_right - 2.5*cm
        c.drawString(qr_text_x, y - 1.3*cm - 2.2*cm, "A autenticidade desta NFS-e pode ser verificada")
        c.drawString(qr_text_x, y - 1.6*cm - 2.2*cm, "pela leitura deste código QR ou pela consulta da")
        c.drawString(qr_text_x, y - 1.9*cm - 2.2*cm, "chave de acesso no portal nacional da NFS-e")
        
        y -= 1.5*cm
        
        # =====================================================================
        # EMITENTE DA NFS-e
        # =====================================================================
        c.setStrokeColor(cinza_borda)
        c.setLineWidth(0.5)
        c.line(margin_left, y, width - margin_right, y)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, y - 0.4*cm, "EMITENTE DA NFS-e")
        
        # CNPJ e IM
        y -= 0.6*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "CNPJ / CPF / NIF")
        c.drawString(margin_left + 5*cm, y - 0.3*cm, "Inscrição Municipal")
        c.drawString(margin_left + 10*cm, y - 0.3*cm, "Telefone")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self._formatar_cnpj(self.prestador['cnpj']))
        c.drawString(margin_left + 5*cm, y - 0.7*cm, self.prestador['im'])
        c.drawString(margin_left + 10*cm, y - 0.7*cm, self.prestador['telefone'])
        
        # Razão Social e Email
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Nome / Nome Empresarial")
        c.drawString(margin_left + 10*cm, y - 0.3*cm, "E-mail")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self.prestador['razao_social'])
        c.drawString(margin_left + 10*cm, y - 0.7*cm, self.prestador['email'])
        
        # Endereço e Município/CEP
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Endereço")
        c.drawString(margin_left + 10*cm, y - 0.3*cm, "Município")
        c.drawString(margin_left + 14*cm, y - 0.3*cm, "CEP")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self.prestador['endereco'])
        c.drawString(margin_left + 10*cm, y - 0.7*cm, self.prestador['municipio'])
        c.drawString(margin_left + 14*cm, y - 0.7*cm, self.prestador['cep'])
        
        # Simples Nacional
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Simples Nacional na Data de Competência")
        c.drawString(margin_left + 10*cm, y - 0.3*cm, "Regime de Apuração Tributária pelo SN")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self.prestador['simples_nacional'])
        c.drawString(margin_left + 10*cm, y - 0.7*cm, self.prestador['regime_apuracao'])
        
        y -= 1.2*cm
        
        # =====================================================================
        # TOMADOR DO SERVIÇO
        # =====================================================================
        c.setStrokeColor(cinza_borda)
        c.line(margin_left, y, width - margin_right, y)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, y - 0.4*cm, "TOMADOR DO SERVIÇO")
        
        y -= 0.6*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "CNPJ / CPF / NIF")
        c.drawString(margin_left + 5*cm, y - 0.3*cm, "Inscrição Municipal")
        c.drawString(margin_left + 10*cm, y - 0.3*cm, "Telefone")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        doc_tomador = self.tomador['documento']
        if len(doc_tomador.replace('.', '').replace('-', '').replace('/', '')) == 11:
            doc_tomador = self._formatar_cpf(doc_tomador)
        c.drawString(margin_left, y - 0.7*cm, doc_tomador)
        c.drawString(margin_left + 5*cm, y - 0.7*cm, self.tomador['im'])
        c.drawString(margin_left + 10*cm, y - 0.7*cm, self.tomador['telefone'])
        
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Nome / Nome Empresarial")
        c.drawString(margin_left + 10*cm, y - 0.3*cm, "E-mail")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self.tomador['nome'])
        c.drawString(margin_left + 10*cm, y - 0.7*cm, self.tomador['email'])
        
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Endereço")
        c.drawString(margin_left + 10*cm, y - 0.3*cm, "Município")
        c.drawString(margin_left + 14*cm, y - 0.3*cm, "CEP")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self.tomador['endereco'])
        c.drawString(margin_left + 10*cm, y - 0.7*cm, self.tomador['municipio'])
        c.drawString(margin_left + 14*cm, y - 0.7*cm, self.tomador['cep'])
        
        y -= 1.2*cm
        
        # =====================================================================
        # INTERMEDIÁRIO DO SERVIÇO
        # =====================================================================
        c.setStrokeColor(cinza_borda)
        c.line(margin_left, y, width - margin_right, y)
        
        c.setFillColor(colors.grey)
        c.setFont("Helvetica", 7)
        c.drawCentredString(width/2, y - 0.4*cm, "INTERMEDIÁRIO DO SERVIÇO NÃO IDENTIFICADO NA NFS-e")
        
        y -= 0.7*cm
        
        # =====================================================================
        # SERVIÇO PRESTADO
        # =====================================================================
        c.setStrokeColor(cinza_borda)
        c.line(margin_left, y, width - margin_right, y)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, y - 0.4*cm, "SERVIÇO PRESTADO")
        
        y -= 0.6*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Código de Tributação Nacional")
        c.drawString(margin_left + 5*cm, y - 0.3*cm, "Código de Tributação Municipal")
        c.drawString(margin_left + 10*cm, y - 0.3*cm, "Local da Prestação")
        c.drawString(margin_left + 14*cm, y - 0.3*cm, "País da Prestação")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self.servico['codigo_nacional'])
        c.drawString(margin_left + 5*cm, y - 0.7*cm, self.servico['codigo_municipal'])
        c.drawString(margin_left + 10*cm, y - 0.7*cm, self.servico['local_prestacao'])
        c.drawString(margin_left + 14*cm, y - 0.7*cm, self.servico['pais_prestacao'])
        
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Descrição do Serviço")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self.servico['descricao'])
        
        y -= 1.2*cm
        
        # =====================================================================
        # TRIBUTAÇÃO MUNICIPAL
        # =====================================================================
        c.setStrokeColor(cinza_borda)
        c.line(margin_left, y, width - margin_right, y)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, y - 0.4*cm, "TRIBUTAÇÃO MUNICIPAL")
        
        # Linha 1
        y -= 0.6*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Tributação do ISSQN")
        c.drawString(margin_left + 4*cm, y - 0.3*cm, "País Resultado da Prestação do Serviço")
        c.drawString(margin_left + 9*cm, y - 0.3*cm, "Município de Incidência do ISSQN")
        c.drawString(margin_left + 14*cm, y - 0.3*cm, "Regime Especial de Tributação")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, "Operação Tributável" if self.tributacao['operacao_tributavel'] else "-")
        c.drawString(margin_left + 4*cm, y - 0.7*cm, "-")
        c.drawString(margin_left + 9*cm, y - 0.7*cm, self.tributacao['municipio_incidencia'])
        c.drawString(margin_left + 14*cm, y - 0.7*cm, self.tributacao['regime_especial'])
        
        # Linha 2
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Tipo de Imunidade")
        c.drawString(margin_left + 4*cm, y - 0.3*cm, "Suspensão da Exigibilidade do ISSQN")
        c.drawString(margin_left + 9*cm, y - 0.3*cm, "Número Processo Suspensão")
        c.drawString(margin_left + 14*cm, y - 0.3*cm, "Benefício Municipal")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self.tributacao['imunidade'])
        c.drawString(margin_left + 4*cm, y - 0.7*cm, self.tributacao['suspensao_exigibilidade'])
        c.drawString(margin_left + 9*cm, y - 0.7*cm, self.tributacao['numero_processo'])
        c.drawString(margin_left + 14*cm, y - 0.7*cm, self.tributacao['beneficio_municipal'])
        
        # Linha 3 - Valores
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Valor do Serviço")
        c.drawString(margin_left + 4*cm, y - 0.3*cm, "Desconto Incondicionado")
        c.drawString(margin_left + 9*cm, y - 0.3*cm, "Total Deduções/Reduções")
        c.drawString(margin_left + 14*cm, y - 0.3*cm, "Cálculo do BM")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self._formatar_moeda(self.valores['valor_servico']))
        c.drawString(margin_left + 4*cm, y - 0.7*cm, "-")
        c.drawString(margin_left + 9*cm, y - 0.7*cm, "-")
        c.drawString(margin_left + 14*cm, y - 0.7*cm, "-")
        
        # Linha 4 - Base, Alíquota, Retenção, ISSQN
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "BC ISSQN")
        c.drawString(margin_left + 4*cm, y - 0.3*cm, "Alíquota Aplicada")
        c.drawString(margin_left + 9*cm, y - 0.3*cm, "Retenção do ISSQN")
        c.drawString(margin_left + 14*cm, y - 0.3*cm, "ISSQN Apurado")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self._formatar_moeda(self.valores['base_calculo']))
        c.drawString(margin_left + 4*cm, y - 0.7*cm, f"{self.valores['aliquota_iss']}%")
        c.drawString(margin_left + 9*cm, y - 0.7*cm, "Não Retido" if not self.valores['iss_retido'] else "Retido")
        c.drawString(margin_left + 14*cm, y - 0.7*cm, self._formatar_moeda(self.valores['valor_iss']))
        
        y -= 1.2*cm
        
        # =====================================================================
        # TRIBUTAÇÃO FEDERAL
        # =====================================================================
        c.setStrokeColor(cinza_borda)
        c.line(margin_left, y, width - margin_right, y)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, y - 0.4*cm, "TRIBUTAÇÃO FEDERAL")
        
        y -= 0.6*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "IRRF")
        c.drawString(margin_left + 3.5*cm, y - 0.3*cm, "CP")
        c.drawString(margin_left + 7*cm, y - 0.3*cm, "CSLL")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, "-")
        c.drawString(margin_left + 3.5*cm, y - 0.7*cm, "-")
        c.drawString(margin_left + 7*cm, y - 0.7*cm, "-")
        
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "PIS")
        c.drawString(margin_left + 3.5*cm, y - 0.3*cm, "COFINS")
        c.drawString(margin_left + 7*cm, y - 0.3*cm, "Retenção do PIS/COFINS")
        c.drawString(margin_left + 12*cm, y - 0.3*cm, "TOTAL TRIBUTAÇÃO FEDERAL")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        pis = self.tributos_federais['pis']
        cofins = self.tributos_federais['cofins']
        total_federal = pis + cofins
        c.drawString(margin_left, y - 0.7*cm, self._formatar_moeda(pis))
        c.drawString(margin_left + 3.5*cm, y - 0.7*cm, self._formatar_moeda(cofins))
        c.drawString(margin_left + 7*cm, y - 0.7*cm, "Não Retido")
        c.drawString(margin_left + 12*cm, y - 0.7*cm, self._formatar_moeda(total_federal))
        
        y -= 1.2*cm
        
        # =====================================================================
        # VALOR TOTAL DA NFS-e
        # =====================================================================
        c.setStrokeColor(cinza_borda)
        c.line(margin_left, y, width - margin_right, y)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, y - 0.4*cm, "VALOR TOTAL DA NFS-E")
        
        y -= 0.6*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "Valor do Serviço")
        c.drawString(margin_left + 4*cm, y - 0.3*cm, "Desconto Condicionado")
        c.drawString(margin_left + 8*cm, y - 0.3*cm, "Desconto Incondicionado")
        c.drawString(margin_left + 12.5*cm, y - 0.3*cm, "ISSQN Retido")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, self._formatar_moeda(self.valores['valor_servico']))
        c.drawString(margin_left + 4*cm, y - 0.7*cm, "R$")
        c.drawString(margin_left + 8*cm, y - 0.7*cm, "R$")
        c.drawString(margin_left + 12.5*cm, y - 0.7*cm, "-")
        
        y -= 1*cm
        c.setFont("Helvetica", 7)
        c.setFillColor(colors.grey)
        c.drawString(margin_left, y - 0.3*cm, "IRRF, CP,CSLL - Retidos")
        c.drawString(margin_left + 4*cm, y - 0.3*cm, "PIS/COFINS Retidos")
        c.drawString(margin_left + 12.5*cm, y - 0.3*cm, "Valor Líquido da NFS-e")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.7*cm, "R$ 0,00")
        c.drawString(margin_left + 4*cm, y - 0.7*cm, "-")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin_left + 12.5*cm, y - 0.7*cm, self._formatar_moeda(self.valores['valor_liquido']))
        
        y -= 1.2*cm
        
        # =====================================================================
        # TOTAIS APROXIMADOS DOS TRIBUTOS
        # =====================================================================
        c.setStrokeColor(cinza_borda)
        c.line(margin_left, y, width - margin_right, y)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, y - 0.4*cm, "TOTAIS APROXIMADOS DOS TRIBUTOS")
        
        y -= 0.6*cm
        # Calcular percentuais aproximados
        valor = float(self.valores['valor_servico'])
        perc_federal = 4.65  # PIS + COFINS + outros
        perc_estadual = 0.00
        perc_municipal = float(self.valores['aliquota_iss'])
        
        c.setFont("Helvetica", 9)
        c.drawCentredString(margin_left + 3*cm, y - 0.3*cm, "Federais")
        c.drawCentredString(width/2, y - 0.3*cm, "Estaduais")
        c.drawCentredString(width - margin_right - 3*cm, y - 0.3*cm, "Municipais")
        
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(margin_left + 3*cm, y - 0.7*cm, f"{perc_federal:.2f} %")
        c.drawCentredString(width/2, y - 0.7*cm, f"{perc_estadual:.2f} %")
        c.drawCentredString(width - margin_right - 3*cm, y - 0.7*cm, f"{perc_municipal:.2f} %")
        
        y -= 1.2*cm
        
        # =====================================================================
        # INFORMAÇÕES COMPLEMENTARES
        # =====================================================================
        c.setStrokeColor(cinza_borda)
        c.line(margin_left, y, width - margin_right, y)
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(margin_left, y - 0.4*cm, "INFORMAÇÕES COMPLEMENTARES")
        
        y -= 0.6*cm
        c.setFont("Helvetica", 9)
        c.drawString(margin_left, y - 0.3*cm, f"NBS: {self.servico['nbs']}")
        
        # Salvar PDF
        c.save()
        
        return True


def gerar_danfse_tubarao(dados_nfse: dict, output_path: str = None) -> str:
    """
    Gera DANFSE no padrão Tubarão/SC.
    
    Args:
        dados_nfse: Dicionário com dados da NFS-e
        output_path: Caminho de saída (opcional)
    
    Returns:
        Caminho do PDF gerado
    """
    if output_path is None:
        volume_path = os.getenv('RAILWAY_VOLUME_MOUNT_PATH', './data')
        pdf_dir = Path(volume_path) / "outputs" / "pdf"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        
        chave = dados_nfse.get('chave_acesso', 'nfse')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = str(pdf_dir / f"danfse_{chave[-10:]}_{timestamp}.pdf")
    
    gerador = GeradorDANFSETubarao(dados_nfse=dados_nfse)
    gerador.gerar_pdf(output_path)
    
    return output_path


if __name__ == "__main__":
    # Teste com dados de exemplo
    dados_teste = {
        'chave_acesso': '42187072258645846000169000010000000000132601038252168',
        'numero': '13',
        'numero_dps': '25',
        'serie_dps': '900',
        'competencia': '02/01/2026',
        'data_emissao': '02/01/2026 16:30:22',
        'tomador_cpf': '318.054.788-00',
        'tomador_nome': 'THAINA PIRES',
        'valor': '89.00',
        'aliquota_iss': '3.00',
        'descricao_servico': 'teleconsulta',
    }
    
    output = gerar_danfse_tubarao(dados_teste, 'teste_danfse_tubarao.pdf')
    print(f"PDF gerado: {output}")

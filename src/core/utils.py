import pandas as pd
import unicodedata
import re
from datetime import datetime
from config.settings import settings
from src.core.logger import logger

def sanitize_text(text):
    """
    Limpa caracteres especiais e normaliza unicode para evitar erros no xhtml2pdf.
    """
    if pd.isna(text) or text == "" or text is None:
        return ""
    
    text = str(text)
    
    # Normalização NFKC (compatibilidade) converte caracteres "exóticos" em seus equivalentes padrão
    normalized = unicodedata.normalize('NFKC', text)
    
    # Mantém caracteres imprimíveis e remove controles que quebram o PDF
    clean = "".join(ch for ch in normalized if unicodedata.category(ch)[0] != "C")
    
    return clean.strip()

def format_currency(val):
    try:
        if pd.isna(val) or str(val).strip() == "": return "R$ 0,00"
        val_str = str(val).strip()
        
        if ',' in val_str and '.' in val_str: 
            clean = val_str.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        elif ',' in val_str: 
            clean = val_str.replace('R$', '').replace(' ', '').replace(',', '.')
        else: 
            clean = val_str.replace('R$', '').strip()
            
        return f"R$ {float(clean):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception as e:
        logger.warning(f"Erro ao formatar moeda '{val}': {e}")
        return str(val)

def parse_currency(val):
    """Converte string de moeda para float para cálculos."""
    try:
        if pd.isna(val): return 0.0
        s = str(val).strip().replace("R$", "").strip()
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            s = s.replace(",", ".")
        return float(s)
    except Exception as e:
        logger.warning(f"Erro ao fazer parse de moeda '{val}': {e}")
        return 0.0

def mask_cpf_cnpj(val):
    """
    Mascaramento de CPF/CNPJ seguindo melhores práticas:
    CPF: ***.***.123-45
    CNPJ: **.***.***/0001-**
    """
    if not val or pd.isna(val):
        return val
    
    clean_val = re.sub(r'\D', '', str(val))
    
    if len(clean_val) == 11:  # CPF
        # Formato: ***.***.890-12
        return f"***.***.{clean_val[6:9]}-{clean_val[9:]}"
    elif len(clean_val) == 14:  # CNPJ
        # Formato: **.***.678/0001-**
        return f"**.***.{clean_val[5:8]}/{clean_val[8:12]}-**"
    
    return val

def mask_name(name, doc=None):
    """
    Mascaramento de Nome:
    - Se for PJ (CNPJ detectado no doc), NÃO mascara a Razão Social (dado público).
    - Se for PF (CPF ou sem doc), mantém o primeiro nome e masca o restante.
    Ex: Stefan Pratti -> Stefan **********
    """
    if not name or pd.isna(name) or not isinstance(name, str):
        return name
    
    # Se forneceu documento e ele parece um CNPJ (14 dígitos), retorna nome completo
    if doc and pd.notna(doc):
        clean_doc = re.sub(r'\D', '', str(doc))
        if len(clean_doc) == 14:
            return name
    
    parts = name.strip().split()
    if len(parts) <= 1:
        return name
    
    first_name = parts[0]
    masked_rest = " ".join(["*" * len(p) for p in parts[1:]])
    return f"{first_name} {masked_rest}"

def clean_filename_text(text):
    if not isinstance(text, str): return ""
    try:
        norm = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        return re.sub(r'[^\w\s-]', '', norm).strip().replace(' ', '_').upper()
    except Exception as e:
        logger.error(f"Erro ao limpar texto para nome de arquivo '{text}': {e}")
        return ""

def validate_columns(df):
    """Verifica se as colunas necessárias existem no DataFrame."""
    missing = []
    columns_present = df.columns.tolist()
    
    for friendly_name, options in settings.REQUIRED_FIELDS:
        if not any(opt in columns_present for opt in options):
            missing.append(f"{friendly_name} (Colunas aceitas: {', '.join(options)})")
    
    if missing:
        logger.warning(f"Colunas ausentes na validação: {missing}")
            
    return missing

def prepare_context(row, mask_data=False):
    """
    Prepara o dicionário de contexto para o Jinja2 e Preview.
    """
    def get(keys, default=""):
        for key in keys:
            if key in row.index and pd.notna(row[key]):
                raw_val = str(row[key]).replace('\n', ' ')
                return sanitize_text(raw_val)
        return default

    # Mapeamento
    # Endereço: tenta Endereço avulso, se não existir usa Endereço Consórcio (modelo GD Gestão)
    endereco_raw = get(['Endereço', 'Endereco'])
    if not endereco_raw:
        endereco_raw = get(['Endereço Consórcio', 'Endereco Consorcio'])
    
    # Cidade + UF: monta sufixo só se existirem
    cidade = get(['Cidade'])
    uf = get(['UF'])
    if cidade and uf:
        endereco_completo = f"{endereco_raw}, {cidade} - {uf}"
    elif uf:
        endereco_completo = f"{endereco_raw} - {uf}" if endereco_raw else f"- {uf}"
    else:
        endereco_completo = endereco_raw

    data_em_raw = get(['Data de Emissão', 'Data Emissao'])
    if not data_em_raw:
        data_em_raw = datetime.now().strftime("%d/%m/%Y")

    ctx = {
        "nome_consorcio": get(['Nome Consórcio', 'Nome Consorcio']),
        "endereco_consorcio": get(['Endereço Consórcio', 'Endereco Consorcio']),
        "cnpj_consorcio": get(['CNPJ Consórcio', 'CNPJ Consorcio']),
        "razao_social": get(['Nome', 'Razão Social', 'Razao Social', 'Cliente']),
        "endereco_consorciado": endereco_completo,
        "cnpj_consorciado": get(['CNPJ/CPF', 'CNPJ', 'CPF']),
        "numero_conta": get(['Número da conta', 'Numero da conta', 'Conta vinculada']),
        "numero_cobranca": get(['Nº da cobrança', 'N da cobranca']),
        "numero_instalacao": get(['Instalação', 'Instalacao', 'Numero Instalacao', 'Num. Instalação']),
        "data_emissao": data_em_raw,
        "data_vencimento": get(['Vencimento', 'Data Vencimento']),
        "mes_referencia": get(['Mês de Referência', 'Mes Referencia', 'Referencia']),
        "total_pagar": format_currency(get(['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Valor emitido', 'Total'], '0')),
        "economia_mes": format_currency(get(['Economia R$', 'Economia mês', 'ECONOMIA'], '0')),
        
        # Tenta buscar por nome de coluna primeiro; aceita também Número da conta como alias
        "dados_bancarios": get(['Dados bancários', 'Dados bancarios', 'Pagamento', 'Número da conta', 'Numero da conta'], '')
    }

    # Aplica mascaramento se solicitado (Melhores Práticas LGPD)
    # Aplica mascaramento se solicitado (Melhores Práticas LGPD)
    if mask_data:
        # Armazena doc original para validação
        raw_doc = ctx["cnpj_consorciado"]
        
        # Passa o documento para decidir se mascara o nome (PJ vs PF)
        ctx["razao_social"] = mask_name(ctx["razao_social"], doc=raw_doc)
        
        # O documento em si continua sendo mascarado parcialmente para segurança visual
        ctx["cnpj_consorciado"] = mask_cpf_cnpj(raw_doc)
        # Endereço também pode conter dados sensíveis, mas manteremos por agora para identificação básica
        # Se necessário, poderíamos mascarar o número.
    
    # FALLBACK INTELIGENTE: Se não achou por nome, tenta pelo índice 29 (Coluna AD)
    if not ctx["dados_bancarios"] or ctx["dados_bancarios"] == "Não Informado":
        if len(row) > 29:
            # Pega o valor da 30ª coluna (índice 29)
            valor_ad = row.iloc[29]
            if pd.notna(valor_ad):
                ctx["dados_bancarios"] = sanitize_text(str(valor_ad))
    
    # FALLBACK INSTALAÇÃO: Coluna A (Índice 0) se não achou por nome
    if not ctx["numero_instalacao"]:
        if len(row) > 0:
            val_0 = row.iloc[0]
            if pd.notna(val_0):
                ctx["numero_instalacao"] = sanitize_text(str(val_0))
                
    # Se ainda assim estiver vazio, coloca o padrão
    if not ctx["dados_bancarios"]:
        ctx["dados_bancarios"] = "Não Informado"
    
    ctx["_raw_total"] = parse_currency(get(['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Valor emitido', 'Total'], '0'))
    
    return ctx

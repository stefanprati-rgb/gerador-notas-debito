import pandas as pd
import unicodedata
import re

# ==========================================
# UTILITÁRIOS DE DADOS E FORMATAÇÃO
# ==========================================

# Mapeamento de campos essenciais para validação
# (Nome Amigável, Lista de Colunas Aceitas)
REQUIRED_FIELDS = [
    ("Nome/Razão Social", ['Nome', 'Razão Social', 'Cliente']),
    ("Endereço", ['Endereço', 'Endereco']),
    ("Cidade", ['Cidade']),
    ("UF", ['UF']),
    ("CNPJ/CPF", ['CNPJ/CPF', 'CNPJ', 'CPF']),
    ("Conta", ['Número da conta', 'Numero da conta', 'Conta vinculada']),
    ("Vencimento", ['Vencimento', 'Data Vencimento']),
    ("Referência", ['Mês de Referência', 'Mes Referencia']),
    # ("Instalação", ['Instalação', 'Instalacao', 'Numero Instalacao', 'Num. Instalação']), # Opcional / Fallback Index 0
    ("Total a Pagar", ['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Total']),
    ("Dados Bancários", ['Dados bancários', 'Dados bancarios', 'Pagamento']) # ADICIONADO PARA COLUNA AD
]

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
    except:
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
    except:
        return 0.0

def clean_filename_text(text):
    if not isinstance(text, str): return ""
    try:
        norm = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        return re.sub(r'[^\w\s-]', '', norm).strip().replace(' ', '_').upper()
    except: return ""

def validate_columns(df):
    """Verifica se as colunas necessárias existem no DataFrame."""
    missing = []
    columns_present = df.columns.tolist()
    
    for friendly_name, options in REQUIRED_FIELDS:
        if not any(opt in columns_present for opt in options):
            missing.append(f"{friendly_name} (Colunas aceitas: {', '.join(options)})")
            
    return missing

def prepare_context(row):
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
    ctx = {
        "nome_consorcio": get(['Nome Consórcio', 'Nome Consorcio'], 'HUBE ENERGY'),
        "endereco_consorcio": get(['Endereço Consórcio', 'Endereco Consorcio']),
        "cnpj_consorcio": get(['CNPJ Consórcio', 'CNPJ Consorcio']),
        "razao_social": get(['Nome', 'Razão Social', 'Cliente']),
        "endereco_consorciado": f"{get(['Endereço','Endereco'])}, {get(['Cidade'])} - {get(['UF'])}",
        "cnpj_consorciado": get(['CNPJ/CPF', 'CNPJ', 'CPF']),
        "numero_conta": get(['Número da conta', 'Numero da conta', 'Conta vinculada']),
        "numero_cobranca": get(['Nº da cobrança', 'N da cobranca']),
        "numero_instalacao": get(['Instalação', 'Instalacao', 'Numero Instalacao', 'Num. Instalação']),
        "data_emissao": get(['Data de Emissão', 'Data Emissao']),
        "data_vencimento": get(['Vencimento', 'Data Vencimento']),
        "mes_referencia": get(['Mês de Referência', 'Mes Referencia']),
        "total_pagar": format_currency(get(['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Total'], '0')),
        "economia_mes": format_currency(get(['Economia R$', 'Economia mês'], '0')),
        
        # Tenta buscar por nome primeiro
        "dados_bancarios": get(['Dados bancários', 'Dados bancarios', 'Pagamento'], '')
    }
    
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
    
    ctx["_raw_total"] = parse_currency(get(['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Total'], '0'))
    
    return ctx

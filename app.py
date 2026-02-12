import streamlit as st
import pandas as pd
from xhtml2pdf import pisa
from io import BytesIO
import zipfile
from datetime import datetime
from jinja2 import Template
import unicodedata
import re

# ==========================================
# CONFIGURAÇÃO VISUAL
# ==========================================
st.set_page_config(page_title="Hube Emissor", layout="centered", page_icon="⚡")

st.markdown("""
<style>
    .stButton>button { width: 100%; font-weight: bold; font-size: 18px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# TEMPLATE HTML (CABEÇALHO LIMPO - SEM QUADRADOS)
# ==========================================
def get_html_template():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 1cm;
        }
        body {
            font-family: Helvetica, Arial, sans-serif;
            font-size: 9pt;
            color: #000;
            line-height: 1.2;
        }
        
        /* ESTRUTURA FIXA */
        table { 
            width: 100%; 
            border-collapse: collapse; 
            table-layout: fixed; 
        }
        
        td { 
            vertical-align: top; 
            padding: 4px; 
            word-wrap: break-word;
        }
        
        /* Textos */
        .header-title {
            font-size: 14pt;
            font-weight: bold;
            text-transform: uppercase;
            text-align: right;
            margin-bottom: 10px;
        }
        
        .label {
            font-size: 7pt;
            font-weight: bold;
            text-transform: uppercase;
            color: #444;
            display: block; 
        }
        
        .value {
            font-size: 9pt;
            font-weight: bold;
            color: #000;
            display: block;
            margin-bottom: 5px; 
        }

        /* Caixa Principal (Destinatário) */
        .main-box {
            border: 1px solid #000;
            margin-top: 5px;
            margin-bottom: 15px;
        }

        /* Tabelas Internas */
        .items-header th {
            border-top: 1px solid #000;
            border-bottom: 1px solid #000;
            text-align: left;
            padding: 4px;
            font-size: 8pt;
            background-color: #f2f2f2;
        }
        .item-row td {
            padding-top: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid #eee;
        }
        
        /* Total */
        .total-row td {
            border-top: 2px solid #000;
            border-bottom: 1px solid #000;
            font-weight: bold;
            background-color: #f2f2f2;
            padding: 6px;
            font-size: 10pt;
        }
        
        .text-right { text-align: right; }
        
    </style>
</head>
<body>

    <table>
        <tr>
            <td width="55%">
                <div style="font-size: 11pt; font-weight: bold; text-transform: uppercase;">{{ nome_consorcio }}</div>
                <div style="margin-top: 4px;">{{ endereco_consorcio }}</div>
                <div>CNPJ: {{ cnpj_consorcio }}</div>
            </td>
            
            <td width="45%" class="text-right">
                <div class="header-title">Aviso de Débito</div>
                
                <div style="margin-top: 5px;">
                    <span class="label">Número da Conta</span>
                    <span class="value">{{ numero_conta }}</span>
                </div>
                <div style="margin-top: 5px;">
                    <span class="label">Nº da Cobrança</span>
                    <span class="value">{{ numero_cobranca }}</span>
                </div>
            </td>
        </tr>
    </table>

    <div class="main-box">
        <table cellpadding="0" cellspacing="0">
            <tr>
                <td width="60%" style="border-right: 1px solid #000; padding: 8px;">
                    
                    <div style="border-bottom: 1px dashed #ccc; padding-bottom: 6px; margin-bottom: 6px;">
                        <span class="label">Natureza da Operação:</span> <span>Locação de Equipamentos</span><br>
                        <span class="label">Código:</span> <span>98569</span>
                    </div>

                    <div>
                        <span class="label">DESTINATÁRIO (CONSORCIADO)</span>
                        <div class="value" style="font-size: 10pt;">{{ razao_social }}</div>
                        <div style="font-size: 9pt;">{{ endereco_consorciado }}</div>
                        <div style="font-size: 9pt;">CNPJ/CPF: {{ cnpj_consorciado }}</div>
                    </div>
                </td>

                <td width="40%" style="padding: 8px;">
                    <div style="margin-bottom: 8px;">
                        <span class="label">Data Emissão</span>
                        <span class="value">{{ data_emissao }}</span>
                    </div>
                    
                    <div style="margin-bottom: 8px;">
                        <span class="label">Vencimento</span>
                        <span class="value" style="font-size: 11pt; color: #cc0000;">{{ data_vencimento }}</span>
                    </div>
                    
                    <div>
                        <span class="label">Referência</span>
                        <span class="value">{{ mes_referencia }}</span>
                    </div>
                </td>
            </tr>
        </table>
    </div>

    <table>
        <thead class="items-header">
            <tr>
                <th width="75%">DISCRIMINAÇÃO DOS SERVIÇOS</th>
                <th width="25%" class="text-right">TOTAL</th>
            </tr>
        </thead>
        <tbody>
            <tr class="item-row">
                <td>
                    <b>SERVIÇO LOC. OUTR. MÁQ. EQUIP. PLAC. FOTOVOLT.</b><br>
                    <span style="font-size: 8pt; color: #666;"><b>Conta para Depósito: {{ numero_conta }}</b></span><br>
                    <span style="font-size: 8pt; color: #666;">Economia Gerada: {{ economia_mes }}</span>
                </td>
                <td class="text-right value">{{ total_pagar }}</td>
            </tr>
             <tr><td colspan="2" style="height: 20px;"></td></tr>
        </tbody>
    </table>

    <table style="margin-bottom: 20px;">
        <tr class="total-row">
            <td class="text-right" width="75%">TOTAL A PAGAR</td>
            <td class="text-right" width="25%">{{ total_pagar }}</td>
        </tr>
    </table>

    <div style="border: 1px solid #ccc; background-color: #f9f9f9; padding: 10px;">
        <div class="label" style="color: #000; border-bottom: 1px solid #ccc; margin-bottom: 5px; padding-bottom: 2px;">Número da Conta</div>
        <div style="font-family: monospace; font-size: 12pt; font-weight: bold; color: #000;">{{ numero_conta }}</div>
        
        <div style="margin-top: 8px; font-size: 7pt; color: #666;">
            * Caso o pagamento não seja efetuado até o vencimento, incidirá multa e juros conforme contrato.
        </div>
    </div>

</body>
</html>
"""

# ==========================================
# LÓGICA DE DADOS
# ==========================================

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

def clean_filename_text(text):
    if not isinstance(text, str): return ""
    try:
        norm = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        return re.sub(r'[^\w\s-]', '', norm).strip().replace(' ', '_').upper()
    except: return ""

def prepare_context(row):
    def get(keys, default=""):
        for key in keys:
            if key in row.index and pd.notna(row[key]):
                return str(row[key]).strip().replace('\n', ' ')
        return default

    # Mapeamento
    return {
        "nome_consorcio": get(['Nome Consórcio', 'Nome Consorcio'], 'HUBE ENERGY'),
        "endereco_consorcio": get(['Endereço Consórcio', 'Endereco Consorcio']),
        "cnpj_consorcio": get(['CNPJ Consórcio', 'CNPJ Consorcio']),
        "razao_social": get(['Nome', 'Razão Social', 'Cliente']),
        "endereco_consorciado": f"{get(['Endereço','Endereco'])}, {get(['Cidade'])} - {get(['UF'])}",
        "cnpj_consorciado": get(['CNPJ/CPF', 'CNPJ', 'CPF']),
        "numero_conta": get(['Número da conta', 'Numero da conta', 'Conta vinculada']),
        "numero_cobranca": get(['Nº da cobrança', 'N da cobranca']),
        "data_emissao": get(['Data de Emissão', 'Data Emissao']),
        "data_vencimento": get(['Vencimento', 'Data Vencimento']),
        "mes_referencia": get(['Mês de Referência', 'Mes Referencia']),
        "total_pagar": format_currency(get(['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Total'], '0')),
        "economia_mes": format_currency(get(['Economia R$', 'Economia mês'], '0')),
        "dados_bancarios": get(['Dados bancários', 'Dados bancarios'], '')
    }

def generate_pdf(html):
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if pisa_status.err: return None, f"Erro layout: {pisa_status.err}"
    return buffer.getvalue(), None

# ==========================================
# UI
# ==========================================
st.title("⚡ Hube | Gerador de Notas")
st.info("Layout Ajustado: Cabeçalho limpo (sem quadrados).")

uploaded_file = st.file_uploader("Upload da Base (.xlsx ou .csv)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
            
        st.write(f"📊 Registros identificados: **{len(df)}**")
        
        if st.button("Gerar Notas", type="primary"):
            zip_buffer = BytesIO()
            erros = []
            sucesso = 0
            bar = st.progress(0)
            
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zf:
                for i, row in df.iterrows():
                    try:
                        ctx = prepare_context(row)
                        html = Template(get_html_template()).render(ctx)
                        pdf, err = generate_pdf(html)
                        
                        if pdf:
                            nome = clean_filename_text(ctx['razao_social'])[:25]
                            venc = clean_filename_text(ctx['data_vencimento']).replace('/','-')
                            raw_id = clean_filename_text(ctx['numero_cobranca'])
                            id_unico = raw_id[-8:] if raw_id else f"L{i+1}"
                            
                            filename = f"NOTA_{nome}_{venc}_{id_unico}.pdf"
                            zf.writestr(filename, pdf)
                            sucesso += 1
                        else:
                            erros.append(f"Linha {i+2}: {err}")
                    except Exception as e:
                        erros.append(f"Linha {i+2}: {str(e)}")
                    bar.progress((i+1)/len(df))
            
            zip_buffer.seek(0)
            
            if erros:
                st.error(f"⚠️ {len(erros)} erros encontrados.")
                with st.expander("Ver Relatório de Erros"):
                    st.write(erros)
            
            if sucesso > 0:
                st.balloons()
                st.download_button(
                    label=f"📥 Baixar {sucesso} Notas (.zip)",
                    data=zip_buffer,
                    file_name=f"Notas_Hube_{datetime.now().strftime('%d%m_%H%M')}.zip",
                    mime="application/zip"
                )
            
    except Exception as e:
        st.error(f"Erro no arquivo: {e}")
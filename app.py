import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
from datetime import datetime
from jinja2 import Template

# Importando módulos refatorados
from utils import (
    sanitize_text,
    format_currency,
    parse_currency,
    clean_filename_text,
    validate_columns,
    prepare_context,
    REQUIRED_FIELDS
)
from pdf_engine import get_html_template, generate_pdf

# ==========================================
# CONFIGURAÇÃO VISUAL
# ==========================================
st.set_page_config(page_title="Hube Emissor", layout="centered", page_icon="⚡")

# ==========================================
# 🔒 SISTEMA DE LOGIN SEGURO
# ==========================================
def check_password():
    """Retorna True se o login for bem-sucedido."""

    # 1. Verifica se já está logado na sessão
    if st.session_state.get("password_correct", False):
        return True

    # 2. Interface de Login
    st.markdown("### 🔒 Acesso Restrito - Hube Energy")
    
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        # Busca as credenciais no "Cofre" (Secrets)
        # O formato esperado no cofre é: [passwords] usuario = "senha"
        
        try:
            secrets_pass = st.secrets["passwords"]
            
            # Verifica se usuario existe e senha bate
            if usuario in secrets_pass and secrets_pass[usuario] == senha:
                st.session_state["password_correct"] = True
                st.success("Logado com sucesso!")
                st.rerun() # Recarrega a página para mostrar o app
            else:
                st.error("Usuário ou senha incorretos.")
        except Exception:
            st.warning("⚠️ O sistema de senhas não foi configurado no servidor.")
            
    return False

# 🛑 BARREIRA DE SEGURANÇA
# Se não estiver logado, o script PARA aqui e não mostra nada abaixo.
if not check_password():
    st.stop()

st.markdown("""
<style>
    .stButton>button { width: 100%; font-weight: bold; font-size: 18px; padding: 15px; }
    .reportview-container .main .block-container { max_width: 1000px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# UI & FLOW PRINCIPAL
# ==========================================
st.title("⚡ Hube | Gerador de Notas")

uploaded_file = st.file_uploader("Upload da Base (.xlsx ou .csv)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Carregamento
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
            
        # 1. Validação de Colunas (UX Robusta)
        missing_cols = validate_columns(df)
        if missing_cols:
            st.error("❌ A planilha enviada não possui todas as colunas necessárias:")
            for m in missing_cols:
                st.markdown(f"- {m}")
            st.warning("Corrija o arquivo e faça o upload novamente.")
            st.stop() # Interrompe execução

        st.success("✅ Estrutura do arquivo validada com sucesso!")

        # 2. Resumo Financeiro (Conferência)
        # Vamos calcular o total baseado no parsing da coluna 'Total a pagar' (ou similar)
        # Identifica qual coluna de total existe
        col_total = next((c for c in ['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Total'] if c in df.columns), None)
        
        total_consolidado = 0.0
        if col_total:
            def safe_float(x):
                # Limpa R$, espaços, etc
                return parse_currency(str(x))
            
            # Usando apply com a função robusta
            total_consolidado = df[col_total].apply(safe_float).sum()
        
        col1, col2 = st.columns(2)
        col1.metric("Registros", len(df))
        col2.metric("Valor Total Consolidado", f"R$ {total_consolidado:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # 3. Data Preview (Transformado)
        st.subheader("🔍 Pré-visualização dos Dados (Formatados)")
        st.caption("Abaixo estão os 5 primeiros registros como aparecerão no PDF (Texto limpo e Moeda formatada).")
        
        # Gera preview aplicando prepare_context nos 5 primeiros
        preview_rows = []
        for _, row in df.head(5).iterrows():
            ctx = prepare_context(row)
            # Remove chaves internas se houver
            clean_ctx = {k: v for k, v in ctx.items() if k != "_raw_total"}
            preview_rows.append(clean_ctx)
        
        st.dataframe(pd.DataFrame(preview_rows))

        # 4. Geração
        st.write("---")
        # Se houver preview, o usuário vê e decide clicar
        if st.button("Gerar Notas", type="primary"):
            zip_buffer = BytesIO()
            erros = []
            sucesso = 0
            bar = st.progress(0)
            status_text = st.empty()
            
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zf:
                total_rows = len(df)
                for i, row in df.iterrows():
                    status_text.text(f"Processando {i+1}/{total_rows}...")
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
                            erros.append(f"Linha {i+2} ({ctx.get('razao_social', 'Sem Nome')}): {err}")
                    except Exception as e:
                        erros.append(f"Linha {i+2}: {str(e)}")
                    
                    bar.progress((i+1)/total_rows)
            
            status_text.empty()
            bar.empty()
            zip_buffer.seek(0)
            
            if erros:
                st.error(f"⚠️ {len(erros)} erros encontrados durante a geração.")
                with st.expander("Ver Relatório de Erros Detalhado"):
                    for e in erros:
                        st.write(e)
            
            if sucesso > 0:
                st.balloons()
                st.success(f"🎉 {sucesso} notas geradas com sucesso!")
                st.download_button(
                    label=f"📥 Baixar {sucesso} Notas (.zip)",
                    data=zip_buffer,
                    file_name=f"Notas_Hube_{datetime.now().strftime('%d%m_%H%M')}.zip",
                    mime="application/zip"
                )
            
    except Exception as e:
        st.error(f"Erro fatal ao processar arquivo: {e}")
import streamlit as st
import pandas as pd
from datetime import datetime, date
from jinja2 import Template

# Importando módulos refatorados
from src.core.utils import (
    sanitize_text,
    format_currency,
    parse_currency,
    clean_filename_text,
    validate_columns,
    prepare_context,
    find_column_in_df,
    parse_date
)
from src.core.date_handler import check_expiration_column, apply_date_replacement
from src.services.zip_builder import generate_notes_zip
from src.services.pdf_engine import get_html_template, list_templates
from src.core.logger import logger
from config.settings import settings

# ==========================================
# CONFIGURAÇÃO VISUAL
# ==========================================
st.set_page_config(page_title=settings.APP_NAME, layout="centered", page_icon="⚡")

# ==========================================
# 🔒 SISTEMA DE LOGIN SEGURO
# ==========================================
def check_password():
    """Retorna True se o login for bem-sucedido."""
    if st.session_state.get("password_correct", False):
        return True

    st.markdown("### 🔒 Acesso Restrito - Hube Energy")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        try:
            secrets_pass = st.secrets.get("passwords", {})
            if usuario in secrets_pass and secrets_pass[usuario] == senha:
                st.session_state["password_correct"] = True
                logger.info(f"Login bem-sucedido para usuário: {usuario}")
                st.success("Logado com sucesso!")
                st.rerun()
            else:
                logger.warning(f"Tentativa de login falha para usuário: {usuario}")
                st.error("Usuário ou senha incorretos.")
        except Exception as e:
            logger.error(f"Erro ao acessar secrets ou validar senha: {e}")
            st.warning("⚠️ O sistema de senhas não foi configurado no servidor.")
            
    return False

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
st.title(f"⚡ {settings.APP_NAME} | Gerador de Notas")

uploaded_file = st.file_uploader("Upload da Base (.xlsx ou .csv)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        logger.info(f"Arquivo carregado: {uploaded_file.name}")
        
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)
            
        missing_cols = validate_columns(df)
        if missing_cols:
            st.error("❌ A planilha enviada não possui todas as colunas necessárias:")
            for m in missing_cols:
                st.markdown(f"- {m}")
            st.warning("Corrija o arquivo e faça o upload novamente.")
            st.stop()

        st.success("✅ Estrutura do arquivo validada com sucesso!")

        # 1. Validação de Vencimento
        col_vencimento = find_column_in_df(df, ['Vencimento', 'Data Vencimento'])
        hoje = date.today()

        if not col_vencimento:
            st.warning("⚠️ A planilha não possui coluna de **Vencimento**.")
            venc_input = st.date_input("Informe a data de vencimento:", value=None, format="DD/MM/YYYY")
            if venc_input:
                df['Vencimento'] = venc_input.strftime('%d/%m/%Y')
                st.info(f"📅 Vencimento definido para todas as notas: **{venc_input.strftime('%d/%m/%Y')}**")
        else:
            linhas_expiradas = check_expiration_column(df, col_vencimento)
            if linhas_expiradas:
                st.warning(f"⚠️ **{len(linhas_expiradas)}** nota(s) possuem data de vencimento já expirada:")
                st.dataframe(pd.DataFrame(linhas_expiradas), use_container_width=True, hide_index=True)

                opcao = st.radio("Deseja substituir as datas expiradas?", 
                                 ["Manter originais", "Substituir por nova data"], horizontal=True)
                if opcao == "Substituir por nova data":
                    nova_data = st.date_input("Nova data de vencimento:", value=hoje, format="DD/MM/YYYY")
                    df = apply_date_replacement(df, col_vencimento, linhas_expiradas, nova_data)
                    st.info(f"📅 Datas substituídas para: **{nova_data.strftime('%d/%m/%Y')}**")

        # 2. Resumo Financeiro
        col_total = find_column_in_df(df, ['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Valor emitido', 'Total'])
        total_consolidado = df[col_total].apply(parse_currency).sum() if col_total else 0.0
        
        c1, c2 = st.columns(2)
        c1.metric("Registros", len(df))
        c2.metric("Valor Total", format_currency(total_consolidado))

        # 3. Proteção LGPD & Preview
        st.write("---")
        ativar_lgpd = st.toggle("Ativar Mascaramento (LGPD)", value=True)
        
        st.subheader("🔍 Pré-visualização")
        preview = [prepare_context(row, mask_data=ativar_lgpd) for _, row in df.head(5).iterrows()]
        st.dataframe(pd.DataFrame(preview).drop(columns=['_raw_total'], errors='ignore'))

        # 4. Geração em Lote
        st.write("---")
        templates = list_templates()
        if not templates:
             st.error("Nenhum template encontrado na pasta templates/!")
             st.stop()
        
        template_escolhido = st.selectbox("Modelo de Nota", templates)

        if st.button("Gerar Todas as Notas (ZIP)", type="primary"):
            html_str = get_html_template(template_escolhido)
            template_jinja = Template(html_str)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(current, total):
                progress_bar.progress(current / total)
                status_text.text(f"Processando {current}/{total}...")

            zip_buffer, relatorio, erros = generate_notes_zip(
                df, template_jinja, mask_data=ativar_lgpd, progress_callback=update_progress
            )
            
            status_text.empty()
            progress_bar.empty()
            
            if erros:
                st.error(f"⚠️ {len(erros)} erros encontrados.")
                with st.expander("Ver Erros"):
                    for e in erros: st.write(e)
            
            sucesso = sum(1 for r in relatorio if r['status'] == 'SUCESSO')
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
        logger.critical(f"Erro fatal: {e}")
        st.error(f"Erro fatal: {e}")

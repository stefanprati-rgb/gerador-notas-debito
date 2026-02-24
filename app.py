import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
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
    find_column_in_df
)
from src.services.pdf_engine import get_html_template, generate_pdf, list_templates
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
                logger.info(f"Login bem-sucedido para usuário: {usuario}")
                st.success("Logado com sucesso!")
                st.rerun() # Recarrega a página para mostrar o app
            else:
                logger.warning(f"Tentativa de login falha para usuário: {usuario}")
                st.error("Usuário ou senha incorretos.")
        except Exception as e:
            logger.error(f"Erro ao acessar secrets ou validar senha: {e}")
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
st.title(f"⚡ {settings.APP_NAME} | Gerador de Notas")

uploaded_file = st.file_uploader("Upload da Base (.xlsx ou .csv)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        logger.info(f"Arquivo carregado: {uploaded_file.name}")
        
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

        # 2a. Verificação de coluna Vencimento — se não existir, solicita ao usuário
        col_vencimento = find_column_in_df(df, ['Vencimento', 'Data Vencimento'])
        vencimento_manual = None

        def _parse_date(val):
            """Tenta converter string para date; retorna None se falhar."""
            for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d'):
                try:
                    return datetime.strptime(str(val).strip(), fmt).date()
                except Exception:
                    pass
            return None

        hoje = date.today()

        if not col_vencimento:
            # ── Caso B: data informada manualmente ──────────────────────────
            st.warning("⚠️ A planilha não possui coluna de **Vencimento**.")
            vencimento_manual = st.date_input(
                "Informe a data de vencimento (ou deixe em branco para seguir sem):",
                value=None,
                format="DD/MM/YYYY",
                help="Esta data será aplicada a todas as notas geradas"
            )
            if vencimento_manual:
                if vencimento_manual < hoje:
                    st.warning(f"⚠️ A data informada (**{vencimento_manual.strftime('%d/%m/%Y')}**) já passou!")
                    opcao_manual = st.radio(
                        "O que deseja fazer?",
                        ["Prosseguir assim mesmo", "Informar outra data"],
                        key="radio_venc_manual",
                        horizontal=True
                    )
                    if opcao_manual == "Informar outra data":
                        vencimento_manual = st.date_input(
                            "Nova data de vencimento:",
                            value=hoje,
                            format="DD/MM/YYYY",
                            key="nova_data_manual"
                        )
                df['Vencimento'] = vencimento_manual.strftime('%d/%m/%Y')
                st.info(f"📅 Vencimento definido para todas as notas: **{vencimento_manual.strftime('%d/%m/%Y')}**")
            else:
                st.info("ℹ️ Seguindo sem data de vencimento.")

        else:
            # ── Caso A: coluna presente — verificar linha a linha ────────────
            linhas_expiradas = []
            for idx, row in df.iterrows():
                val = row.get(col_vencimento, None)
                if pd.isna(val) or str(val).strip() == '':
                    continue
                d = _parse_date(val)
                if d and d < hoje:
                    nome_col = find_column_in_df(df, ['Nome', 'Razão Social', 'Razao Social', 'Cliente'])
                    razao = str(row[nome_col]) if nome_col else f"Linha {idx + 2}"
                    linhas_expiradas.append({
                        "Linha": idx + 2,
                        "Razão Social": razao,
                        "Vencimento": d.strftime('%d/%m/%Y')
                    })

            if linhas_expiradas:
                st.warning(f"⚠️ **{len(linhas_expiradas)}** nota(s) possuem data de vencimento já expirada:")
                st.dataframe(pd.DataFrame(linhas_expiradas), use_container_width=True, hide_index=True)

                opcao_col = st.radio(
                    "O que deseja fazer?",
                    ["Prosseguir com as datas originais", "Substituir datas expiradas por uma nova data"],
                    key="radio_venc_col",
                    horizontal=True
                )
                if opcao_col == "Substituir datas expiradas por uma nova data":
                    nova_data = st.date_input(
                        "Nova data de vencimento (será aplicada apenas às notas expiradas):",
                        value=hoje,
                        format="DD/MM/YYYY",
                        key="nova_data_col"
                    )
                    # Substitui apenas as linhas expiradas
                    indices_expirados = [r["Linha"] - 2 for r in linhas_expiradas]
                    df.loc[indices_expirados, col_vencimento] = nova_data.strftime('%d/%m/%Y')
                    st.info(f"📅 {len(linhas_expiradas)} data(s) substituída(s) para: **{nova_data.strftime('%d/%m/%Y')}**")

        # 2b. Resumo Financeiro (Conferência)
        # Vamos calcular o total baseado no parsing da coluna 'Total a pagar' (ou similar)
        # Identifica qual coluna de total existe
        col_total = find_column_in_df(df, ['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Valor emitido', 'Total'])
        
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

        # Opções de Proteção LGPD
        st.write("---")
        col_lgpd1, col_lgpd2 = st.columns([3, 1])
        with col_lgpd1:
            st.subheader("🛡️ Proteção de Dados (LGPD)")
        with col_lgpd2:
            ativar_lgpd = st.toggle("Ativar Mascaramento", value=True, help="Oculta parte dos nomes e documentos (CPF/CNPJ) para maior privacidade.")

        # 3. Data Preview (Transformado)
        st.subheader("🔍 Pré-visualização dos Dados")
        st.caption("Abaixo estão os 5 primeiros registros. Ative a 'Proteção de Dados' acima para ver o mascaramento.")
        
        # Gera preview aplicando prepare_context nos 5 primeiros
        preview_rows = []
        for _, row in df.head(5).iterrows():
            ctx = prepare_context(row, mask_data=ativar_lgpd)
            # Remove chaves internas se houver
            clean_ctx = {k: v for k, v in ctx.items() if k != "_raw_total"}
            preview_rows.append(clean_ctx)
        
        st.dataframe(pd.DataFrame(preview_rows))

        # 4. Geração
        st.write("---")

        # Seleção de Template
        templates_disponiveis = list_templates()
        if not templates_disponiveis:
             st.error("Nenhum template encontrado na pasta templates/!")
             st.stop()
        
        template_escolhido = st.selectbox("Modelo de Nota", templates_disponiveis)


        st.write("---")
        
        # 5. Geração em Lote


        # Se houver preview, o usuário vê e decide clicar
        if st.button("Gerar Todas as Notas (ZIP)", type="primary"):
            logger.info("Iniciando geração em lote...")
            html_template_string = get_html_template(template_escolhido)
            template_jinja = Template(html_template_string)

            zip_buffer = BytesIO()
            erros = []
            relatorio = []
            sucesso = 0
            bar = st.progress(0)
            status_text = st.empty()
            
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zf:
                total_rows = len(df)
                for i, row in df.iterrows():
                    status_text.text(f"Processando {i+1}/{total_rows}...")
                    
                    # Variáveis para Log
                    log_razao = "Desconhecido"
                    log_cobranca = "N/A"
                    
                    try:
                        ctx = prepare_context(row, mask_data=ativar_lgpd)
                        log_razao = ctx.get('razao_social', 'Desconhecido')
                        log_cobranca = ctx.get('numero_cobranca', 'N/A')

                        html = template_jinja.render(ctx)
                        pdf, err = generate_pdf(html)
                        
                        if pdf:
                            nome = clean_filename_text(ctx['razao_social'])[:25]
                            venc = clean_filename_text(ctx['data_vencimento']).replace('/','-')
                            raw_id = clean_filename_text(ctx['numero_cobranca'])
                            id_unico = raw_id[-8:] if raw_id else f"L{i+1}"
                            
                            filename = f"NOTA_{nome}_{venc}_{id_unico}.pdf"
                            zf.writestr(filename, pdf)
                            sucesso += 1
                            
                            relatorio.append({
                                "linha_planilha": i + 2,
                                "razao_social": log_razao,
                                "numero_cobranca": log_cobranca,
                                "status": "SUCESSO",
                                "mensagem_erro": "",
                                "nome_arquivo_pdf": filename
                            })
                        else:
                            msg_erro = f"Erro layout: {err}"
                            erros.append(f"Linha {i+2} ({log_razao}): {err}")
                            relatorio.append({
                                "linha_planilha": i + 2,
                                "razao_social": log_razao,
                                "numero_cobranca": log_cobranca,
                                "status": "ERRO",
                                "mensagem_erro": msg_erro,
                                "nome_arquivo_pdf": ""
                            })
                            logger.error(f"Erro na geração de PDF linha {i+2}: {msg_erro}")

                    except Exception as e:
                        msg_erro = str(e)
                        erros.append(f"Linha {i+2}: {msg_erro}")
                        relatorio.append({
                            "linha_planilha": i + 2,
                            "razao_social": log_razao,
                            "numero_cobranca": log_cobranca,
                            "status": "ERRO",
                            "mensagem_erro": msg_erro,
                            "nome_arquivo_pdf": ""
                        })
                        logger.exception(f"Exceção ao processar linha {i+2}: {msg_erro}")
                    
                    bar.progress((i+1)/total_rows)

                # Gera CSV de relatório e inclui no ZIP
                if relatorio:
                    csv_data = pd.DataFrame(relatorio).to_csv(index=False, sep=";", encoding="utf-8-sig")
                    zf.writestr("relatorio_processamento.csv", csv_data)
            
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
                logger.info(f"Geração concluída. Sucesso: {sucesso}, Erros: {len(erros)}")
                st.download_button(
                    label=f"📥 Baixar {sucesso} Notas (.zip)",
                    data=zip_buffer,
                    file_name=f"Notas_Hube_{datetime.now().strftime('%d%m_%H%M')}.zip",
                    mime="application/zip"
                )
            
    except Exception as e:
        logger.critical(f"Erro fatal ao processar arquivo: {e}")
        st.error(f"Erro fatal ao processar arquivo: {e}")

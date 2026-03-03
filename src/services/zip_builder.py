import zipfile
import pandas as pd
from io import BytesIO
from datetime import datetime
from jinja2 import Template
from typing import Callable, Optional
from src.core.utils import prepare_context, clean_filename_text
from src.services.pdf_engine import generate_pdf
from src.core.logger import logger

def generate_notes_zip(
    df: pd.DataFrame,
    template_jinja: Template,
    mask_data: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> tuple[BytesIO, list[dict], list[str]]:
    """
    Gera um buffer ZIP contendo os PDFs das notas e um relatório de processamento CSV.
    Retorna: (zip_buffer, relatorio, erros)
    """
    zip_buffer = BytesIO()
    erros = []
    relatorio = []
    sucesso = 0
    total_rows = len(df)
    
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zf:
        for i, row in df.iterrows():
            if progress_callback:
                progress_callback(i + 1, total_rows)
            
            # Variáveis para Log
            log_razao = "Desconhecido"
            log_cobranca = "N/A"
            
            try:
                ctx = prepare_context(row, mask_data=mask_data)
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

        # Gera CSV de relatório e inclui no ZIP
        if relatorio:
            csv_data = pd.DataFrame(relatorio).to_csv(index=False, sep=";", encoding="utf-8-sig")
            zf.writestr("relatorio_processamento.csv", csv_data)
            
    zip_buffer.seek(0)
    return zip_buffer, relatorio, erros

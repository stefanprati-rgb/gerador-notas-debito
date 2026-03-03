import pandas as pd
from datetime import date
from typing import Optional
from src.core.utils import parse_date, find_column_in_df

def check_expiration_column(df: pd.DataFrame, col_vencimento: str) -> list[dict]:
    """
    Verifica as datas de vencimento na coluna especificada e identifica notas expiradas.
    Retorna uma lista de dicionários com os detalhes das notas expiradas.
    """
    hoje = date.today()
    linhas_expiradas = []
    
    # Identifica coluna de Nome para o relatório de erros
    nome_col = find_column_in_df(df, ['Nome', 'Razão Social', 'Razao Social', 'Cliente'])
    
    for idx, row in df.iterrows():
        val = row.get(col_vencimento)
        d = parse_date(val)
        
        if d and d < hoje:
            razao = str(row[nome_col]) if nome_col else f"Linha {idx + 2}"
            linhas_expiradas.append({
                "Linha": idx + 2,
                "Razão Social": razao,
                "Vencimento": d.strftime('%d/%m/%Y')
            })
            
    return linhas_expiradas

def apply_date_replacement(df: pd.DataFrame, col_vencimento: str, expired_rows: list[dict], new_date: date) -> pd.DataFrame:
    """
    Substitui as datas das linhas expiradas por uma nova data informada.
    """
    indices_expirados = [r["Linha"] - 2 for r in expired_rows]
    df.loc[indices_expirados, col_vencimento] = new_date.strftime('%d/%m/%Y')
    return df

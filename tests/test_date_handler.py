import pytest
import pandas as pd
from datetime import date
from src.core.date_handler import check_expiration_column, apply_date_replacement
from src.core.utils import parse_date

def test_parse_date_formats():
    assert parse_date("01/01/2024") == date(2024, 1, 1)
    assert parse_date("2024-01-01") == date(2024, 1, 1)
    assert parse_date("01-01-2024") == date(2024, 1, 1)
    assert parse_date("2024/01/01") == date(2024, 1, 1)
    assert parse_date(date(2024, 1, 1)) == date(2024, 1, 1)
    assert parse_date(None) is None
    assert parse_date("") is None

def test_check_expiration_column():
    hoje = date.today()
    passado = "01/01/2020"
    futuro = "01/01/2099"
    
    df = pd.DataFrame({
        'Nome': ['Cliente A', 'Cliente B', 'Cliente C'],
        'Vencimento': [passado, futuro, '']
    })
    
    expirados = check_expiration_column(df, 'Vencimento')
    
    assert len(expirados) == 1
    assert expirados[0]['Razão Social'] == 'Cliente A'
    assert expirados[0]['Vencimento'] == passado

def test_apply_date_replacement():
    df = pd.DataFrame({
        'Vencimento': ['01/01/2020', '01/01/2099']
    })
    expired_rows = [{'Linha': 2, 'Razão Social': 'Cliente A', 'Vencimento': '01/01/2020'}]
    nova_data = date(2025, 12, 31)
    
    df_fixed = apply_date_replacement(df, 'Vencimento', expired_rows, nova_data)
    
    assert df_fixed.iloc[0]['Vencimento'] == '31/12/2025'
    assert df_fixed.iloc[1]['Vencimento'] == '01/01/2099'

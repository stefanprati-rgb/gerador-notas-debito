import pytest
import pandas as pd
from src.core.utils import (
    sanitize_text,
    format_currency,
    parse_currency,
    clean_filename_text,
    prepare_context
)

# Testes para sanitize_text
def test_sanitize_text_basic():
    assert sanitize_text("Teste 123") == "Teste 123"

def test_sanitize_text_none():
    assert sanitize_text(None) == ""

def test_sanitize_text_special_chars():
    # Testa caracteres que poderiam quebrar
    assert "café" in sanitize_text("café") 
    
# Testes para format_currency
def test_format_currency_valid():
    assert format_currency(1000.50) == "R$ 1.000,50"
    assert format_currency("1000.5") == "R$ 1.000,50"

def test_format_currency_none():
    assert format_currency(None) == "R$ 0,00"

def test_format_currency_invalid():
    # Deve retornar a string original se falhar
    assert format_currency("invalid") == "invalid"

# Testes para parse_currency
def test_parse_currency_valid():
    assert parse_currency("R$ 1.000,50") == 1000.50
    assert parse_currency("1.000,50") == 1000.50
    assert parse_currency("1000.50") == 1000.50

def test_parse_currency_none():
    assert parse_currency(None) == 0.0

# Testes para clean_filename_text
def test_clean_filename_text_basic():
    assert clean_filename_text("Empresa S.A.") == "EMPRESA_SA"

def test_clean_filename_text_accents():
    assert clean_filename_text("João & Maria") == "JOAO__MARIA"

def test_clean_filename_text_none():
    assert clean_filename_text(None) == ""
# Testes para prepare_context
def test_prepare_context_masking():
    row = pd.Series({
        'Nome': 'Stefan Pratti',
        'CNPJ/CPF': '123.456.789-01',
        'Endereço': 'Rua Teste, 123',
        'UF': 'SP',
        'Total a pagar': 'R$ 1.500,00'
    })
    
    # Com mascaramento
    ctx_masked = prepare_context(row, mask_data=True)
    assert ctx_masked['razao_social'] == 'Stefan ******'
    assert ctx_masked['cnpj_consorciado'] == '***.***.789-01'
    assert ctx_masked['total_pagar'] == 'R$ 1.500,00'
    
    # Sem mascaramento
    ctx_raw = prepare_context(row, mask_data=False)
    assert ctx_raw['razao_social'] == 'Stefan Pratti'
    assert ctx_raw['cnpj_consorciado'] == '123.456.789-01'

def test_prepare_context_fallbacks():
    # Testa fallback da coluna Dados Bancários (índice 29)
    data = [None] * 30
    data[29] = "Banco X - Ag 123 - CC 456"
    row = pd.Series(data)
    
    ctx = prepare_context(row)
    assert ctx['dados_bancarios'] == "Banco X - Ag 123 - CC 456"

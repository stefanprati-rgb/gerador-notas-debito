import pytest
import pandas as pd
from src.core.utils import sanitize_text, format_currency, parse_currency, clean_filename_text

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

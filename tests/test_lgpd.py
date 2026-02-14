from src.core.utils import mask_cpf_cnpj, mask_name, clean_filename_text

def test_mask_cpf():
    assert mask_cpf_cnpj("123.456.789-01") == "***.***.789-01"
    assert mask_cpf_cnpj("12345678901") == "***.***.789-01"

def test_mask_cnpj():
    assert mask_cpf_cnpj("12.345.678/0001-90") == "**.***.678/0001-**"
    assert mask_cpf_cnpj("12345678000190") == "**.***.678/0001-**"

def test_mask_name_pf():
    # PF sem documento -> Mascara
    assert mask_name("Stefan Pratti") == "Stefan ******"
    # PF com CPF -> Mascara
    assert mask_name("Stefan Pratti", doc="123.456.789-00") == "Stefan ******"

def test_mask_name_pj():
    # PJ com CNPJ -> NÃO Mascara
    nome_empresa = "Hube Soluções e Tecnologia Ltda"
    cnpj = "12.345.678/0001-90"
    assert mask_name(nome_empresa, doc=cnpj) == nome_empresa
    
    # PJ com CNPJ limpo -> NÃO Mascara
    cnpj_limpo = "12345678000190"
    assert mask_name(nome_empresa, doc=cnpj_limpo) == nome_empresa

def test_clean_filename():
    assert clean_filename_text("São Paulo") == "SAO_PAULO"
    assert clean_filename_text("João da Silva") == "JOAO_DA_SILVA"

if __name__ == "__main__":
    test_mask_cpf()
    test_mask_cnpj()
    test_mask_name_pf()
    test_mask_name_pj()
    test_clean_filename()
    print("Todos os testes de mascaramento (incluindo lógica PJ) passaram!")

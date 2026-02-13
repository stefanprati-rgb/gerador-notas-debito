from src.core.utils import mask_cpf_cnpj, mask_name

def test_mask_cpf():
    assert mask_cpf_cnpj("123.456.789-01") == "***.***.789-01"
    assert mask_cpf_cnpj("12345678901") == "***.***.789-01"

def test_mask_cnpj():
    assert mask_cpf_cnpj("12.345.678/0001-90") == "**.***.678/0001-**"
    assert mask_cpf_cnpj("12345678000190") == "**.***.678/0001-**"

def test_mask_name():
    assert mask_name("Stefan Pratti") == "Stefan ******"
    assert mask_name("João da Silva") == "João ** *****"
    assert mask_name("Hube") == "Hube"

if __name__ == "__main__":
    test_mask_cpf()
    test_mask_cnpj()
    test_mask_name()
    print("Todos os testes de mascaramento passaram!")

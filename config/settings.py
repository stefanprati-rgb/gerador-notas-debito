from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Caminhos
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR: Path = BASE_DIR.parent / "templates"
    LOGS_DIR: Path = BASE_DIR.parent / "logs"
    
    # App Info
    APP_NAME: str = "Hube Emissor"
    APP_VERSION: str = "1.0.0"
    
    # PDF Configuration
    DEFAULT_ENCODING: str = "utf-8"
    
    # Required Columns for Validation
    REQUIRED_FIELDS: list = [
        ("Nome/Razão Social", ['Nome', 'Razão Social', 'Cliente']),
        ("Endereço", ['Endereço', 'Endereco']),
        ("Cidade", ['Cidade']),
        ("UF", ['UF']),
        ("CNPJ/CPF", ['CNPJ/CPF', 'CNPJ', 'CPF']),
        ("Conta", ['Número da conta', 'Numero da conta', 'Conta vinculada']),
        ("Vencimento", ['Vencimento', 'Data Vencimento']),
        ("Referência", ['Mês de Referência', 'Mes Referencia']),
        # ("Instalação", ['Instalação', 'Instalacao', 'Numero Instalacao', 'Num. Instalação']), # Opcional / Fallback Index 0
        ("Total a Pagar", ['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Total']),
        ("Dados Bancários", ['Dados bancários', 'Dados bancarios', 'Pagamento'])
    ]

    class Config:
        env_file = ".env"

settings = Settings()

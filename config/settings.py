from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Caminhos
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    TEMPLATES_DIR: Path = BASE_DIR / "templates"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # App Info
    APP_NAME: str = "Hube Emissor"
    APP_VERSION: str = "1.0.0"
    
    # PDF Configuration
    DEFAULT_ENCODING: str = "utf-8"
    
    # Required Columns for Validation
    # Aliases expandidos para suportar diferentes modelos de planilha (ex: GD Gestão)
    REQUIRED_FIELDS: list = [
        ("Nome/Razão Social", ['Nome', 'Razão Social', 'Razao Social', 'Cliente']),
        ("Endereço", ['Endereço', 'Endereco', 'Endereço Consórcio', 'Endereco Consorcio']),
        # Cidade removida — já vem embutida no endereço completo em alguns modelos
        ("UF", ['UF']),
        ("CNPJ/CPF", ['CNPJ/CPF', 'CNPJ', 'CPF']),
        ("Conta", ['Número da conta', 'Numero da conta', 'Conta vinculada']),
        # Vencimento removido — tratado na UI (usuário pode informar manualmente)
        ("Referência", ['Mês de Referência', 'Mes Referencia', 'Referencia']),
        # ("Instalação", ['Instalação', 'Instalacao', 'Numero Instalacao', 'Num. Instalação']), # Opcional / Fallback Index 0
        ("Total a Pagar", ['Total a pagar', 'Total calculado R$', 'Valor consolidado', 'Valor emitido', 'Total']),
        ("Dados Bancários", ['Dados bancários', 'Dados bancarios', 'Pagamento', 'Número da conta', 'Numero da conta'])
    ]

    class Config:
        env_file = ".env"

settings = Settings()

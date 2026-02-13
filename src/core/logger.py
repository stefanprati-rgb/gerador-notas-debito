import logging
import sys
from pathlib import Path
from config.settings import settings

def setup_logger(name: str = "app_logger"):
    # Garante que o diretório de logs existe
    settings.LOGS_DIR.mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler
    file_handler = logging.FileHandler(settings.LOGS_DIR / "app.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Filtro LGPD para mascarar dados sensíveis nos logs
    class SensitiveDataFilter(logging.Filter):
        def filter(self, record):
            msg = str(record.msg)
            # Regex simples para CPF e CNPJ
            # CPF: 000.000.000-00 ou 00000000000
            msg = re.sub(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', '***.***.***-**', msg)
            msg = re.sub(r'\b\d{11}\b', '***********', msg)
            # CNPJ: 00.000.000/0000-00
            msg = re.sub(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b', '**.***.***/****-**', msg)
            record.msg = msg
            return True

    import re
    lgpd_filter = SensitiveDataFilter()

    # Evita duplicidade de handlers se a função for chamada múltiplas vezes
    if not logger.handlers:
        logger.addFilter(lgpd_filter)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logger()

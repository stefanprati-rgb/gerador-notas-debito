from xhtml2pdf import pisa
from io import BytesIO
from typing import List
from config.settings import settings
from src.core.logger import logger

def list_templates():
    """
    Lista arquivos .html dentro da pasta templates/.
    Retorna lista ordenada alfabeticamente.
    """
    templates_dir = settings.TEMPLATES_DIR

    if not templates_dir.exists():
        # Cria a pasta caso não exista, para evitar erros de navegação
        try:
            templates_dir.mkdir(exist_ok=True, parents=True)
            logger.info(f"Diretório de templates criado em: {templates_dir}")
        except Exception as e:
            logger.error(f"Erro ao criar diretório de templates: {e}")
        return []

    templates = [
        f.name for f in templates_dir.glob("*.html")
        if not f.name.startswith(".")
    ]
    
    logger.debug(f"Templates encontrados: {templates}")
    return sorted(templates)

def get_html_template(template_name: str):
    # Melhoria na resolução do caminho para garantir compatibilidade com diferentes OS
    template_path = settings.TEMPLATES_DIR / template_name
    
    try:
        # Forçamos utf-8 para garantir que acentos dos dados bancários não quebrem
        return template_path.read_text(encoding=settings.DEFAULT_ENCODING)
    except FileNotFoundError:
        logger.error(f"Template não encontrado: {template_path}")
        return f"""
        <html>
            <body>
                <h2 style="color: red;">Erro: Template não encontrado</h2>
                <p>O arquivo de template <b>templates/{template_name}</b> não foi localizado.</p>
                <p>Verifique se o arquivo existe na pasta 'templates' e se o nome está correto.</p>
            </body>
        </html>
        """
    except Exception as e:
        logger.exception(f"Erro ao ler template {template_name}: {e}")
        return str(e)

def generate_pdf(html):
    """
    Converte HTML para PDF usando xhtml2pdf.
    O HTML já deve conter a variável {{ dados_bancarios }} renderizada pelo Jinja2.
    """
    buffer = BytesIO()
    # xhtml2pdf é sensível a encodings; o Jinja já entrega a string processada
    try:
        pisa_status = pisa.CreatePDF(html, dest=buffer, encoding=settings.DEFAULT_ENCODING)
        
        if pisa_status.err: 
            logger.error(f"Erro na geração do PDF: {pisa_status.err}")
            return None, f"Erro layout: {pisa_status.err}"
        
        return buffer.getvalue(), None
    except Exception as e:
        logger.exception(f"Exceção durante geração do PDF: {e}")
        return None, str(e)

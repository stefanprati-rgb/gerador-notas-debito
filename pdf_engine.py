from xhtml2pdf import pisa
from io import BytesIO

from pathlib import Path

from typing import List

def list_templates() -> List[str]:
    """
    Lista os arquivos de template HTML disponíveis na pasta templates/.
    Ignora arquivos ocultos ou que iniciam com underscore.
    """
    templates_dir = Path(__file__).parent / "templates"
    if not templates_dir.exists():
        return []
    
    templates = [
        f.name for f in templates_dir.glob("*.html")
        if not f.name.startswith((".", "_"))
    ]
    return sorted(templates)

def get_html_template(template_name: str):
    template_path = Path(__file__).parent / "templates" / template_name
    try:
        return template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"""
        <html>
            <body>
                <h2 style="color: red;">Erro: Template não encontrado</h2>
                <p>O arquivo de template <b>templates/{template_name}</b> não foi localizado.</p>
                <p>Verifique se o arquivo existe na pasta 'templates' e se o nome está correto.</p>
            </body>
        </html>
        """

def generate_pdf(html):
    """
    Converte HTML para PDF usando xhtml2pdf.
    """
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=buffer)
    if pisa_status.err: return None, f"Erro layout: {pisa_status.err}"
    return buffer.getvalue(), None

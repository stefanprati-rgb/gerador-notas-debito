from xhtml2pdf import pisa
from io import BytesIO
from pathlib import Path
from typing import List

def list_templates():
    """
    Lista arquivos .html dentro da pasta templates/.
    Retorna lista ordenada alfabeticamente.
    """
    templates_dir = Path("templates")

    if not templates_dir.exists():
        # Cria a pasta caso não exista, para evitar erros de navegação
        templates_dir.mkdir(exist_ok=True)
        return []

    templates = [
        f.name for f in templates_dir.glob("*.html")
        if not f.name.startswith(".")
    ]

    return sorted(templates)

def get_html_template(template_name: str):
    # Melhoria na resolução do caminho para garantir compatibilidade com diferentes OS
    template_path = Path("templates") / template_name
    
    try:
        # Forçamos utf-8 para garantir que acentos dos dados bancários não quebrem
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
    O HTML já deve conter a variável {{ dados_bancarios }} renderizada pelo Jinja2.
    """
    buffer = BytesIO()
    # xhtml2pdf é sensível a encodings; o Jinja já entrega a string processada
    pisa_status = pisa.CreatePDF(html, dest=buffer, encoding='utf-8')
    
    if pisa_status.err: 
        return None, f"Erro layout: {pisa_status.err}"
    
    return buffer.getvalue(), None

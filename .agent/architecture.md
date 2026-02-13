# Decisões de Arquitetura

## Padrão Arquitetural
O projeto segue uma estrutura de **Scripts Modulares** organizada por responsabilidade, facilitando a manutenção e testes.

## Estrutura de Pastas
- **src/**: Código fonte principal.
    - **core/**: Lógica de processamento de dados e validações.
    - **adapters/**: (Se houver) Integrações com sistemas externos.
    - **services/**: Motores de geração (ex: PDF Engine).
- **templates/**: Arquivos HTML/Jinja2 para renderização documental.
- **config/**: Configurações globais e presets.
- **data/**: Armazenamento temporário ou persistente de insumos.
- **output/**: Destino dos arquivos gerados.

## Separação de Responsabilidades
- **app.py**: Orquestração da interface Streamlit e fluxo de usuário.
- **utils.py**: Funções utilitárias de manipulação de dataframes, formatação de strings e tratamento de dados brutos da planilha.
- **pdf_engine.py**: Lógica isolada para transformar HTML em PDF, gerenciamento de fontes e estilos CSS.

## Decisões Importantes
- **xhtml2pdf**: Escolhido pela facilidade de transformar layouts HTML/CSS em PDF, embora possua limitações de CSS moderno.
- **Isolamento de Templates**: Uso de arquivos `.html` externos para evitar poluição do código Python.

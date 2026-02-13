# Projeto: Emissor de Notas Hube

## Objetivo
Automação para geração de notas de débito (ou avisos de débito) de forma em lote, utilizando arquivos de planilha (Excel/CSV) como fonte de dados. O projeto visa facilitar o processo de cobrança e emissão documental.

## Tipo
automação

## Stack Técnica
- **Linguagem**: Python 3.x
- **Framework UI**: Streamlit
- **Geração de PDF**: xhtml2pdf / Jinja2
- **Manipulação de Dados**: Pandas, Openpyxl
- **Outras dependências**: [Conforme requirements.txt]

## Integrações Externas
- [x] Planilhas locais (Excel/CSV)
- [ ] API (Nenhuma no momento)
- [ ] Banco de Dados (Nenhum no momento)

## Requisitos Críticos
- **Performance**: Processamento eficiente de planilhas com múltiplas linhas.
- **Segurança**: Proteção de dados sensíveis nas notas geradas.
- **Compliance**: LGPD (Lei Geral de Proteção de Dados) é mandatória.
- **Disponibilidade**: Uso sob demanda via interface Streamlit.

## LGPD & Dados Pessoais
**⚠️ Este projeto processa dados pessoais de clientes para a emissão de notas.**

### Dados Coletados/Processados
- **Nome/Razão Social**: [Sim] - Finalidade: Identificação na nota.
- **CPF/CNPJ**: [Sim] - Finalidade: Identificação fiscal/faturamento.
- **Endereço**: [Sim] - Finalidade: Localização/entrega.
- **Dados Bancários**: [Sim] - Finalidade: Instruções de pagamento.

### Base Legal
- [X] Contrato (necessário para execução de cobrança/serviço)
- [ ] Consentimento
- [ ] Obrigação legal

### Retenção de Dados
- **Período**: Conforme regras contábeis/fiscais vigentes.
- **Critério de exclusão**: Sob pedido ou fim do período legal.

### Compliance
- [x] Ambiente de dev deve evitar exposição de dados reais onde possível.
- [x] Logs não devem conter dados pessoais sensíveis (CPF, etc).
- [ ] Criptografia em repouso (a verificar se necessário no target de deploy).

## Contexto do Time
- **Tamanho**: Solo
- **Nível**: Sênior
- **Deployment**: Streamlit (Cloud/Local)

## Ambiente
- **Desenvolvimento**: Windows, VS Code
- **Produção**: Streamlit Cloud / On-premise

## Notas Adicionais
O projeto foi refatorado recentemente para separar lógica de negócio (`utils.py`, `pdf_engine.py`) da interface (`app.py`).

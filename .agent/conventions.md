# Convenções Específicas do Projeto

## Nomenclatura
- **Arquivos**: `snake_case.py`
- **Variáveis/Funções**: `snake_case` (em Inglês, conforme regras globais)
- **Classes**: `PascalCase`
- **Pastas**: `snake_case`

## Padrões de Código
- **Docstrings**: Obrigatórias em funções complexas, escritas em **Português (PT-BR)**.
- **Comentários**: Em **Português (PT-BR)** para explicar o "porquê" da lógica.
- **Tratamento de Erros**: Uso consistente de blocos `try-except` com logs informativos.
- **Tipagem**: Uso de *Type Hints* onde possível para aumentar a clareza.

## Git & Commits
- Seguir **Conventional Commits** (Ex: `feat:`, `fix:`, `refactor:`, `docs:`).

## LGPD & Dados
- Nunca imprimir CPFs ou dados sensíveis em logs de nível `INFO` ou `ERROR` que possam ser exportados.
- Usar máscaras em logs caso seja necessário rastrear um item (ex: `123.***.***-45`).

# Tasks & Roadmap

## Em Progresso
- [x] Inicialização do contexto do agente (`.agent/`)
- [ ] Verificação de conformidade LGPD nos fluxos de geração

## Próximos Passos
- [ ] Implementar logs auditáveis para rastreio de geração de notas sem expor dados sensíveis.
- [ ] Melhorar a robustez da leitura de planilhas (fallback de colunas).
- [ ] Adicionar testes unitários para o motor de PDF.

## Backlog
- [ ] Suporte a múltiplos templates de nota.
- [ ] Dashboard de histórico de notas geradas (se houver persistência).

## Issues Conhecidos
- Limitação do `xhtml2pdf` com fontes customizadas (necessário registro manual).
- Dependência de nomes de colunas exatos na planilha (resolver com mapping flexível).

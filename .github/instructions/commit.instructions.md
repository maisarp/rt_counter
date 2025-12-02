# Instruções para Mensagens de Commit

## Formato da Mensagem

```
[tipo] - breve descrição

- mudança 1
- mudança 2
- mudança N

** Mensagem de Commit Gerada pelo Copilot **
```

## Tipos de Commit

| Tipo | Descrição |
|------|-----------|
| `[feature]` | Nova funcionalidade ou recurso |
| `[hotfix]` | Correção urgente em produção |
| `[bugfix]` | Correção de bug |
| `[refactor]` | Refatoração de código sem alterar comportamento |
| `[docs]` | Alterações na documentação |
| `[test]` | Adição ou modificação de testes |
| `[style]` | Formatação, espaços, ponto e vírgula, etc. |
| `[chore]` | Tarefas de manutenção (dependências, configs) |
| `[perf]` | Melhorias de performance |

## Regras

1. **Tipo obrigatório**: Sempre iniciar com o tipo entre colchetes
2. **Descrição breve**: Após o tipo, usar hífen e uma descrição curta (máximo 50 caracteres)
3. **Lista de mudanças**: Detalhar as alterações em bullet points
4. **Idioma**: Escrever em português
5. **Assinatura**: Finalizar com `** Mensagem de Commit Gerada pelo Copilot **`

## Exemplo Completo

```
[feature] - implementação de timer

- implementa timer na aplicação
- inclusão de testes unitários para a classe Timer
- inclusão na interface (botões de iniciar, parar e feedback visual)

** Mensagem de Commit Gerada pelo Copilot **
```

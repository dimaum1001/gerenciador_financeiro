# Convenções de Terminologia (PT-BR ↔ Inglês)

Este documento descreve o mapeamento entre os valores legados (em inglês) que
continuam gravados no banco de dados e os novos termos expostos em português.
Enquanto as migrações definitivas não forem aplicadas, a API aceita ambos os
formatos e adiciona campos derivados (`*_portugues`, `*_legado`) nas respostas.

## Tipos de Conta (`AccountType`)

| Inglês      | Português        |
|-------------|------------------|
| `cash`      | `dinheiro`       |
| `checking`  | `conta_corrente` |
| `savings`   | `poupanca`       |
| `credit`    | `cartao_credito` |
| `investment`| `investimento`   |
| `other`     | `outros`         |

## Tipos de Categoria (`CategoryType`)

| Inglês   | Português |
|----------|-----------|
| `income` | `receita` |
| `expense`| `despesa` |

## Transações

| Campo                | Inglês                              | Português                        |
|----------------------|-------------------------------------|----------------------------------|
| `tipo`               | `income`, `expense`, `transfer`     | `receita`, `despesa`, `transferencia` |
| `status`             | `pending`, `cleared`, `reconciled`  | `pendente`, `compensada`, `conciliada` |
| `payment_method`     | `cash`, `pix`, `debit`, `credit`, `boleto`, `transfer`, `check`, `other` | `dinheiro`, `pix`, `cartao_debito`, `cartao_credito`, `boleto`, `transferencia`, `cheque`, `outros` |

## Orçamentos (`BudgetStatus`)

| Inglês     | Português  |
|------------|------------|
| `active`   | `ativo`    |
| `paused`   | `pausado`  |
| `completed`| `concluido`|
| `exceeded` | `excedido` |

## Regras Recorrentes

| Campo       | Inglês                                       | Português                         |
|-------------|----------------------------------------------|-----------------------------------|
| `frequencia`| `daily`, `weekly`, `monthly`, `quarterly`, `yearly` | `diario`, `semanal`, `mensal`, `trimestral`, `anual` |
| `status`    | `active`, `paused`, `completed`, `cancelled` | `ativa`, `pausada`, `concluida`, `cancelada` |

> **Observação:** novos clientes devem preferir os valores PT-BR. Clientes
> legados podem continuar enviando os valores antigos; o backend faz a tradução
> automaticamente até que a migração estrutural esteja concluída.

## Tabelas e Colunas (Planejamento da Migração)

| Tabela atual      | Nova tabela        | Colunas a renomear (antigo → novo)                                                                                           |
|-------------------|--------------------|------------------------------------------------------------------------------------------------------------------------------|
| `users`           | `usuarios`         | `id` (mantém), `email` (mantém), `timezone → fuso_horario`, `moeda_padrao` (mantém), `formato_data` (mantém), `is_demo → demo` |
| `accounts`        | `contas`           | `user_id → usuario_id`, `is_demo_data → dados_demo`, `saldo_inicial` (mantém), `account_id` não existe                        |
| `categories`      | `categorias`       | `user_id → usuario_id`, `is_demo_data → dados_demo`, `parent_id → categoria_pai_id`                                           |
| `transactions`    | `transacoes`       | `user_id → usuario_id`, `account_id → conta_id`, `category_id → categoria_id`, `transfer_account_id → conta_transferencia_id`, `transfer_transaction_id → transacao_transferencia_id`, `recurring_rule_id → regra_recorrente_id`, `payment_method → metodo_pagamento`, `attachment_url → anexo_url`, `attachment_name → anexo_nome`, `is_demo_data → dados_demo` |
| `budgets`         | `orcamentos`       | `user_id → usuario_id`, `category_id → categoria_id`, `is_demo_data → dados_demo`, `budget_status` já coberto por enum        |
| `recurring_rules` | `regras_recorrentes` | `user_id → usuario_id`, `account_id → conta_id`, `category_id → categoria_id`, `payment_method → metodo_pagamento`, `status` (enum já tratado), `proxima_execucao` etc. mantidos, `recurring_rule_id` não se aplica                                  |

> Durante a migração Alembic, criaremos _views_ ou sinônimos temporários com os
> nomes antigos (`accounts`, `transactions`, etc.) apontando para as novas
> tabelas, garantindo que qualquer integração legada baseada em SQL direto
> continue funcionando até o desligamento oficial. Do lado da API, os campos
> Pydantic continuarão aceitando/alimentando `*_id` em inglês via `alias`,
> enquanto os atributos internos e o banco usarão os nomes PT-BR.

### Estratégia de Compatibilidade

1. **Camada de Tradução (já implementada)** — enums e valores persistidos são
   traduzidos automaticamente.
2. **Migrar Banco/Tabelas** — renomear tabelas e colunas conforme quadro acima,
   atualizar as FKs/índices e criar views com os nomes antigos para clientes SQL.
3. **Aliases na API** — manter `Field(alias=...)` para permitir tanto `account_id`
   quanto `conta_id` durante o período de transição.
4. **Depreciação gradual** — comunicar o prazo de desligamento dos nomes legados
   e remover as views/aliases após a migração completa.

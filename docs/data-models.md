# Modelos de Dados

Todos os models herdam de `TimestampedModel` (`app_core`), que fornece `created_at` e `updated_at`. Valores como totais e saldos são **calculados em tempo real** — nunca armazenados.

---

## User (`app_accounts`)

Campo de login: `email` (substitui `username`).

| Campo | Tipo |
|---|---|
| `id` | PK |
| `email` | string, único |
| `password` | string |
| `is_active` | bool |
| `is_staff` | bool |
| `created_at` | datetime |
| `updated_at` | datetime |

---

## FinancialMonth (`app_months`)

Restrição de unicidade: `(user, year, month)`.

| Campo | Tipo | Observação |
|---|---|---|
| `id` | PK | — |
| `user` | FK → User | — |
| `year` | int | — |
| `month` | int | — |
| `investment_goal` | decimal | Meta mensal de investimento |
| `start_date` | date, nullable | Data de início do mês (opcional) |
| `end_date` | date, nullable | Data de fim do mês (opcional) |
| `created_at` | datetime | — |
| `updated_at` | datetime | — |

### Métodos calculados

| Método | Descrição |
|---|---|
| `total_entries()` | Soma de todas as entradas do mês |
| `total_variable_expenses()` | Soma dos gastos variáveis |
| `total_fixed_expenses()` | Soma das despesas fixas |
| `total_card_invoices()` | Soma das faturas de cartão |
| `total_investments()` | Soma dos investimentos |
| `total_installment_payments()` | Soma das parcelas de planos `payment` |
| `total_installment_sales()` | Soma das parcelas de planos `sale` |
| `total_installment_loans()` | Soma das parcelas de planos `loan` |
| `total_expenses()` | Variáveis + Fixas + Faturas |
| `total_fixed_display()` | Fixas + Faturas (agrupado para exibição) |
| `previous_balance()` | Saldo final do mês anterior (ou 0) |
| `current_balance()` | Saldo atual: anterior + entradas − despesas − investimentos |

---

## Entry — Entradas (`app_months`)

| Campo | Tipo |
|---|---|
| `id` | PK |
| `financial_month` | FK → FinancialMonth |
| `description` | string |
| `amount` | decimal |
| `date` | date |
| `created_at` | datetime |
| `updated_at` | datetime |

---

## VariableExpense — Gastos variáveis (`app_months`)

| Campo | Tipo |
|---|---|
| `id` | PK |
| `financial_month` | FK → FinancialMonth |
| `description` | string |
| `amount` | decimal |
| `date` | date |
| `created_at` | datetime |
| `updated_at` | datetime |

---

## FixedExpense — Despesas fixas (`app_months`)

| Campo | Tipo | Valores |
|---|---|---|
| `id` | PK | — |
| `financial_month` | FK → FinancialMonth | — |
| `description` | string | — |
| `amount` | decimal | — |
| `status` | string | `paid` / `unpaid` |
| `created_at` | datetime | — |
| `updated_at` | datetime | — |

---

## Card (`app_cards`)

| Campo | Tipo | Valores |
|---|---|---|
| `id` | PK | — |
| `user` | FK → User | — |
| `name` | string | — |
| `brand` | string | `Visa`, `Mastercard`, `Elo`, `American Express`, `Hipercard`, `Outros` |
| `closing_day` | int | Dia de fechamento da fatura |
| `due_day` | int | Dia de vencimento |
| `created_at` | datetime | — |
| `updated_at` | datetime | — |

---

## CardInvoice — Fatura do cartão (`app_cards`)

Restrição de unicidade: `(card, financial_month)`.

| Campo | Tipo | Valores |
|---|---|---|
| `id` | PK | — |
| `card` | FK → Card | — |
| `financial_month` | FK → FinancialMonth | — |
| `amount` | decimal | — |
| `status` | string | `paid` / `unpaid` |
| `created_at` | datetime | — |
| `updated_at` | datetime | — |

---

## Investment — Investimentos (`app_investments`)

| Campo | Tipo |
|---|---|
| `id` | PK |
| `financial_month` | FK → FinancialMonth |
| `place` | string |
| `amount` | decimal |
| `date` | date |
| `created_at` | datetime |
| `updated_at` | datetime |

---

## InstallmentPlan — Plano de parcelamento (`app_installments`)

| Campo | Tipo | Valores |
|---|---|---|
| `id` | PK | — |
| `user` | FK → User | — |
| `name` | string | — |
| `kind` | string | `payment` (saída) / `sale` (entrada) / `loan` (empréstimo) |
| `created_at` | datetime | — |
| `updated_at` | datetime | — |

### Métodos calculados

| Método | Descrição |
|---|---|
| `total()` | Soma de todas as parcelas |
| `total_paid()` | Soma das parcelas pagas |
| `total_remaining()` | `total() - total_paid()` |
| `count_paid()` | Número de parcelas pagas |
| `count_total()` | Número total de parcelas |

---

## Installment — Parcela (`app_installments`)

| Campo | Tipo | Valores |
|---|---|---|
| `id` | PK | — |
| `plan` | FK → InstallmentPlan | — |
| `financial_month` | FK → FinancialMonth | — |
| `number` | int | Número da parcela |
| `amount` | decimal | — |
| `status` | string | `paid` / `unpaid` |
| `receipt_url` | string (URL) | Link do comprovante (Google Drive etc.) |
| `created_at` | datetime | — |
| `updated_at` | datetime | — |

---

## Diagrama de relacionamentos

```
User ──< FinancialMonth ──< Entry
     │                 ──< VariableExpense
     │                 ──< FixedExpense
     │                 ──< Investment
     │                 ──< CardInvoice >── Card <── User
     │                 ──< Installment >── InstallmentPlan <── User
     ├──< Card
     └──< InstallmentPlan
```

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

| Campo | Tipo |
|---|---|
| `id` | PK |
| `user` | FK → User |
| `year` | int |
| `month` | int |
| `investment_goal` | decimal |

---

## Entry — Entradas (`app_months`)

| Campo | Tipo |
|---|---|
| `id` | PK |
| `financial_month` | FK → FinancialMonth |
| `date` | date |
| `description` | string |
| `amount` | decimal |

---

## VariableExpense — Gastos variáveis (`app_months`)

| Campo | Tipo |
|---|---|
| `id` | PK |
| `financial_month` | FK → FinancialMonth |
| `description` | string |
| `date` | date |
| `payment_method` | string |
| `amount` | decimal |

---

## FixedExpense — Despesas fixas (`app_months`)

| Campo | Tipo | Valores |
|---|---|---|
| `id` | PK | — |
| `financial_month` | FK → FinancialMonth | — |
| `description` | string | — |
| `status` | string | `paid` / `unpaid` |
| `amount` | decimal | — |

---

## Card (`app_cards`)

| Campo | Tipo |
|---|---|
| `id` | PK |
| `user` | FK → User |
| `name` | string |
| `brand` | string |
| `closing_day` | int |
| `due_day` | int |

---

## CardInvoice — Fatura do cartão (`app_cards`)

| Campo | Tipo |
|---|---|
| `id` | PK |
| `card` | FK → Card |
| `financial_month` | FK → FinancialMonth |
| `amount` | decimal |

---

## Investment — Investimentos (`app_investments`)

| Campo | Tipo |
|---|---|
| `id` | PK |
| `financial_month` | FK → FinancialMonth |
| `place` | string |
| `amount` | decimal |

---

## InstallmentPlan — Plano de parcelamento (`app_installments`)

| Campo | Tipo | Valores |
|---|---|---|
| `id` | PK | — |
| `user` | FK → User | — |
| `name` | string | — |
| `kind` | string | `payment` / `sale` |

---

## Installment — Parcela (`app_installments`)

| Campo | Tipo | Valores |
|---|---|---|
| `id` | PK | — |
| `plan` | FK → InstallmentPlan | — |
| `financial_month` | FK → FinancialMonth | — |
| `number` | int | — |
| `amount` | decimal | — |
| `status` | string | `paid` / `unpaid` |
| `receipt_url` | string | URL do comprovante |

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

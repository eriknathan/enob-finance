# Arquitetura

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12+ / Django 6.x |
| Banco de dados | SQLite (desenvolvimento) / PostgreSQL (produção via Docker) |
| Frontend | Django Template Language (DTL) + TailwindCSS (CDN) |
| Autenticação | Django Auth nativo — Custom User com login por e-mail |
| Exportação | openpyxl (geração de `.xlsx` multi-abas) |
| Servidor de produção | Gunicorn + Nginx |
| Containerização | Docker / docker-compose |

O projeto é uma aplicação monolítica Django full stack. Não há framework JS adicional. TailwindCSS é carregado via CDN. Variáveis de ambiente lidas de `.env` via `python-dotenv`.

---

## Organização em Apps

Cada domínio de negócio vive em um app Django com prefixo `app_`.

| App | Responsabilidade |
|---|---|
| `app_core` | `TimestampedModel` abstrato, template base, mixins compartilhados, home/redirect, template tags (`core_tags`) |
| `app_accounts` | Custom User (login por e-mail), autenticação |
| `app_months` | Mês financeiro e seus lançamentos: entradas, gastos variáveis, despesas fixas, resumo e saldo |
| `app_cards` | Cartões de crédito, faturas mensais e histórico por cartão |
| `app_investments` | Investimentos do mês, meta mensal, visão anual meta × realizado e simulador de rendimento |
| `app_installments` | Planos de parcelamento (pagamentos, vendas e empréstimos) e suas parcelas |
| `app_dashboard` | Dashboard consolidado com tabela e gráficos anuais |
| `app_exports` | Exportação de todos os dados para Excel (`.xlsx`) |

---

## Regras de Negócio

1. **Continuidade de saldo** — o saldo final de um mês entra como "saldo do mês anterior" no mês seguinte, calculado recursivamente via `FinancialMonth.current_balance()`.
2. **Meta × investido** — a meta mensal é definida manualmente; o valor investido é sempre derivado da soma dos investimentos do mês, nunca digitado diretamente.
3. **Template replicável** — todo mês novo nasce da mesma estrutura base.
4. **Parcelamento** — planos geram N parcelas distribuídas pelos meses, cada uma com status e comprovante próprios.
5. **Tipos de plano** — `kind` pode ser `payment` (saída/pagamento), `sale` (entrada/venda) ou `loan` (empréstimo).
6. **Comprovantes por link** — armazena-se a URL do comprovante (ex.: Google Drive), não o arquivo.
7. **Isolamento por usuário** — todas as queries filtram pelo usuário autenticado.
8. **Totais e saldos calculados** — valores derivados (totais, saldos) são sempre calculados via métodos/propriedades dos models; nunca armazenados.

---

## Fluxo de URLs

```
/                       → HomeView (redireciona ao dashboard)
/conta/                 → app_accounts (login, registro, logout)
/meses/                 → app_months (FinancialMonth, Entry, Expense, FixedExpense)
/cartoes/               → app_cards (Card, CardInvoice)
/investimentos/         → app_investments (Investment, meta anual, simulador)
/parcelamentos/         → app_installments (InstallmentPlan, Installment)
/dashboard/             → app_dashboard (visão consolidada)
/exportar/              → app_exports (download .xlsx)
/admin/                 → Django Admin
```

---

## Templates

Todos os arquivos de template ficam na pasta raiz `templates/`, organizados por app.

```
templates/
  base.html
  components/
    button.html
    card.html
    input.html
    month_carousel.html
    sidebar.html
    status_pill.html
    topbar.html
  app_accounts/
  app_months/
  app_cards/
  app_investments/
  app_installments/
  app_dashboard/
```

Signals, quando usados, ficam em `signals.py` dentro da app correspondente.

---

## Configurações de Ambiente

O projeto lê variáveis de `.env` na raiz. Configurações relevantes:

| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | valor insecure de dev | Chave secreta do Django |
| `DEBUG` | `True` | Modo de depuração |
| `ALLOWED_HOSTS` | `*` | Hosts permitidos (separados por vírgula) |

Em produção, use `enobfinance/settings_prod.py` (via `DJANGO_SETTINGS_MODULE`), que enforça `DEBUG=False`, cookies seguros e HTTPS redirect.

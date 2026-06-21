# Arquitetura

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12+ / Django 5.x |
| Banco de dados | SQLite (padrão do Django) |
| Frontend | Django Template Language (DTL) + TailwindCSS |
| Autenticação | Django Auth nativo — Custom User com login por e-mail |
| Exportação | openpyxl (geração de `.xlsx` multi-abas) |

O projeto é uma aplicação monolítica Django full stack. Não há framework JS adicional. TailwindCSS é carregado via CDN ou build local.

---

## Organização em Apps

Cada domínio de negócio vive em um app Django com prefixo `app_`.

| App | Responsabilidade |
|---|---|
| `app_core` | `TimestampedModel` abstrato, template base, mixins compartilhados, home/redirect |
| `app_accounts` | Custom User (login por e-mail), autenticação |
| `app_months` | Mês financeiro e seus lançamentos: entradas, gastos variáveis, despesas fixas, resumo e saldo |
| `app_cards` | Cartões de crédito e faturas mensais |
| `app_investments` | Investimentos do mês e visão anual meta × realizado |
| `app_installments` | Planos de parcelamento (pagamentos e vendas) e suas parcelas |
| `app_dashboard` | Dashboard consolidado (mensal e anual) |
| `app_exports` | Exportação de todos os dados para Excel |

---

## Regras de Negócio

1. **Continuidade de saldo** — o saldo final de um mês entra como "saldo do mês anterior" (entrada) no mês seguinte.
2. **Meta × investido** — a meta mensal é definida manualmente; o valor investido é sempre derivado da soma dos investimentos do mês, nunca digitado diretamente.
3. **Template replicável** — todo mês novo nasce da mesma estrutura base.
4. **Parcelamento** — planos geram N parcelas distribuídas pelos meses, cada uma com status e comprovante próprios.
5. **Pagamento × venda** — mesma estrutura; diferença apenas no `kind` (`payment` vs. `sale`).
6. **Comprovantes por link** — armazena-se a URL do comprovante (ex.: Google Drive), não o arquivo.
7. **Isolamento por usuário** — todas as queries filtram pelo usuário autenticado.

---

## Templates

Todos os arquivos de template ficam na pasta raiz `templates/`, organizados por app.

```
templates/
  base.html
  components/
  app_accounts/
  app_months/
  app_cards/
  app_investments/
  app_installments/
  app_dashboard/
  app_exports/
```

Signals, quando usados, ficam em `signals.py` dentro da app correspondente.

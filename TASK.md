## 13. Lista de Tarefas (Sprints)

> Checklist granular. Marque `[x]` conforme concluir cada item.

### Sprint 0 — Setup do Projeto ✅

- [x] **0.1 — Inicialização**
    - [x] 0.1.1 Criar virtualenv e instalar Django
    - [x] 0.1.2 Criar projeto Django (`enobfinance`)
    - [x] 0.1.3 Configurar SQLite (padrão) em `settings.py`
    - [x] 0.1.4 Definir `LANGUAGE_CODE = 'pt-br'` e `TIME_ZONE` apropriado
    - [x] 0.1.5 Configurar pasta de templates na raiz: `TEMPLATES['DIRS'] = [BASE_DIR / 'templates']`
    - [x] 0.1.6 Configurar arquivos estáticos
- [x] **0.2 — Padrões de código**
    - [x] 0.2.1 Definir convenção de aspas simples e código em inglês
    - [x] 0.2.2 Criar `requirements.txt` (Django, openpyxl)
    - [x] 0.2.3 Configurar `.gitignore`
- [x] **0.3 — App base (`app_core`)**
    - [x] 0.3.1 Criar app `app_core`
    - [x] 0.3.2 Criar `TimestampedModel` abstrato com `created_at` e `updated_at`
    - [x] 0.3.3 Criar `templates/base.html` com estrutura HTML, Tailwind e blocos
    - [x] 0.3.4 Integrar TailwindCSS (CDN ou build) e fonte Sora
    - [x] 0.3.5 Criar view/home que redireciona ao dashboard ou login

### Sprint 1 — Autenticação por E-mail (`app_accounts`) ✅

- [x] **1.1 — Custom User**
    - [x] 1.1.1 Criar app `app_accounts`
    - [x] 1.1.2 Criar Custom User (`AbstractUser`) com `email` como `USERNAME_FIELD`
    - [x] 1.1.3 Remover/ignorar `username`; herdar de `TimestampedModel`
    - [x] 1.1.4 Criar `UserManager` para criação por e-mail
    - [x] 1.1.5 Configurar `AUTH_USER_MODEL` antes da primeira migração
    - [x] 1.1.6 Rodar migração inicial
- [x] **1.2 — Cadastro e login**
    - [x] 1.2.1 Criar form de cadastro (e-mail e senha)
    - [x] 1.2.2 Criar CBV de cadastro (`CreateView`)
    - [x] 1.2.3 Criar CBV de login por e-mail (`LoginView` customizada)
    - [x] 1.2.4 Criar CBV de logout
    - [x] 1.2.5 Criar templates `templates/app_accounts/login.html` e `register.html`
    - [x] 1.2.6 Proteger rotas com `LoginRequiredMixin`
    - [x] 1.2.7 Mensagens de erro/sucesso em pt-BR

### Sprint 2 — Design System e Layout ✅

- [x] **2.1 — Base visual**
    - [x] 2.1.1 Definir paleta de cores e gradientes no template base
    - [x] 2.1.2 Aplicar tipografia Sora e escala tipográfica
    - [x] 2.1.3 Criar componentes parciais (`templates/components/`): botão, input, card, pill de status
- [x] **2.2 — Navegação**
    - [x] 2.2.1 Criar sidebar (desktop) com itens de menu
    - [x] 2.2.2 Criar topbar responsiva
    - [x] 2.2.3 Implementar menu mobile
    - [x] 2.2.4 Marcar item ativo do menu
    - [x] 2.2.5 Implementar toggle de tema claro/escuro

### Sprint 3 — Mês Financeiro e Template Mensal (`app_months`) ✅

- [x] **3.1 — Models**
    - [x] 3.1.1 Criar app `app_months`
    - [x] 3.1.2 Model `FinancialMonth` (user, year, month, investment_goal) com unique (user, year, month)
    - [x] 3.1.3 Model `Entry` (entradas)
    - [x] 3.1.4 Model `VariableExpense` (gastos variáveis)
    - [x] 3.1.5 Model `FixedExpense` (despesas fixas, status pago/não pago)
    - [x] 3.1.6 Métodos de cálculo: total de entradas, saídas, investido, cartões, saldo
    - [x] 3.1.7 Método de saldo do mês anterior (carry-over)
    - [x] 3.1.8 Migrações
- [x] **3.2 — Views e templates do mês**
    - [x] 3.2.1 CBV de detalhe do mês (`DetailView`) renderizando o template completo
    - [x] 3.2.2 Card de resumo do mês
    - [x] 3.2.3 Card de saldo atual
    - [x] 3.2.4 CRUD de entradas (Create/Update/Delete views)
    - [x] 3.2.5 CRUD de gastos variáveis
    - [x] 3.2.6 CRUD de despesas fixas
    - [x] 3.2.7 Garantir isolamento por usuário em todas as queries
- [x] **3.3 — Navegação entre meses (carrossel)**
    - [x] 3.3.1 Lógica para mês anterior/próximo (a partir de Jan/2026)
    - [x] 3.3.2 Criação automática/lazy do mês ao acessar
    - [x] 3.3.3 Componente de carrossel de meses no template

### Sprint 4 — Cartões e Faturas (`app_cards`) ✅

- [x] **4.1 — Models**
    - [x] 4.1.1 Criar app `app_cards`
    - [x] 4.1.2 Model `Card` (name, brand, closing_day, due_day)
    - [x] 4.1.3 Model `CardInvoice` (card, financial_month, amount)
    - [x] 4.1.4 Migrações
- [x] **4.2 — Views e templates**
    - [x] 4.2.1 CRUD de cartões (CBVs)
    - [x] 4.2.2 Template de cadastro/listagem de cartões
    - [x] 4.2.3 Registro de fatura por cartão no mês
    - [x] 4.2.4 Integrar total de cartões ao resumo do mês

### Sprint 5 — Investimentos e Meta (`app_investments`) ✅

- [x] **5.1 — Models e regras**
    - [x] 5.1.1 Criar app `app_investments`
    - [x] 5.1.2 Model `Investment` (financial_month, place, amount)
    - [x] 5.1.3 Lógica de "investido por mês" (soma dos lançamentos)
    - [x] 5.1.4 Edição da meta mensal (campo em `FinancialMonth`)
    - [x] 5.1.5 Migrações
- [x] **5.2 — Views e templates**
    - [x] 5.2.1 CRUD de investimentos do mês
    - [x] 5.2.2 Tela de investimentos com visão anual meta × investido
    - [x] 5.2.3 Totais anuais (soma das metas e do investido)

### Sprint 6 — Pagamentos e Vendas Parcelados (`app_installments`) ✅

- [x] **6.1 — Models**
    - [x] 6.1.1 Criar app `app_installments`
    - [x] 6.1.2 Model `InstallmentPlan` (name, kind: payment/sale)
    - [x] 6.1.3 Model `Installment` (plan, financial_month, number, amount, status, receipt_url)
    - [x] 6.1.4 Métodos de resumo: pago, falta pagar, total
    - [x] 6.1.5 Migrações
- [x] **6.2 — Views e templates**
    - [x] 6.2.1 Criar plano com geração/distribuição de parcelas por mês
    - [x] 6.2.2 Listagem de planos (pagamentos e vendas)
    - [x] 6.2.3 Marcar parcela como paga e anexar link de comprovante
    - [x] 6.2.4 Exibir resumo pago/falta/total por plano

### Sprint 7 — Dashboard Consolidado (`app_dashboard`) ✅

- [x] **7.1 — Dashboard**
    - [x] 7.1.1 Criar app `app_dashboard`
    - [x] 7.1.2 Agregar dados do mês atual (cards de resumo)
    - [x] 7.1.3 Agregar visão anual (totais por mês)
    - [x] 7.1.4 Template do dashboard com grid de cards
    - [x] 7.1.5 Atalhos para mês, cartões, investimentos, parcelamentos e exportação

### Sprint 8 — Exportação para Excel (`app_exports`) ✅

- [x] **8.1 — Exportação**
    - [x] 8.1.1 Criar app `app_exports`
    - [x] 8.1.2 Adicionar `openpyxl` às dependências
    - [x] 8.1.3 Serviço que monta workbook em memória
    - [x] 8.1.4 Aba "Resumo Anual" (meta × investido e totais)
    - [x] 8.1.5 Abas por mês (entradas, saídas, despesas fixas, faturas, investimentos)
    - [x] 8.1.6 Aba "Cartões"
    - [x] 8.1.7 Abas "Pagamentos" e "Vendas"
    - [x] 8.1.8 Formatação (cabeçalhos escuros, texto branco)
    - [x] 8.1.9 View de download (`HttpResponse` com content-type xlsx)
    - [x] 8.1.10 Botão "Exportar Excel" no dashboard

### Sprint 9 — Finalização ✅

- [x] **10.1 — Qualidade**
    - [x] 10.1.1 Revisão geral de consistência visual entre telas
    - [x] 10.1.2 Revisão de isolamento de dados por usuário
    - [x] 10.1.3 Implementar testes (models, views, regras de negócio)
- [x] **10.2 — Infraestrutura**
    - [x] 10.2.1 Adicionar Docker (Dockerfile e docker-compose)
    - [x] 10.2.2 Preparar configuração para produção
    - [x] 10.2.3 Documentar setup no README

---
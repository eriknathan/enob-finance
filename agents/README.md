# Agentes de IA — EnobFinance

Time de desenvolvimento especializado na stack do projeto: **Python + Django full stack**, DTL, TailwindCSS, SQLite.

---

## Agentes disponíveis

| Agente | Arquivo | Especialidade |
|---|---|---|
| [Backend Django](#backend-django) | `backend.md` | Models, views, forms, business logic, auth, migrations |
| [Frontend DTL + Tailwind](#frontend-dtl--tailwind) | `frontend.md` | Templates, design system, componentes, UI moderna |
| [QA / Tester](#qa--tester) | `qa.md` | Testes funcionais e de design com Playwright |

---

## Backend Django

**Arquivo:** `backend.md`

Responsável por toda a camada de dados e lógica de negócio do Django: models, migrations, CBVs, forms, autenticação, regras de carry-over, isolamento por usuário e exportação Excel.

**Quando usar:**
- Criar ou modificar models e migrações
- Implementar CBVs (Create, Update, Delete, Detail, List)
- Escrever lógica de negócio (carry-over de saldo, cálculo de totais, distribuição de parcelas)
- Configurar autenticação por e-mail (Custom User)
- Implementar exportação para `.xlsx` com openpyxl
- Resolver erros de backend, ORM ou queries

---

## Frontend DTL + Tailwind

**Arquivo:** `frontend.md`

Responsável por toda a camada visual: templates HTML com DTL, componentes reutilizáveis, design system Enobtech, responsividade e experiência do usuário.

**Quando usar:**
- Criar ou refatorar templates HTML
- Implementar componentes (`templates/components/`)
- Aplicar o design system (cores, gradientes, tipografia Sora)
- Construir navegação (sidebar, topbar, carrossel de meses)
- Garantir responsividade (mobile, tablet, desktop)
- Qualquer tela nova ou ajuste visual

---

## QA / Tester

**Arquivo:** `qa.md`

Responsável por verificar que o sistema funciona como esperado e que o design está correto, acessando a aplicação em execução via Playwright.

**Quando usar:**
- Validar que uma feature implementada funciona no browser
- Verificar fluxos completos (login → dashboard → mês → lançamento)
- Confirmar que o design está aplicado corretamente na tela
- Identificar regressões após mudanças
- Testar responsividade em diferentes viewports

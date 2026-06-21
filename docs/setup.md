# Setup e Desenvolvimento

## Pré-requisitos

- Python 3.12+
- pip

## Instalação

```bash
# 1. Clonar o repositório
git clone <url-do-repositório>
cd enob-finance

# 2. Criar e ativar o virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Aplicar migrações
python manage.py migrate

# 5. Criar superusuário (opcional)
python manage.py createsuperuser

# 6. Rodar o servidor
python manage.py runserver
```

A aplicação estará disponível em `http://localhost:8000`.

---

## Dependências

Definidas em `requirements.txt`:

- `Django` — framework principal
- `openpyxl` — exportação para Excel

---

## Configurações relevantes (`settings.py`)

| Configuração | Valor |
|---|---|
| `LANGUAGE_CODE` | `pt-br` |
| `TIME_ZONE` | America/Sao_Paulo |
| Banco de dados | SQLite (padrão do Django) |
| `AUTH_USER_MODEL` | `app_accounts.User` |
| `TEMPLATES['DIRS']` | `[BASE_DIR / 'templates']` |

---

## Estrutura de pastas esperada

```
enob-finance/
  enobfinance/        # projeto Django (settings, urls, wsgi)
  app_core/
  app_accounts/
  app_months/
  app_cards/
  app_investments/
  app_installments/
  app_dashboard/
  app_exports/
  templates/          # todos os templates HTML na raiz
  docs/               # esta documentação
  requirements.txt
  manage.py
```

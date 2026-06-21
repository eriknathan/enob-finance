# Setup e Desenvolvimento

## Pré-requisitos

- Python 3.12+ (testado com 3.14)
- pip

## Instalação local

```bash
# 1. Clonar o repositório
git clone <url-do-repositório>
cd enob-finance

# 2. Criar e ativar o virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar o arquivo .env (opcional em desenvolvimento)
echo "SECRET_KEY=sua-chave-secreta-aqui" > .env

# 5. Aplicar migrações
python manage.py migrate

# 6. Criar superusuário (opcional)
python manage.py createsuperuser

# 7. Rodar o servidor
python manage.py runserver
```

A aplicação estará disponível em `http://localhost:8000`.

---

## Variáveis de ambiente (`.env`)

O projeto usa `python-dotenv` para carregar variáveis de um arquivo `.env` na raiz.

| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | valor insecure de dev | Chave secreta do Django |
| `DEBUG` | `True` | Ativar modo de depuração |
| `ALLOWED_HOSTS` | `*` | Hosts permitidos (separados por vírgula) |

Em produção, todas essas variáveis devem ser definidas no ambiente e `DEBUG` deve ser `False`.

---

## Dependências (`requirements.txt`)

| Pacote | Uso |
|---|---|
| `Django>=6.0` | Framework principal |
| `openpyxl>=3.1` | Exportação para Excel |
| `gunicorn>=21.0` | Servidor WSGI de produção |
| `psycopg2-binary>=2.9` | Driver PostgreSQL (produção) |
| `python-dotenv>=1.0` | Leitura do `.env` |

---

## Docker

Para rodar com Docker (Nginx + Gunicorn + SQLite):

```bash
# Criar o .env com a chave secreta
echo "SECRET_KEY=sua-chave-longa-e-aleatoria" > .env

# Subir os containers
docker-compose up --build
```

A aplicação ficará disponível em `http://localhost:8000` (porta configurável no `docker-compose.yml`).

O banco SQLite é persistido via bind mount (`./db.sqlite3`).

---

## Produção

```bash
export SECRET_KEY="<chave-longa-e-aleatoria>"
export ALLOWED_HOSTS="seudominio.com"
export DEBUG="False"
export DJANGO_SETTINGS_MODULE="enobfinance.settings_prod"

python manage.py migrate
python manage.py collectstatic --no-input
gunicorn enobfinance.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

`settings_prod.py` enforça `DEBUG=False`, flags de segurança em cookies, redirecionamento HTTPS e logging no console.

---

## Configurações relevantes (`settings.py`)

| Configuração | Valor |
|---|---|
| `LANGUAGE_CODE` | `pt-br` |
| `TIME_ZONE` | `America/Sao_Paulo` |
| `AUTH_USER_MODEL` | `app_accounts.User` |
| `TEMPLATES['DIRS']` | `[BASE_DIR / 'templates']` |
| Banco de dados | SQLite (desenvolvimento) |

---

## Estrutura de pastas

```
enob-finance/
  enobfinance/          # projeto Django (settings, urls, wsgi, asgi)
  app_core/             # base abstrata e utilitários
  app_accounts/         # autenticação
  app_months/           # mês financeiro
  app_cards/            # cartões e faturas
  app_investments/      # investimentos
  app_installments/     # parcelamentos
  app_dashboard/        # dashboard
  app_exports/          # exportação Excel
  templates/            # todos os templates HTML na raiz
  static/               # arquivos estáticos
  docs/                 # documentação
  nginx/                # configuração Nginx (Docker)
  requirements.txt
  manage.py
  Makefile
  Dockerfile
  docker-compose.yml
```

---

## Comandos úteis (Makefile)

```bash
make              # ver comandos disponíveis
make run          # python manage.py runserver
make migrate      # python manage.py migrate
make migrations   # python manage.py makemigrations
make shell        # python manage.py shell
```

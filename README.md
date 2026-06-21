# EnobFinance

Gerenciador de finanças pessoais construído com Python + Django full stack. Parte do ecossistema Enob.

## Funcionalidades

- **Orçamento mensal** — cada mês é uma página própria com entradas, gastos variáveis e despesas fixas
- **Continuidade de saldo** — o saldo final do mês N vira automaticamente o saldo inicial do mês N+1
- **Faturas de cartão** — registre o valor de cada fatura por cartão e por mês
- **Investimentos com meta** — lance investimentos e defina uma meta mensal; visão anual mostra meta × realizado
- **Simulador de rendimento** — calcule projeções com base em CDI e outras taxas
- **Parcelamentos** — gerencie planos parcelados de pagamento, venda ou empréstimo; marque cada parcela como paga e anexe comprovante por link
- **Dashboard** — visão consolidada mensal e anual com gráficos
- **Exportação Excel** — baixe um `.xlsx` completo com resumo anual, abas por mês, cartões e planos de parcelamento
- **Multi-usuário** — cada usuário enxerga apenas seus próprios dados; autenticação por e-mail

## Pré-requisitos

- Python 3.12+ (testado com 3.14)
- pip

## Setup local

```bash
# 1. Clonar o repositório
git clone <url-do-repositório>
cd enob-finance

# 2. Criar e ativar o virtualenv
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Aplicar migrações
python manage.py migrate

# 5. Criar superusuário
python manage.py createsuperuser

# 6. Iniciar o servidor
python manage.py runserver
```

Acesse http://localhost:8000 no navegador.

## Docker

```bash
# Criar o .env com a chave secreta
echo "SECRET_KEY=sua-chave-longa-e-aleatoria" > .env

# Subir os containers (Nginx + Gunicorn)
docker-compose up --build
```

A aplicação ficará disponível em http://localhost:8000. O banco SQLite é persistido via bind mount (`./db.sqlite3`).

## Produção

Defina as variáveis de ambiente e aponte para o módulo de configurações de produção:

```bash
export SECRET_KEY="<chave-longa-e-aleatoria>"
export ALLOWED_HOSTS="seudominio.com"
export DEBUG="False"
export DJANGO_SETTINGS_MODULE="enobfinance.settings_prod"

python manage.py migrate
python manage.py collectstatic --no-input
gunicorn enobfinance.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

`settings_prod.py` enforça `DEBUG=False`, flags de segurança em cookies e redirecionamento HTTPS.

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12+, Django 6.x |
| Frontend | Django Template Language, TailwindCSS (CDN) |
| Banco de dados | SQLite (dev) / PostgreSQL (produção) |
| Exportação Excel | openpyxl |
| Servidor de produção | Gunicorn + Nginx |
| Containerização | Docker / docker-compose |

## Documentação

Veja [`docs/`](docs/) para arquitetura, padrões de código, modelos de dados, design system e setup detalhado.

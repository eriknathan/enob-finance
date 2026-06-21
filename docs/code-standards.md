# Padrões de Código

## Idioma

- **Código** (variáveis, funções, classes, arquivos, comentários): inglês.
- **Interface do usuário** (labels, mensagens, textos em templates): português brasileiro.

## Estilo

- Aspas simples sempre que possível.
- Class Based Views (CBVs) — preferir `DetailView`, `CreateView`, `UpdateView`, `DeleteView`, `ListView`, `TemplateView`, `RedirectView` e mixins nativos do Django.
- Views via função (`def`) apenas quando estritamente necessário (ex.: ações simples como toggle de status).
- Sem over-engineering: apenas o solicitado, sem abstrações antecipadas.
- Sem comentários óbvios — adicionar apenas quando o "por que" não é evidente pelo código.

## Models

- Todo model herda de `TimestampedModel` (definido em `app_core`), que fornece `created_at` e `updated_at`.
- Valores derivados (totais, saldos) são **calculados** via métodos/propriedades — nunca armazenados.
- Isolamento obrigatório: toda query filtra pelo `user` autenticado.

## Apps

- Prefixo `app_` em todos os apps Django.
- Cada app cobre um único domínio de negócio.
- Signals ficam em `signals.py` dentro da app correspondente.
- Template tags compartilhadas ficam em `app_core/templatetags/`.

## Dependências externas

O projeto prioriza recursos nativos do Django. As bibliotecas externas são:

- `openpyxl` — exportação Excel.
- `gunicorn` — servidor WSGI de produção.
- `psycopg2-binary` — driver PostgreSQL (produção).
- `python-dotenv` — leitura de variáveis de ambiente de `.env`.
- Lib de OAuth do Google — login social (sprint posterior).

## Segurança

- Proteção CSRF nativa do Django habilitada.
- Rotas protegidas com `LoginRequiredMixin`.
- Nenhuma query sem filtro por usuário.
- Chave secreta e configurações sensíveis via variáveis de ambiente (`.env`).

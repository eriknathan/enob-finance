# Infisical — Gerenciamento de Segredos

O EnobFinance usa o [Infisical](https://infisical.com) como cofre centralizado de segredos. Em vez de cadastrar variável por variável no GitHub Secrets, todos os segredos de produção vivem no Infisical e são injetados automaticamente no deploy via GitHub Action.

---

## Por que Infisical?

| Problema (antes) | Solução (depois) |
|---|---|
| Cada segredo precisava ser cadastrado manualmente no GitHub | Um único lugar para gerenciar todos os segredos |
| Adicionar uma nova variável exigia atualizar o workflow e o GitHub | Basta adicionar no Infisical — o deploy pega automaticamente |
| Sem histórico de quem alterou qual segredo | Audit log centralizado no Infisical |
| Difícil sincronizar entre ambientes (dev/staging/prod) | Ambientes separados dentro do mesmo projeto |

---

## Como funciona no pipeline

```
Push para main
      │
      ▼
   [test]  ──────── roda os testes com PostgreSQL
      │
      ▼
[build-push] ───── builda a imagem Docker e faz push para o GHCR
      │
      ▼
  [deploy]  ───── roda no runner self-hosted (vps-enob)
      │
      ├─ 1. Infisical Action busca todos os segredos → grava .env
      ├─ 2. Variáveis específicas de deploy são ADICIONADAS ao .env (>>)
      ├─ 3. docker compose pull web
      ├─ 4. docker compose up -d --force-recreate
      └─ 5. docker image prune -f
```

### O step de segredos em detalhe

```yaml
- name: Buscar segredos do Infisical
  uses: Infisical/secrets-action@v1.0.0
  with:
    client-id: ${{ secrets.INFISICAL_CLIENT_ID }}
    client-secret: ${{ secrets.INFISICAL_CLIENT_SECRET }}
    domain: "https://infisical.seudominio.com/api"
    project-slug: "enob-finance"
    env-slug: "prod"
    export-type: "file"
    file-output-path: ".env"

- name: Ajustar variáveis específicas do deploy
  run: |
    {
      echo "DB_HOST=db"
      echo "DB_PORT=5432"
      echo "IMAGE=${{ env.IMAGE }}:main-${{ github.run_number }}"
    } >> .env
```

- O Infisical Action autentica com `client-id` + `client-secret`, acessa o projeto `enob-finance` no ambiente `prod` e **grava** o `.env` com todos os segredos.
- O step seguinte usa `>>` (append) — nunca `>` — para adicionar as três variáveis de infraestrutura sem apagar o que o Infisical escreveu.
- `DB_HOST=db` aponta para o serviço Docker interno (não o `localhost` usado nos testes).
- `IMAGE` é calculado em runtime com o número do run para garantir que o deploy sempre use a imagem recém-buildada.

---

## Configuração inicial

### 1. Criar conta e projeto no Infisical

1. Acesse [app.infisical.com](https://app.infisical.com) (cloud) ou instale a versão self-hosted.
2. Crie um novo projeto com o slug `enob-finance`.
3. Dentro do projeto, vá em **Environments** e confirme que o ambiente `prod` existe (é criado por padrão).

### 2. Adicionar os segredos em produção

No Infisical, vá em **Secrets → prod** e adicione todas as variáveis de ambiente da aplicação:

| Variável | Descrição |
|---|---|
| `DEBUG` | `False` em produção |
| `SECRET_KEY` | Chave secreta do Django (gere com `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `ALLOWED_HOSTS` | Domínio da aplicação (ex: `finance.seudominio.com`) |
| `CSRF_TRUSTED_ORIGINS` | `https://finance.seudominio.com` |
| `SECURE_SSL_REDIRECT` | `True` |
| `SECURE_HSTS_SECONDS` | `31536000` |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | `True` |
| `DB_NAME` | Nome do banco de dados |
| `DB_USER` | Usuário do banco |
| `DB_PASSWORD` | Senha do banco |

> `DB_HOST` e `DB_PORT` são injetados pelo workflow (não precisam estar no Infisical).

### 3. Criar uma Machine Identity para o GitHub Actions

1. No Infisical, vá em **Access Control → Machine Identities**.
2. Clique em **Create identity** e dê o nome `github-actions`.
3. Selecione o método de autenticação **Universal Auth**.
4. Copie o `Client ID` e o `Client Secret` gerados.
5. Ainda em Machine Identities, abra a identidade criada e vá em **Project Access**.
6. Adicione o projeto `enob-finance` com a role `viewer` (somente leitura é suficiente).

### 4. Cadastrar as credenciais no GitHub

No repositório do GitHub, vá em **Settings → Secrets and variables → Actions** e adicione:

| Secret | Valor |
|---|---|
| `INFISICAL_CLIENT_ID` | O Client ID gerado no passo anterior |
| `INFISICAL_CLIENT_SECRET` | O Client Secret gerado no passo anterior |

> Esses são os únicos dois segredos que precisam estar no GitHub. Todos os outros vivem no Infisical.

### 5. Atualizar o `domain` no workflow

Se você usa o Infisical Cloud, substitua o `domain` no workflow pelo endpoint oficial:

```yaml
domain: "https://app.infisical.com/api"
```

Se usa self-hosted, aponte para o seu domínio:

```yaml
domain: "https://infisical.seudominio.com/api"
```

---

## Self-hosted vs Cloud

| | Cloud (`app.infisical.com`) | Self-hosted |
|---|---|---|
| Custo | Gratuito até certo limite | Custo de infraestrutura |
| Controle | Gerenciado pela Infisical | Total |
| Configuração | Imediata | Requer deploy (Docker Compose disponível) |
| Audit log | Sim | Sim |

Para o EnobFinance, o cloud é suficiente e elimina a necessidade de manter mais um serviço.

---

## Rotação de segredos

1. Atualize o valor no Infisical (Secrets → prod → edite a variável).
2. O próximo deploy já pega o valor novo automaticamente — sem tocar no workflow ou no GitHub.

Para rotacionar o `INFISICAL_CLIENT_SECRET`:
1. No Infisical, vá em **Machine Identities → github-actions → Client Secrets**.
2. Gere um novo secret e adicione ao GitHub antes de revogar o antigo.
3. Após confirmar que o pipeline roda com sucesso, revogue o secret antigo.

---

## Referências

- [Documentação oficial do Infisical](https://infisical.com/docs)
- [GitHub Action `Infisical/secrets-action`](https://github.com/Infisical/secrets-action)
- [Self-hosted — Docker Compose](https://infisical.com/docs/self-hosting/deployment-options/docker-compose)

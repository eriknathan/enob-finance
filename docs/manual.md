# Manual de Uso — EnobFinance

EnobFinance é um gerenciador de finanças pessoais organizado por mês. A ideia central é simples: cada mês é uma "página" própria com estrutura idêntica — entradas, gastos variáveis, despesas fixas, faturas de cartão e investimentos. O saldo de um mês passa automaticamente para o próximo, formando um histórico contínuo sem retrabalho.

---

## Índice

1. [Primeiros passos](#1-primeiros-passos)
2. [Dashboard](#2-dashboard)
3. [Mês Financeiro](#3-mês-financeiro)
4. [Cartões de Crédito](#4-cartões-de-crédito)
5. [Investimentos](#5-investimentos)
6. [Parcelamentos](#6-parcelamentos)
7. [Exportação para Excel](#7-exportação-para-excel)
8. [Conceitos e regras do sistema](#8-conceitos-e-regras-do-sistema)

---

## 1. Primeiros passos

### Criar uma conta

Acesse `/conta/registro/` e preencha seu e-mail e senha. O sistema usa e-mail como identificador — não há campo de username.

### Fazer login

Acesse `/conta/login/` com e-mail e senha. Ao entrar, você é redirecionado automaticamente ao **Dashboard**.

### Navegar pelo sistema

A **sidebar** (barra lateral esquerda) é o ponto de partida para todas as seções:

| Item da sidebar | O que abre |
|---|---|
| Dashboard | Visão consolidada do ano |
| Meses | Mês financeiro atual |
| Cartões | Lista de cartões de crédito |
| Investimentos | Visão anual de investimentos |
| Parcelamentos | Planos de parcelamento |
| Exportar | Download do arquivo Excel |

---

## 2. Dashboard

**URL:** `/dashboard/`

O Dashboard é a tela inicial após o login. Ela mostra um panorama financeiro do ano selecionado.

### O que você vê

- **Tabela anual** — uma linha por mês, com colunas de entradas, gastos variáveis, despesas fixas, faturas, investimentos e saldo
- **Gráficos** — visualização mensal de entradas vs. saídas, evolução do saldo e investimentos
- **Cards de resumo** — totais consolidados do ano (soma de entradas, despesas, investimentos)

### Navegar entre anos

Use as setas ao lado do ano exibido, ou adicione `?ano=2025` na URL para ir direto a um ano específico.

### Clicar em um mês

Qualquer linha da tabela ou coluna do gráfico leva ao detalhe do mês correspondente.

---

## 3. Mês Financeiro

**URL:** `/meses/<ano>/<mês>/` (ex.: `/meses/2026/6/`)

Esta é a tela principal do sistema. Cada mês tem sua própria página com o mesmo template, dividida em seções:

### Carrossel de meses

Na parte superior da tela, uma barra horizontal exibe os 12 meses do ano como pílulas clicáveis. O mês ativo fica destacado em azul. Use as setas para navegar entre anos.

### Cards de resumo

Seis indicadores no topo resumem o mês:

| Card | O que mostra |
|---|---|
| **Saldo atual** | Balanço final: saldo anterior + entradas − despesas − investimentos |
| **Entradas** | Soma de todas as receitas do mês |
| **Gastos Var.** | Soma dos gastos variáveis |
| **Despesas Fixas** | Soma das despesas fixas mensais |
| **Investido** | Soma dos investimentos do mês |
| **Faturas** | Soma das faturas de cartão |

> O **Saldo atual** leva em conta o saldo do mês anterior automaticamente. Se o mês anterior não existir, considera-se zero.

---

### 3.1 Entradas

Receitas do mês: salário, rendimentos, freelas, restituição de imposto, etc.

**Campos:**
- **Descrição** — nome da receita
- **Valor** — valor em R$
- **Data** — data em que a entrada ocorreu

**Como usar:**
1. Clique em **Adicionar** no cabeçalho da seção
2. Preencha descrição, valor e data
3. Salve — o saldo recalcula automaticamente

> A linha **"Saldo do mês anterior"** aparece automaticamente no topo da lista de entradas, sem necessidade de cadastro manual.

---

### 3.2 Gastos Variáveis

Despesas que variam de mês para mês: supermercado, restaurantes, transporte, farmácia, etc.

**Campos:**
- **Descrição** — o que foi gasto
- **Valor** — valor em R$
- **Data** — data da compra ou pagamento

**Como usar:**
1. Clique em **Adicionar**
2. Preencha os campos
3. Salve — o resumo atualiza imediatamente

---

### 3.3 Despesas Fixas

Contas e compromissos mensais de valor fixo ou previsível: aluguel, internet, energia, plano de saúde, assinaturas, etc.

**Campos:**
- **Descrição** — nome da despesa
- **Valor** — valor em R$
- **Status** — `Pago` ou `Não pago`

**Marcar como pago:**
Clique diretamente na pílula de status na tabela. Ela alterna entre **Pago** (verde) e **Não pago** (vermelho) sem precisar abrir o formulário.

> As faturas de cartão aparecem automaticamente nessa seção como uma linha agrupada **"Faturas de Cartão (Automático)"**, sem status individual — elas são gerenciadas na seção de Faturas.

---

### 3.4 Faturas de Cartão

Registra o valor total da fatura de cada cartão no mês. Cada cartão pode ter apenas uma fatura por mês.

**Campos:**
- **Cartão** — seleciona entre seus cartões cadastrados
- **Valor** — valor total da fatura
- **Status** — `Pago` ou `Não pago`

**Marcar como paga:**
Clique na pílula de status na linha da fatura — ela alterna instantaneamente.

> Para adicionar faturas, os cartões devem estar cadastrados previamente em **Cartões → Novo Cartão**.

---

### 3.5 Investimentos

Registra tudo que foi investido no mês, por ativo ou instituição.

**Campos:**
- **Onde** — nome do ativo, banco ou fundo (ex.: "CDB Nubank 110% CDI", "IVVB11")
- **Valor** — valor aportado em R$
- **Data** — data do aporte

**Meta de investimento:**
Use o botão **Meta** para definir quanto quer investir no mês. A tela de Investimentos Anuais compara essa meta com o realizado.

---

### 3.6 Configurar Período

No topo da página do mês, o botão **Configurar Período** permite definir as datas de início e fim do mês (opcional). Útil para registrar um período customizado, como um mês fiscal diferente do calendário.

---

## 4. Cartões de Crédito

**URL:** `/cartoes/`

Gerencia os cartões de crédito cadastrados. Esses cartões aparecem no seletor de faturas dentro de cada mês.

### Cadastrar um cartão

Clique em **Novo Cartão** e preencha:

| Campo | Descrição |
|---|---|
| **Nome** | Nome do cartão (ex.: "Nubank Ultravioleta") |
| **Bandeira** | Visa, Mastercard, Elo, American Express, Hipercard ou Outros |
| **Dia de fechamento** | Dia do mês em que a fatura fecha |
| **Dia de vencimento** | Dia do mês em que a fatura vence |

### Detalhe do cartão

Clique em **Detalhes** no card de um cartão para ver:
- **Histórico de faturas** — todas as faturas registradas, por mês
- **Gráfico de evolução** — valor das últimas 12 faturas em linha do tempo

---

## 5. Investimentos

**URL:** `/investimentos/`

Visão anual dos investimentos: meta definida × valor efetivamente investido.

### Tabela anual

Uma linha por mês com três colunas:
- **Meta** — valor definido no mês financeiro
- **Investido** — soma dos aportes do mês
- **Diferença** — investido − meta (positivo = superou, negativo = ficou abaixo)
- **% da meta** — percentual atingido

### Gráficos

Barras lado a lado comparando meta e investido em cada mês do ano.

### Navegar entre anos

Use as setas ao lado do ano para ver histórico de anos anteriores ou próximos.

### Simulador de Rendimento

**URL:** `/investimentos/simulador/`

Acessível pela sidebar ou pelo menu de investimentos. Permite simular quanto um valor cresce ao longo do tempo com base em uma taxa (ex.: % do CDI).

---

## 6. Parcelamentos

**URL:** `/parcelamentos/`

Gerencia compras, vendas e empréstimos divididos em parcelas mensais.

### Tipos de plano

| Tipo | Efeito no saldo | Exemplo |
|---|---|---|
| **Pagamento** | Saída (despesa) | Compra de notebook em 12x |
| **Venda** | Entrada (receita) | Venda de eletrônico usado em 6x |
| **Empréstimo** | Entrada esperada (recebimento) | Dinheiro emprestado a um amigo |

> O tipo define como as parcelas aparecem no resumo do mês em que estão associadas.

### Criar um plano

1. Clique em **Novo Plano**
2. Informe nome e tipo (`Pagamento`, `Venda` ou `Empréstimo`)
3. Defina a quantidade de parcelas, o valor de cada uma e o mês inicial
4. Salve — as parcelas são criadas automaticamente e distribuídas pelos meses

### Detalhe do plano

Exibe todas as parcelas com:
- **Número da parcela** — ex.: `3/12`
- **Mês de referência** — mês em que a parcela está associada
- **Valor** — valor da parcela
- **Status** — `Pago` ou `Pendente`
- **Comprovante** — link (ex.: Google Drive) do recibo ou transferência

### Marcar parcela como paga

Clique no botão **Pagar** na linha da parcela. Uma janela confirma a ação e permite colar o link do comprovante antes de salvar.

### Resumo do plano

No cabeçalho da página de detalhe:
- **Total** — soma de todas as parcelas
- **Pago** — soma das parcelas com status "pago"
- **Restante** — total − pago
- **Progresso** — `3/12 parcelas pagas`

---

## 7. Exportação para Excel

**URL:** `/exportar/`

Gera e baixa um arquivo `.xlsx` com todos os dados do usuário autenticado.

### Abas geradas

| Aba | Conteúdo |
|---|---|
| **Resumo Anual** | Uma linha por mês com entradas, gastos, faturas, investimentos, meta e saldo |
| **Jan-25, Fev-25…** | Uma aba por mês com todas as seções (entradas, gastos, fixas, faturas, investimentos, parcelamentos e resumo) |
| **Cartões** | Lista de cartões com bandeira, fechamento e vencimento |
| **Pagamentos** | Planos de parcelamento do tipo pagamento com detalhamento por parcela |
| **Vendas** | Planos de parcelamento do tipo venda |
| **Empréstimos** | Planos de parcelamento do tipo empréstimo |

### Formatação do arquivo

- Valores monetários em formato `R$ #.###,##`
- Datas no formato `DD/MM/AAAA`
- Saldo positivo em **verde**, negativo em **vermelho**
- Status de parcelas e faturas coloridos (verde = pago, vermelho = pendente)
- Linhas alternadas em cinza claro para facilitar leitura
- Filtro automático no resumo anual

> O arquivo é gerado em memória e baixado imediatamente. Nenhum arquivo é salvo no servidor.

---

## 8. Conceitos e regras do sistema

### Continuidade de saldo

O **saldo final** de um mês é calculado como:

```
saldo atual = saldo anterior + entradas − (gastos variáveis + despesas fixas + faturas) − investimentos
```

Esse saldo aparece automaticamente como **"Saldo do mês anterior"** no próximo mês, sem necessidade de lançamento manual. Se o mês anterior não existir no sistema, o saldo inicial é zero.

### Valores nunca armazenados

Totais, saldos e percentuais são **sempre calculados em tempo real** a partir dos lançamentos. Editar ou excluir qualquer lançamento recalcula tudo instantaneamente.

### Isolamento por usuário

Cada usuário enxerga **apenas seus próprios dados**. Não há compartilhamento de meses, cartões ou planos entre contas diferentes.

### Comprovantes por link

O sistema não armazena arquivos. Para comprovantes, cole o link do arquivo no Google Drive, Dropbox ou qualquer serviço de armazenamento. O link fica salvo e clicável na tabela de parcelas.

### Meta de investimento

A meta é um valor-alvo que você define por mês. O valor **investido** é automaticamente a soma dos aportes lançados naquele mês — não é um campo editável separado. A tela anual de investimentos compara os dois.

### Faturas de cartão no mês

O valor total das faturas de todos os cartões do mês é tratado como uma despesa fixa especial — aparece agrupado na seção **Despesas Fixas** como "Faturas de Cartão (Automático)" e entra no cálculo do total de saídas do mês.

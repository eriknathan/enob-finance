# Design System

Identidade visual **dark premium** com gradientes harmônicos, construída inteiramente com TailwindCSS dentro do Django Template Language. Base nos tokens do Design System Enobtech.

---

## Cores

### Primárias e de marca

| Token | Hex | Uso |
|---|---|---|
| `brand-blue` | `#0066FF` | Botões, links, destaques, ícones |
| `brand-blue-light` | `#00AAFF` | Final do gradiente primário |
| `brand-dark` | `#000918` | Fundo dark premium, cabeçalhos, sidebar |
| `brand-surface` | `#0A1428` | Superfícies elevadas no dark (cards) |
| `brand-gray-dark` | `#454D60` | Texto secundário |

### Apoio e estado

| Token | Hex | Uso |
|---|---|---|
| `gray-200` | `#E5E7EB` | Bordas de inputs, divisores |
| `gray-500` | `#6B7280` | Texto terciário / placeholder |
| `green-400` | `#22C55E` | Estado positivo (pago, saldo positivo) |
| `red-400` | `#EF4444` | Estado negativo (não pago, saldo negativo) |
| `yellow-400` | `#FBBF24` | Alertas e destaques |

### Gradientes

| Nome | Classe Tailwind |
|---|---|
| Gradiente primário (botões) | `bg-gradient-to-r from-[#0066FF] to-[#00AAFF]` |
| Gradiente de título | `bg-gradient-to-r from-[#0066FF] to-[#00AAFF] bg-clip-text text-transparent` |
| Card premium (saldo) | `bg-gradient-to-br from-[#0A1428] to-[#000918]` |

---

## Tipografia

| Propriedade | Valor |
|---|---|
| Família | **Sora**, sans-serif (`font-['Sora']`) |
| Títulos de tela | `text-3xl font-bold` |
| Títulos de card | `text-lg font-semibold` |
| Corpo | `text-base font-normal` |
| Labels | `text-sm font-medium` |

---

## Botões

```html
<!-- Primário -->
<button class='inline-flex items-center gap-2 px-6 py-3 rounded-xl
               bg-gradient-to-r from-[#0066FF] to-[#00AAFF] text-white
               text-sm font-semibold shadow-lg shadow-blue-500/25
               hover:shadow-blue-500/40 transition-all'>
  Salvar
</button>

<!-- Secundário (ghost) -->
<button class='inline-flex items-center gap-2 px-6 py-3 rounded-xl
               border border-gray-200 text-gray-700 text-sm font-medium
               hover:bg-gray-50 transition-all'>
  Cancelar
</button>

<!-- Destrutivo -->
<button class='px-4 py-2 rounded-lg bg-red-50 text-red-600 text-sm
               font-medium hover:bg-red-100 transition-all'>
  Excluir
</button>
```

---

## Inputs e Forms

```html
<div class='flex flex-col gap-1.5'>
  <label class='text-sm font-medium text-[#000918]'>Descrição</label>
  <input type='text'
         class='w-full px-4 py-3 rounded-lg bg-gray-50 border border-gray-200
                text-[#454D60] text-base placeholder-gray-400
                focus:border-[#0066FF] focus:ring-2 focus:ring-blue-100
                outline-none transition-all'
         placeholder='Ex.: Salário'>
</div>
```

- Layout vertical com `gap-4`, label acima do input.
- Erros de validação: `text-sm text-red-500` abaixo do campo.

---

## Cards

```html
<!-- Card padrão -->
<div class='rounded-2xl bg-white border border-gray-100 shadow-sm p-6'>
  <h3 class='text-lg font-semibold text-[#000918] mb-4'>Título</h3>
</div>

<!-- Card de destaque (saldo) -->
<div class='rounded-2xl bg-gradient-to-br from-[#0A1428] to-[#000918]
            text-white p-6 shadow-xl'>
  <p class='text-sm text-white/60'>Saldo atual</p>
  <p class='text-3xl font-bold'>R$ 0,00</p>
</div>
```

---

## Grids

| Contexto | Classe Tailwind |
|---|---|
| Cards de resumo | `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4` |
| Conteúdo do mês | `grid grid-cols-1 lg:grid-cols-2 gap-6` |
| Container máximo | `max-w-screen-2xl mx-auto px-6 md:px-10 xl:px-16` |
| Tabelas | `w-full overflow-x-auto` com `min-w-full` interno |

---

## Navegação

- **Sidebar** (desktop): `bg-[#000918] text-white/70`, largura fixa, links com `hover:bg-white/5 rounded-lg`, item ativo com gradiente azul.
- **Topbar**: `h-[68px] bg-white/90 backdrop-blur border-b border-gray-200`.
- **Carrossel de meses**: barra horizontal com pílulas `rounded-full`, mês ativo em gradiente azul, setas anterior/próximo.

---

## Status Pills

```html
<span class='px-3 py-1 rounded-full bg-green-50 text-green-600 text-xs font-semibold'>Pago</span>
<span class='px-3 py-1 rounded-full bg-red-50 text-red-600 text-xs font-semibold'>Não pago</span>
```

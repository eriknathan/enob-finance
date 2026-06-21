"""
Script de dados mockados para desenvolvimento e demonstração do EnobFinance.

Cobre todos os modelos e campos do sistema com dados realistas em BRL:
  - 12 meses de histórico financeiro
  - Múltiplas entradas, gastos variáveis e despesas fixas por mês
  - 4 cartões de crédito com faturas e status variados
  - Investimentos mensais em diferentes ativos com meta definida
  - Planos de parcelamento dos 3 tipos: pagamento, venda e empréstimo

Uso:
    python mock_data.py

Login gerado: demo@enob.com / demo123
"""

import os
import sys
import django
import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enobfinance.settings')
django.setup()

from django.contrib.auth import get_user_model
from app_months.models import FinancialMonth, Entry, VariableExpense, FixedExpense
from app_cards.models import Card, CardInvoice
from app_investments.models import Investment
from app_installments.models import InstallmentPlan, Installment

User = get_user_model()

EMAIL = 'demo@enob.com'
PASSWORD = 'demo123'

TODAY = datetime.date.today()


def _month_offset(base_year, base_month, offset):
    """Returns (year, month) after applying a month offset (can be negative)."""
    m = base_month + offset
    y = base_year
    while m <= 0:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    return y, m


def _last_day(year, month):
    import calendar
    return calendar.monthrange(year, month)[1]


def _d(year, month, day):
    last = _last_day(year, month)
    return datetime.date(year, month, min(day, last))


def _clean(user):
    print('  Limpando dados existentes...')
    FinancialMonth.objects.filter(user=user).delete()
    Card.objects.filter(user=user).delete()
    InstallmentPlan.objects.filter(user=user).delete()


def create_user():
    user, created = User.objects.get_or_create(email=EMAIL)
    user.set_password(PASSWORD)
    user.save()
    status = 'criado' if created else 'atualizado'
    print(f'Usuário {status}: {EMAIL} / {PASSWORD}')
    return user


def create_cards(user):
    cards = [
        Card.objects.create(
            user=user, name='Nubank Ultravioleta', brand='Mastercard',
            closing_day=25, due_day=5,
        ),
        Card.objects.create(
            user=user, name='Itaú Click', brand='Visa',
            closing_day=15, due_day=25,
        ),
        Card.objects.create(
            user=user, name='XP Visa Infinite', brand='Visa',
            closing_day=10, due_day=20,
        ),
        Card.objects.create(
            user=user, name='Amex Gold', brand='American Express',
            closing_day=20, due_day=2,
        ),
    ]
    print(f'  {len(cards)} cartões criados.')
    return cards


def create_months(user, cards):
    """Cria 12 meses de histórico financeiro com dados completos."""

    nubank, itau, xp, amex = cards

    # Dados variáveis por mês para simular realidade (offset 0 = mês atual)
    month_configs = [
        # offset, investment_goal, bonus_entry, freelance_amount, extra_variable
        (-11, Decimal('400.00'), False, None, False),
        (-10, Decimal('400.00'), False, None, False),
        (-9,  Decimal('500.00'), False, Decimal('800.00'), False),
        (-8,  Decimal('500.00'), True,  None, True),
        (-7,  Decimal('600.00'), False, None, False),
        (-6,  Decimal('600.00'), False, Decimal('1500.00'), False),
        (-5,  Decimal('700.00'), True,  None, True),
        (-4,  Decimal('700.00'), False, None, False),
        (-3,  Decimal('800.00'), False, Decimal('2000.00'), False),
        (-2,  Decimal('800.00'), False, None, True),
        (-1,  Decimal('900.00'), True,  Decimal('1200.00'), False),
        (0,   Decimal('1000.00'), False, None, False),
    ]

    months_map = {}  # (year, month) -> FinancialMonth

    for offset, goal, has_bonus, freelance, has_extra_var in month_configs:
        year, month = _month_offset(TODAY.year, TODAY.month, offset)
        last = _last_day(year, month)
        is_past = (year, month) < (TODAY.year, TODAY.month)
        is_current = (year, month) == (TODAY.year, TODAY.month)

        fm = FinancialMonth.objects.create(
            user=user,
            year=year,
            month=month,
            investment_goal=goal,
            start_date=_d(year, month, 1),
            end_date=_d(year, month, last),
        )
        months_map[(year, month)] = fm

        # ── Entradas ──────────────────────────────────────────────────────────
        Entry.objects.create(
            financial_month=fm,
            description='Salário Líquido',
            amount=Decimal('7200.00'),
            date=_d(year, month, 5),
        )
        Entry.objects.create(
            financial_month=fm,
            description='Rendimento CDB',
            amount=Decimal('38.50'),
            date=_d(year, month, last),
        )
        Entry.objects.create(
            financial_month=fm,
            description='Rendimento Tesouro Direto',
            amount=Decimal('22.10'),
            date=_d(year, month, last),
        )
        if has_bonus:
            Entry.objects.create(
                financial_month=fm,
                description='Bônus de Desempenho',
                amount=Decimal('3500.00'),
                date=_d(year, month, 10),
            )
        if freelance:
            Entry.objects.create(
                financial_month=fm,
                description='Freela — Design de Interface',
                amount=freelance,
                date=_d(year, month, 18),
            )

        # ── Gastos Variáveis ──────────────────────────────────────────────────
        variable_base = [
            ('Supermercado Extra', Decimal('680.00'), 8),
            ('Supermercado (2ª ida)', Decimal('320.00'), 22),
            ('iFood / Delivery', Decimal('195.00'), 14),
            ('Restaurantes', Decimal('280.00'), 20),
            ('Uber / 99', Decimal('110.00'), 17),
            ('Farmácia', Decimal('95.40'), 12),
            ('Combustível', Decimal('250.00'), 6),
            ('Estacionamento', Decimal('48.00'), 15),
            ('Streaming (extra)', Decimal('29.90'), 5),
        ]
        for desc, amount, day in variable_base:
            VariableExpense.objects.create(
                financial_month=fm,
                description=desc,
                amount=amount,
                date=_d(year, month, day),
            )
        if has_extra_var:
            VariableExpense.objects.create(
                financial_month=fm,
                description='Viagem de Fim de Semana',
                amount=Decimal('850.00'),
                date=_d(year, month, 25),
            )
            VariableExpense.objects.create(
                financial_month=fm,
                description='Compra de Roupas',
                amount=Decimal('420.00'),
                date=_d(year, month, 26),
            )

        # ── Despesas Fixas ────────────────────────────────────────────────────
        fixed_expenses = [
            ('Aluguel', Decimal('2200.00'), 'paid'),
            ('Condomínio', Decimal('380.00'), 'paid'),
            ('Internet Fibra 1 Gbs', Decimal('149.90'), 'paid'),
            ('Energia Elétrica', Decimal('210.00'), 'paid' if is_past else 'unpaid'),
            ('Água e Esgoto', Decimal('78.50'), 'paid' if is_past else 'unpaid'),
            ('Plano de Saúde', Decimal('580.00'), 'paid'),
            ('Academia Smart Fit', Decimal('89.90'), 'paid'),
            ('Spotify Premium Família', Decimal('34.90'), 'paid'),
            ('Netflix 4K', Decimal('55.90'), 'paid'),
            ('YouTube Premium', Decimal('27.90'), 'paid'),
            ('iCloud 200 GB', Decimal('9.90'), 'paid'),
            ('Seguro do Carro', Decimal('195.00'), 'paid' if is_past else 'unpaid'),
        ]
        for desc, amount, status in fixed_expenses:
            FixedExpense.objects.create(
                financial_month=fm,
                description=desc,
                amount=amount,
                status=status,
            )

        # ── Faturas de Cartão ─────────────────────────────────────────────────
        invoice_data = [
            (nubank,  Decimal('1850.00')),
            (itau,    Decimal('620.00')),
            (xp,      Decimal('430.00')),
            (amex,    Decimal('280.00')),
        ]
        for card, amount in invoice_data:
            inv_status = 'paid' if is_past else 'unpaid'
            CardInvoice.objects.create(
                card=card,
                financial_month=fm,
                amount=amount,
                status=inv_status,
            )

        # ── Investimentos ─────────────────────────────────────────────────────
        investments = [
            ('CDB Nubank 110% CDI', Decimal('300.00'), 10),
            ('Tesouro Selic 2029', Decimal('200.00'), 12),
            ('IVVB11 (S&P 500 ETF)', Decimal('150.00'), 8),
            ('BOVA11 (Ibovespa ETF)', Decimal('100.00'), 8),
        ]
        if goal >= Decimal('700.00'):
            investments.append(('CDB Banco Inter 112% CDI', Decimal('200.00'), 15))
        if goal >= Decimal('900.00'):
            investments.append(('Fundo Multimercado XP', Decimal('300.00'), 20))

        for place, amount, day in investments:
            Investment.objects.create(
                financial_month=fm,
                place=place,
                amount=amount,
                date=_d(year, month, day),
            )

    print(f'  {len(month_configs)} meses criados com entradas, gastos, despesas fixas, faturas e investimentos.')
    return months_map


def create_installment_plans(user, months_map):
    """Cria planos de parcelamento dos 3 tipos com parcelas distribuídas nos meses."""

    sorted_months = sorted(months_map.keys())
    if len(sorted_months) < 6:
        print('  Meses insuficientes para criar parcelamentos.')
        return

    def get_fm(idx):
        if idx < len(sorted_months):
            return months_map[sorted_months[idx]]
        return None

    # ── PAGAMENTOS (kind=payment) ──────────────────────────────────────────────

    # Plano 1: MacBook Pro 14" — 12x
    plan_mac = InstallmentPlan.objects.create(
        user=user, name='MacBook Pro 14" M3', kind='payment',
    )
    mac_amount = Decimal('666.58')
    for i in range(12):
        fm = get_fm(i)
        if fm:
            Installment.objects.create(
                plan=plan_mac, financial_month=fm,
                number=i + 1, amount=mac_amount,
                status='paid' if i < 8 else 'unpaid',
                receipt_url='https://drive.google.com/file/d/1aBcD_macbook_comprovante' if i < 8 else '',
            )

    # Plano 2: iPhone 15 Pro — 6x
    plan_iphone = InstallmentPlan.objects.create(
        user=user, name='iPhone 15 Pro 256 GB', kind='payment',
    )
    iphone_amount = Decimal('583.33')
    for i in range(6):
        fm = get_fm(i + 3)
        if fm:
            Installment.objects.create(
                plan=plan_iphone, financial_month=fm,
                number=i + 1, amount=iphone_amount,
                status='paid' if i < 3 else 'unpaid',
                receipt_url='https://drive.google.com/file/d/2xYzW_iphone_comprovante' if i < 3 else '',
            )

    # Plano 3: Monitor LG 32" 4K — 10x
    plan_monitor = InstallmentPlan.objects.create(
        user=user, name='Monitor LG 32" 4K UltraFine', kind='payment',
    )
    monitor_amount = Decimal('249.90')
    for i in range(10):
        fm = get_fm(i + 1)
        if fm:
            Installment.objects.create(
                plan=plan_monitor, financial_month=fm,
                number=i + 1, amount=monitor_amount,
                status='paid' if i < 7 else 'unpaid',
                receipt_url='https://drive.google.com/file/d/3mNkP_monitor_comprovante' if i < 7 else '',
            )

    # Plano 4: Curso de Inglês EF — 12x (em andamento)
    plan_ingles = InstallmentPlan.objects.create(
        user=user, name='Curso de Inglês EF (12 meses)', kind='payment',
    )
    ingles_amount = Decimal('389.00')
    for i in range(12):
        fm = get_fm(i)
        if fm:
            Installment.objects.create(
                plan=plan_ingles, financial_month=fm,
                number=i + 1, amount=ingles_amount,
                status='paid' if i < 9 else 'unpaid',
                receipt_url='https://drive.google.com/file/d/4qRsT_ingles_comprovante' if i < 9 else '',
            )

    # Plano 5: Ar-condicionado Inverter — 8x (quitado)
    plan_ar = InstallmentPlan.objects.create(
        user=user, name='Ar-condicionado Inverter 12000 BTU', kind='payment',
    )
    ar_amount = Decimal('281.25')
    for i in range(8):
        fm = get_fm(i)
        if fm:
            Installment.objects.create(
                plan=plan_ar, financial_month=fm,
                number=i + 1, amount=ar_amount,
                status='paid',
                receipt_url=f'https://drive.google.com/file/d/5vUwX_arcond_p{i+1}',
            )

    # ── VENDAS (kind=sale) ────────────────────────────────────────────────────

    # Plano 6: Venda do MacBook Air M1 (antigo) — 6x
    plan_venda_mac = InstallmentPlan.objects.create(
        user=user, name='Venda MacBook Air M1 (usado)', kind='sale',
    )
    venda_mac_amount = Decimal('316.67')
    for i in range(6):
        fm = get_fm(i + 2)
        if fm:
            Installment.objects.create(
                plan=plan_venda_mac, financial_month=fm,
                number=i + 1, amount=venda_mac_amount,
                status='paid' if i < 4 else 'unpaid',
                receipt_url='https://drive.google.com/file/d/6yZaB_vendamac_comprovante' if i < 4 else '',
            )

    # Plano 7: Venda de Móveis (Mesa + Cadeira) — 3x
    plan_venda_moveis = InstallmentPlan.objects.create(
        user=user, name='Venda de Móveis (Mesa + Cadeira)', kind='sale',
    )
    movel_amount = Decimal('433.33')
    for i in range(3):
        fm = get_fm(i + 5)
        if fm:
            Installment.objects.create(
                plan=plan_venda_moveis, financial_month=fm,
                number=i + 1, amount=movel_amount,
                status='paid' if i < 2 else 'unpaid',
                receipt_url='https://drive.google.com/file/d/7cDeF_moveis_comprovante' if i < 2 else '',
            )

    # Plano 8: Venda de Câmera Sony a6400 — 4x
    plan_venda_camera = InstallmentPlan.objects.create(
        user=user, name='Venda Câmera Sony a6400 + Lentes', kind='sale',
    )
    camera_amount = Decimal('562.50')
    for i in range(4):
        fm = get_fm(i + 8)
        if fm:
            Installment.objects.create(
                plan=plan_venda_camera, financial_month=fm,
                number=i + 1, amount=camera_amount,
                status='paid' if i < 1 else 'unpaid',
                receipt_url='https://drive.google.com/file/d/8gHiJ_camera_comprovante' if i < 1 else '',
            )

    # ── EMPRÉSTIMOS (kind=loan) ───────────────────────────────────────────────

    # Plano 9: Empréstimo para irmão — 10x
    plan_emp_irmao = InstallmentPlan.objects.create(
        user=user, name='Empréstimo — Irmão (reforma)', kind='loan',
    )
    emp_amount = Decimal('350.00')
    for i in range(10):
        fm = get_fm(i)
        if fm:
            Installment.objects.create(
                plan=plan_emp_irmao, financial_month=fm,
                number=i + 1, amount=emp_amount,
                status='paid' if i < 7 else 'unpaid',
                receipt_url='https://drive.google.com/file/d/9kLmN_emprestimo_comprovante' if i < 7 else '',
            )

    # Plano 10: Empréstimo para amigo — 6x
    plan_emp_amigo = InstallmentPlan.objects.create(
        user=user, name='Empréstimo — Amigo (emergência)', kind='loan',
    )
    emp2_amount = Decimal('200.00')
    for i in range(6):
        fm = get_fm(i + 4)
        if fm:
            Installment.objects.create(
                plan=plan_emp_amigo, financial_month=fm,
                number=i + 1, amount=emp2_amount,
                status='paid' if i < 2 else 'unpaid',
                receipt_url='https://drive.google.com/file/d/0pQrS_emp2_comprovante' if i < 2 else '',
            )

    total_plans = 10
    total_installments = Installment.objects.filter(plan__user=user).count()
    print(f'  {total_plans} planos de parcelamento criados ({total_installments} parcelas).')


def populate():
    print('\n=== EnobFinance — Carga de Dados Mock ===\n')

    user = create_user()
    _clean(user)

    print('\nCriando cartões...')
    cards = create_cards(user)

    print('\nCriando meses financeiros...')
    months_map = create_months(user, cards)

    print('\nCriando planos de parcelamento...')
    create_installment_plans(user, months_map)

    print('\n=== Concluído ===')
    print(f'  Login: {EMAIL}')
    print(f'  Senha: {PASSWORD}')
    print(f'  Meses: {FinancialMonth.objects.filter(user=user).count()}')
    print(f'  Cartões: {len(cards)}')
    print(f'  Planos: {InstallmentPlan.objects.filter(user=user).count()}')
    print(f'  Parcelas: {Installment.objects.filter(plan__user=user).count()}')
    print(f'  Investimentos: {Investment.objects.filter(financial_month__user=user).count()}')


if __name__ == '__main__':
    populate()

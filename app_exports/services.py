import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

MONTH_NAMES = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez',
}

_CURRENCY_FMT = '#,##0.00'


def _dark_fill():
    return PatternFill(start_color='000918', end_color='000918', fill_type='solid')


def _white_bold(size=10):
    return Font(color='FFFFFF', bold=True, size=size)


def _center():
    return Alignment(horizontal='center', vertical='center')


def _left():
    return Alignment(horizontal='left', vertical='center')


def _header_row(ws, row_num, headers):
    for col, text in enumerate(headers, start=1):
        cell = ws.cell(row=row_num, column=col, value=text)
        cell.fill = _dark_fill()
        cell.font = _white_bold()
        cell.alignment = _center()


def _section_title(ws, row_num, title, n_cols):
    cell = ws.cell(row=row_num, column=1, value=title)
    cell.fill = PatternFill(start_color='0A1428', end_color='0A1428', fill_type='solid')
    cell.font = Font(color='FFFFFF', bold=True, size=10)
    cell.alignment = _left()
    if n_cols > 1:
        ws.merge_cells(
            start_row=row_num, start_column=1,
            end_row=row_num, end_column=n_cols,
        )


def _money(ws, row_num, col, value):
    cell = ws.cell(row=row_num, column=col, value=float(value or 0))
    cell.number_format = _CURRENCY_FMT
    return cell


def _col_width(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ── Annual Summary ────────────────────────────────────────────────────────────

def _build_annual_summary(wb, user):
    from decimal import Decimal
    from app_months.models import FinancialMonth

    ws = wb.create_sheet('Resumo Anual')

    headers = [
        'Ano', 'Mês',
        'Entradas', 'Gastos Var.', 'Desp. Fixas', 'Faturas', 'Parcelamentos',
        'Total Saídas', 'Investido', 'Meta', 'Saldo',
    ]
    _header_row(ws, 1, headers)
    _col_width(ws, [6, 8, 14, 14, 14, 14, 16, 14, 14, 14, 14])
    ws.freeze_panes = 'A2'

    months = (
        FinancialMonth.objects
        .filter(user=user)
        .order_by('year', 'month')
    )

    row = 2
    totals = {k: Decimal('0') for k in ('entries', 'var', 'fixed', 'invoices', 'installments', 'expenses', 'invested', 'goal')}

    for fm in months:
        entries = fm.total_entries()
        var = fm.total_variable_expenses()
        fixed = fm.total_fixed_expenses()
        invoices = fm.total_card_invoices()
        inst_pay = fm.total_installment_payments()
        expenses = fm.total_expenses()
        invested = fm.total_investments()
        goal = fm.investment_goal
        balance = fm.current_balance()

        ws.cell(row=row, column=1, value=fm.year)
        ws.cell(row=row, column=2, value=MONTH_NAMES[fm.month])
        _money(ws, row, 3, entries)
        _money(ws, row, 4, var)
        _money(ws, row, 5, fixed)
        _money(ws, row, 6, invoices)
        _money(ws, row, 7, inst_pay)
        _money(ws, row, 8, expenses)
        _money(ws, row, 9, invested)
        _money(ws, row, 10, goal)
        _money(ws, row, 11, balance)

        totals['entries'] += entries
        totals['var'] += var
        totals['fixed'] += fixed
        totals['invoices'] += invoices
        totals['installments'] += inst_pay
        totals['expenses'] += expenses
        totals['invested'] += invested
        totals['goal'] += goal
        row += 1

    # Totals row
    _section_title(ws, row, 'TOTAL', 2)
    _money(ws, row, 3, totals['entries'])
    _money(ws, row, 4, totals['var'])
    _money(ws, row, 5, totals['fixed'])
    _money(ws, row, 6, totals['invoices'])
    _money(ws, row, 7, totals['installments'])
    _money(ws, row, 8, totals['expenses'])
    _money(ws, row, 9, totals['invested'])
    _money(ws, row, 10, totals['goal'])


# ── Monthly sheets ────────────────────────────────────────────────────────────

def _build_month_sheet(wb, fm):
    sheet_name = f'{MONTH_NAMES[fm.month]}-{str(fm.year)[2:]}'
    ws = wb.create_sheet(sheet_name)
    _col_width(ws, [30, 16, 16, 16])

    row = 1

    # Entradas
    _section_title(ws, row, 'Entradas', 2)
    row += 1
    _header_row(ws, row, ['Descrição', 'Valor'])
    row += 1
    for entry in fm.entries.all():
        ws.cell(row=row, column=1, value=entry.description)
        _money(ws, row, 2, entry.amount)
        row += 1
    _money(ws, row, 2, fm.total_entries()).font = Font(bold=True)
    row += 2

    # Gastos Variáveis
    _section_title(ws, row, 'Gastos Variáveis', 2)
    row += 1
    _header_row(ws, row, ['Descrição', 'Valor'])
    row += 1
    for exp in fm.variable_expenses.all():
        ws.cell(row=row, column=1, value=exp.description)
        _money(ws, row, 2, exp.amount)
        row += 1
    _money(ws, row, 2, fm.total_variable_expenses()).font = Font(bold=True)
    row += 2

    # Despesas Fixas
    _section_title(ws, row, 'Despesas Fixas', 3)
    row += 1
    _header_row(ws, row, ['Descrição', 'Valor', 'Status'])
    row += 1
    for exp in fm.fixed_expenses.all():
        ws.cell(row=row, column=1, value=exp.description)
        _money(ws, row, 2, exp.amount)
        ws.cell(row=row, column=3, value='Pago' if exp.is_paid else 'Pendente')
        row += 1
    _money(ws, row, 2, fm.total_fixed_expenses()).font = Font(bold=True)
    row += 2

    # Faturas de Cartão
    _section_title(ws, row, 'Faturas de Cartão', 3)
    row += 1
    _header_row(ws, row, ['Cartão', 'Bandeira', 'Valor'])
    row += 1
    for inv in fm.card_invoices.select_related('card').all():
        ws.cell(row=row, column=1, value=inv.card.name)
        ws.cell(row=row, column=2, value=inv.card.brand)
        _money(ws, row, 3, inv.amount)
        row += 1
    _money(ws, row, 3, fm.total_card_invoices()).font = Font(bold=True)
    row += 2

    # Investimentos
    _section_title(ws, row, 'Investimentos', 2)
    row += 1
    _header_row(ws, row, ['Onde', 'Valor'])
    row += 1
    for inv in fm.investments.all():
        ws.cell(row=row, column=1, value=inv.place)
        _money(ws, row, 2, inv.amount)
        row += 1
    _money(ws, row, 2, fm.total_investments()).font = Font(bold=True)
    if fm.investment_goal:
        row += 1
        ws.cell(row=row, column=1, value='Meta')
        _money(ws, row, 2, fm.investment_goal)
    row += 2

    # Parcelamentos do mês
    installments = fm.installments.select_related('plan').all()
    if installments.exists():
        _section_title(ws, row, 'Parcelamentos', 4)
        row += 1
        _header_row(ws, row, ['Plano', 'Tipo', 'Parcela', 'Valor'])
        row += 1
        for inst in installments:
            ws.cell(row=row, column=1, value=inst.plan.name)
            ws.cell(row=row, column=2, value=inst.plan.get_kind_display())
            ws.cell(row=row, column=3, value=f'{inst.number}/{inst.plan.count_total()}')
            _money(ws, row, 4, inst.amount)
            row += 1


# ── Cards sheet ───────────────────────────────────────────────────────────────

def _build_cards_sheet(wb, user):
    from app_cards.models import Card

    ws = wb.create_sheet('Cartões')
    _col_width(ws, [30, 20, 14, 14])

    _header_row(ws, 1, ['Nome', 'Bandeira', 'Fechamento', 'Vencimento'])

    cards = Card.objects.filter(user=user).order_by('name')
    for row, card in enumerate(cards, start=2):
        ws.cell(row=row, column=1, value=card.name)
        ws.cell(row=row, column=2, value=card.brand)
        ws.cell(row=row, column=3, value=f'Dia {card.closing_day}')
        ws.cell(row=row, column=4, value=f'Dia {card.due_day}')


# ── Installments sheets ───────────────────────────────────────────────────────

def _build_installments_sheet(wb, user, kind, sheet_name):
    from app_installments.models import InstallmentPlan

    ws = wb.create_sheet(sheet_name)
    _col_width(ws, [30, 14, 14, 14, 10, 20, 12, 16, 18])

    plans = (
        InstallmentPlan.objects
        .filter(user=user, kind=kind)
        .prefetch_related('installments__financial_month')
        .order_by('name')
    )

    row = 1
    for plan in plans:
        _section_title(ws, row, plan.name, 4)
        row += 1

        ws.cell(row=row, column=1, value='Total')
        ws.cell(row=row, column=2, value='Pago')
        ws.cell(row=row, column=3, value='Restante')
        ws.cell(row=row, column=4, value='Parcelas')
        for col in range(1, 5):
            ws.cell(row=row, column=col).font = Font(bold=True)
        row += 1

        _money(ws, row, 1, plan.total())
        _money(ws, row, 2, plan.total_paid())
        _money(ws, row, 3, plan.total_remaining())
        ws.cell(row=row, column=4, value=f'{plan.count_paid()}/{plan.count_total()}')
        row += 2

        _header_row(ws, row, ['#', 'Mês', 'Ano', 'Valor', 'Status', 'Comprovante'])
        row += 1

        for inst in plan.installments.all():
            ws.cell(row=row, column=1, value=inst.number)
            ws.cell(row=row, column=2, value=MONTH_NAMES[inst.financial_month.month])
            ws.cell(row=row, column=3, value=inst.financial_month.year)
            _money(ws, row, 4, inst.amount)
            ws.cell(row=row, column=5, value='Pago' if inst.is_paid else 'Pendente')
            ws.cell(row=row, column=6, value=inst.receipt_url or '')
            row += 1

        row += 1


# ── Public entry point ────────────────────────────────────────────────────────

def build_export(user):
    wb = Workbook()
    wb.remove(wb.active)

    _build_annual_summary(wb, user)

    from app_months.models import FinancialMonth
    months = (
        FinancialMonth.objects
        .filter(user=user)
        .order_by('year', 'month')
    )
    for fm in months:
        _build_month_sheet(wb, fm)

    _build_cards_sheet(wb, user)
    _build_installments_sheet(wb, user, 'payment', 'Pagamentos')
    _build_installments_sheet(wb, user, 'sale', 'Vendas')

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

import io
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from app_core.constants import MONTH_NAMES_SHORT as MONTH_NAMES

_CURRENCY_FMT = '"R$" #,##0.00;[Red]"R$" -#,##0.00'
_DATE_FMT = 'DD/MM/YYYY'


def _border():
    thin = Side(border_style='thin', color='E2E8F0')
    return Border(left=thin, right=thin, top=thin, bottom=thin)


def _dark_fill():
    return PatternFill(start_color='000918', end_color='000918', fill_type='solid')


def _mid_fill():
    return PatternFill(start_color='0A1428', end_color='0A1428', fill_type='solid')


def _alt_fill():
    return PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')


def _white_bold(size=10):
    return Font(color='FFFFFF', bold=True, size=size)


def _center():
    return Alignment(horizontal='center', vertical='center')


def _left():
    return Alignment(horizontal='left', vertical='center')


def _right():
    return Alignment(horizontal='right', vertical='center')


def _header_row(ws, row_num, headers):
    for col, text in enumerate(headers, start=1):
        cell = ws.cell(row=row_num, column=col, value=text)
        cell.fill = _dark_fill()
        cell.font = _white_bold()
        cell.alignment = _center()
        cell.border = _border()


def _section_title(ws, row_num, title, n_cols):
    cell = ws.cell(row=row_num, column=1, value=title)
    cell.fill = _mid_fill()
    cell.font = Font(color='FFFFFF', bold=True, size=10)
    cell.alignment = _left()
    if n_cols > 1:
        ws.merge_cells(
            start_row=row_num, start_column=1,
            end_row=row_num, end_column=n_cols,
        )


def _money(ws, row_num, col, value, alt=False):
    cell = ws.cell(row=row_num, column=col, value=float(value or 0))
    cell.number_format = _CURRENCY_FMT
    cell.border = _border()
    cell.alignment = _right()
    if alt:
        cell.fill = _alt_fill()
    return cell


def _text(ws, row_num, col, value, alt=False):
    cell = ws.cell(row=row_num, column=col, value=value)
    cell.border = _border()
    if alt:
        cell.fill = _alt_fill()
    return cell


def _date_cell(ws, row_num, col, value, alt=False):
    cell = ws.cell(row=row_num, column=col, value=value)
    cell.number_format = _DATE_FMT
    cell.alignment = _center()
    cell.border = _border()
    if alt:
        cell.fill = _alt_fill()
    return cell


def _col_width(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _row_height(ws, row_num, height=18):
    ws.row_dimensions[row_num].height = height


# ── Annual Summary ────────────────────────────────────────────────────────────

def _build_annual_summary(wb, user):
    from app_months.models import FinancialMonth

    ws = wb.create_sheet('Resumo Anual')

    headers = [
        'Ano', 'Mês',
        'Entradas', 'Gastos Var.', 'Desp. Fixas', 'Faturas',
        'Pgtos. Parc.', 'Vendas Parc.', 'Emprést.',
        'Total Saídas', 'Investido', 'Meta', '% Meta', 'Saldo',
    ]
    _header_row(ws, 1, headers)
    _col_width(ws, [6, 8, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 10, 14])
    _row_height(ws, 1, 22)
    ws.freeze_panes = 'C2'

    months = (
        FinancialMonth.objects
        .filter(user=user)
        .order_by('year', 'month')
    )

    row = 2
    totals = {k: Decimal('0') for k in (
        'entries', 'var', 'fixed', 'invoices',
        'inst_pay', 'inst_sale', 'inst_loan',
        'expenses', 'invested', 'goal',
    )}

    for i, fm in enumerate(months):
        alt = (i % 2 == 1)
        entries = fm.total_entries()
        var = fm.total_variable_expenses()
        fixed = fm.total_fixed_expenses()
        invoices = fm.total_card_invoices()
        inst_pay = fm.total_installment_payments()
        inst_sale = fm.total_installment_sales()
        inst_loan = fm.total_installment_loans()
        expenses = fm.total_expenses()
        invested = fm.total_investments()
        goal = fm.investment_goal
        balance = fm.current_balance()
        pct = round(float(invested / goal * 100), 1) if goal > 0 else None

        _text(ws, row, 1, fm.year, alt).alignment = _center()
        _text(ws, row, 2, MONTH_NAMES[fm.month], alt).alignment = _center()
        _money(ws, row, 3, entries, alt).font = Font(color='16A34A', size=10)
        _money(ws, row, 4, var, alt)
        _money(ws, row, 5, fixed, alt)
        _money(ws, row, 6, invoices, alt).font = Font(color='A855F7', size=10)
        _money(ws, row, 7, inst_pay, alt)
        _money(ws, row, 8, inst_sale, alt).font = Font(color='16A34A', size=10)
        _money(ws, row, 9, inst_loan, alt)
        _money(ws, row, 10, expenses, alt).font = Font(color='EF4444', size=10)
        _money(ws, row, 11, invested, alt).font = Font(color='3B82F6', size=10)
        _money(ws, row, 12, goal, alt)

        pct_cell = ws.cell(row=row, column=13, value=pct)
        pct_cell.number_format = '0.0"%"'
        pct_cell.alignment = _center()
        pct_cell.border = _border()
        if alt:
            pct_cell.fill = _alt_fill()
        if pct is not None:
            pct_cell.font = Font(color='16A34A' if pct >= 100 else 'EF4444', size=10)

        bal_cell = _money(ws, row, 14, balance, alt)
        bal_cell.font = Font(
            color='16A34A' if balance >= 0 else 'EF4444',
            bold=True,
            size=10,
        )

        totals['entries'] += entries
        totals['var'] += var
        totals['fixed'] += fixed
        totals['invoices'] += invoices
        totals['inst_pay'] += inst_pay
        totals['inst_sale'] += inst_sale
        totals['inst_loan'] += inst_loan
        totals['expenses'] += expenses
        totals['invested'] += invested
        totals['goal'] += goal
        _row_height(ws, row, 18)
        row += 1

    ws.auto_filter.ref = f'A1:N{row - 1}'

    _section_title(ws, row, 'TOTAL', 2)
    _money(ws, row, 3, totals['entries']).font = Font(bold=True, color='16A34A')
    _money(ws, row, 4, totals['var']).font = Font(bold=True)
    _money(ws, row, 5, totals['fixed']).font = Font(bold=True)
    _money(ws, row, 6, totals['invoices']).font = Font(bold=True, color='A855F7')
    _money(ws, row, 7, totals['inst_pay']).font = Font(bold=True)
    _money(ws, row, 8, totals['inst_sale']).font = Font(bold=True, color='16A34A')
    _money(ws, row, 9, totals['inst_loan']).font = Font(bold=True)
    _money(ws, row, 10, totals['expenses']).font = Font(bold=True, color='EF4444')
    _money(ws, row, 11, totals['invested']).font = Font(bold=True, color='3B82F6')
    _money(ws, row, 12, totals['goal']).font = Font(bold=True)


# ── Monthly sheets ────────────────────────────────────────────────────────────

def _build_month_sheet(wb, fm):
    sheet_name = f'{MONTH_NAMES[fm.month]}-{str(fm.year)[2:]}'
    ws = wb.create_sheet(sheet_name)
    _col_width(ws, [30, 14, 14, 16])

    row = 1

    # Entradas
    _section_title(ws, row, 'Entradas', 3)
    row += 1
    _header_row(ws, row, ['Descrição', 'Data', 'Valor'])
    row += 1
    for i, entry in enumerate(fm.entries.all()):
        alt = i % 2 == 1
        _text(ws, row, 1, entry.description, alt)
        _date_cell(ws, row, 2, entry.date, alt)
        _money(ws, row, 3, entry.amount, alt).font = Font(color='16A34A', size=10)
        row += 1
    total_row = _money(ws, row, 3, fm.total_entries())
    total_row.font = Font(bold=True, color='16A34A')
    ws.cell(row=row, column=1, value='Total Entradas').font = Font(bold=True)
    row += 2

    # Gastos Variáveis
    _section_title(ws, row, 'Gastos Variáveis', 3)
    row += 1
    _header_row(ws, row, ['Descrição', 'Data', 'Valor'])
    row += 1
    for i, exp in enumerate(fm.variable_expenses.all()):
        alt = i % 2 == 1
        _text(ws, row, 1, exp.description, alt)
        _date_cell(ws, row, 2, exp.date, alt)
        _money(ws, row, 3, exp.amount, alt)
        row += 1
    total_row = _money(ws, row, 3, fm.total_variable_expenses())
    total_row.font = Font(bold=True, color='EF4444')
    ws.cell(row=row, column=1, value='Total Gastos Variáveis').font = Font(bold=True)
    row += 2

    # Despesas Fixas
    _section_title(ws, row, 'Despesas Fixas', 3)
    row += 1
    _header_row(ws, row, ['Descrição', 'Valor', 'Status'])
    row += 1
    for i, exp in enumerate(fm.fixed_expenses.all()):
        alt = i % 2 == 1
        _text(ws, row, 1, exp.description, alt)
        _money(ws, row, 2, exp.amount, alt)
        status_cell = _text(ws, row, 3, 'Pago' if exp.is_paid else 'Pendente', alt)
        status_cell.alignment = _center()
        status_cell.font = Font(
            color='16A34A' if exp.is_paid else 'EF4444', size=10
        )
        row += 1
    total_row = _money(ws, row, 2, fm.total_fixed_expenses())
    total_row.font = Font(bold=True, color='EF4444')
    ws.cell(row=row, column=1, value='Total Despesas Fixas').font = Font(bold=True)
    row += 2

    # Faturas de Cartão
    _section_title(ws, row, 'Faturas de Cartão', 4)
    row += 1
    _header_row(ws, row, ['Cartão', 'Bandeira', 'Valor', 'Status'])
    row += 1
    for i, inv in enumerate(fm.card_invoices.select_related('card').all()):
        alt = i % 2 == 1
        _text(ws, row, 1, inv.card.name, alt)
        _text(ws, row, 2, inv.card.brand, alt)
        _money(ws, row, 3, inv.amount, alt).font = Font(color='A855F7', size=10)
        status_cell = _text(ws, row, 4, 'Pago' if inv.status == 'paid' else 'Pendente', alt)
        status_cell.alignment = _center()
        status_cell.font = Font(
            color='16A34A' if inv.status == 'paid' else 'EF4444', size=10
        )
        row += 1
    total_row = _money(ws, row, 3, fm.total_card_invoices())
    total_row.font = Font(bold=True, color='A855F7')
    ws.cell(row=row, column=1, value='Total Faturas').font = Font(bold=True)
    row += 2

    # Investimentos
    _section_title(ws, row, 'Investimentos', 3)
    row += 1
    _header_row(ws, row, ['Onde', 'Data', 'Valor'])
    row += 1
    for i, inv in enumerate(fm.investments.all()):
        alt = i % 2 == 1
        _text(ws, row, 1, inv.place, alt)
        _date_cell(ws, row, 2, inv.date, alt)
        _money(ws, row, 3, inv.amount, alt).font = Font(color='3B82F6', size=10)
        row += 1
    total_row = _money(ws, row, 3, fm.total_investments())
    total_row.font = Font(bold=True, color='3B82F6')
    ws.cell(row=row, column=1, value='Total Investido').font = Font(bold=True)
    if fm.investment_goal:
        row += 1
        _text(ws, row, 1, 'Meta').font = Font(bold=True)
        _money(ws, row, 3, fm.investment_goal)
    row += 2

    # Parcelamentos do mês
    installments = fm.installments.select_related('plan').all()
    if installments.exists():
        _section_title(ws, row, 'Parcelamentos', 4)
        row += 1
        _header_row(ws, row, ['Plano', 'Tipo', 'Parcela', 'Valor'])
        row += 1
        for i, inst in enumerate(installments):
            alt = i % 2 == 1
            _text(ws, row, 1, inst.plan.name, alt)
            _text(ws, row, 2, inst.plan.get_kind_display(), alt)
            _text(ws, row, 3, f'{inst.number}/{inst.plan.count_total()}', alt).alignment = _center()
            _money(ws, row, 4, inst.amount, alt)
            row += 1

    # Resumo do mês
    row += 1
    _section_title(ws, row, 'Resumo do Mês', 2)
    row += 1
    summary = [
        ('Saldo anterior', fm.previous_balance()),
        ('Total de entradas', fm.total_entries()),
        ('Total de saídas', fm.total_expenses()),
        ('Total investido', fm.total_investments()),
        ('Saldo final', fm.current_balance()),
    ]
    for label, value in summary:
        _text(ws, row, 1, label).font = Font(bold=True)
        bal_cell = _money(ws, row, 2, value)
        if label == 'Saldo final':
            bal_cell.font = Font(
                bold=True,
                color='16A34A' if value >= 0 else 'EF4444',
            )
        elif label in ('Total de entradas',):
            bal_cell.font = Font(color='16A34A', size=10)
        elif label in ('Total de saídas',):
            bal_cell.font = Font(color='EF4444', size=10)
        elif label == 'Total investido':
            bal_cell.font = Font(color='3B82F6', size=10)
        row += 1


# ── Cards sheet ───────────────────────────────────────────────────────────────

def _build_cards_sheet(wb, user):
    from app_cards.models import Card

    ws = wb.create_sheet('Cartões')
    _col_width(ws, [30, 20, 14, 14])

    _header_row(ws, 1, ['Nome', 'Bandeira', 'Fechamento', 'Vencimento'])

    cards = list(Card.objects.filter(user=user).order_by('name'))
    for i, card in enumerate(cards):
        alt = i % 2 == 1
        row = i + 2
        _text(ws, row, 1, card.name, alt)
        _text(ws, row, 2, card.brand, alt)
        _text(ws, row, 3, f'Dia {card.closing_day}', alt).alignment = _center()
        _text(ws, row, 4, f'Dia {card.due_day}', alt).alignment = _center()

    if cards:
        ws.auto_filter.ref = f'A1:D{len(cards) + 1}'


# ── Installments sheets ───────────────────────────────────────────────────────

def _build_installments_sheet(wb, user, kind, sheet_name):
    from app_installments.models import InstallmentPlan, Installment

    ws = wb.create_sheet(sheet_name)
    _col_width(ws, [30, 14, 14, 14, 10, 12, 30])

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

        labels = ['Total', 'Pago', 'Restante', 'Parcelas']
        for col, label in enumerate(labels, start=1):
            ws.cell(row=row, column=col, value=label).font = Font(bold=True)
        row += 1

        _money(ws, row, 1, plan.total())
        paid_cell = _money(ws, row, 2, plan.total_paid())
        paid_cell.font = Font(color='16A34A', size=10)
        rem_cell = _money(ws, row, 3, plan.total_remaining())
        rem_cell.font = Font(color='EF4444', size=10)
        ws.cell(row=row, column=4, value=f'{plan.count_paid()}/{plan.count_total()}').alignment = _center()
        row += 2

        _header_row(ws, row, ['#', 'Mês', 'Ano', 'Valor', 'Status', 'Comprovante'])
        row += 1

        for i, inst in enumerate(plan.installments.all()):
            alt = i % 2 == 1
            _text(ws, row, 1, inst.number, alt).alignment = _center()
            _text(ws, row, 2, MONTH_NAMES[inst.financial_month.month], alt).alignment = _center()
            _text(ws, row, 3, inst.financial_month.year, alt).alignment = _center()
            _money(ws, row, 4, inst.amount, alt)
            status_cell = _text(ws, row, 5, 'Pago' if inst.is_paid else 'Pendente', alt)
            status_cell.alignment = _center()
            status_cell.font = Font(
                color='16A34A' if inst.is_paid else 'EF4444', size=10
            )
            _text(ws, row, 6, inst.receipt_url or '', alt)
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
    _build_installments_sheet(wb, user, 'loan', 'Empréstimos')

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

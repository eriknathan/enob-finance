from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from app_core.models import TimestampedModel


class FinancialMonth(TimestampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='financial_months',
    )
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    investment_goal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    opening_balance = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'year', 'month')
        ordering = ('-year', '-month')

    def __str__(self):
        return f'{self.month:02d}/{self.year}'

    # ── Totals ────────────────────────────────────────────────────────────────

    def total_entries(self):
        result = self.entries.aggregate(total=models.Sum('amount'))['total']
        return result or Decimal('0')

    def total_variable_expenses(self):
        result = self.variable_expenses.aggregate(total=models.Sum('amount'))['total']
        return result or Decimal('0')

    def total_fixed_expenses(self):
        result = self.fixed_expenses.aggregate(total=models.Sum('amount'))['total']
        return result or Decimal('0')

    def total_investments(self):
        result = self.investments.aggregate(total=models.Sum('amount'))['total']
        return result or Decimal('0')

    def total_card_invoices(self):
        result = self.card_invoices.aggregate(total=models.Sum('amount'))['total']
        return result or Decimal('0')

    def total_installment_payments(self):
        try:
            result = self.installments.filter(
                plan__kind='payment'
            ).aggregate(total=models.Sum('amount'))['total']
            return result or Decimal('0')
        except Exception:
            return Decimal('0')

    def total_installment_sales(self):
        try:
            result = self.installments.filter(
                plan__kind='sale'
            ).aggregate(total=models.Sum('amount'))['total']
            return result or Decimal('0')
        except Exception:
            return Decimal('0')

    def total_installment_loans(self):
        try:
            result = self.installments.filter(
                plan__kind='loan'
            ).aggregate(total=models.Sum('amount'))['total']
            return result or Decimal('0')
        except Exception:
            return Decimal('0')

    def total_entries_with_carry(self):
        return self.previous_balance() + self.total_entries()

    def total_expenses(self):
        return self.total_variable_expenses()

    # ── Balance ───────────────────────────────────────────────────────────────

    def previous_balance(self):
        if self.opening_balance is not None:
            return self.opening_balance
        prev_year = self.year if self.month > 1 else self.year - 1
        prev_month = self.month - 1 if self.month > 1 else 12
        try:
            prev = FinancialMonth.objects.get(user=self.user, year=prev_year, month=prev_month)
            return prev.current_balance()
        except FinancialMonth.DoesNotExist:
            return Decimal('0')

    def current_balance(self):
        return (
            self.previous_balance()
            + self.total_entries()
            - self.total_expenses()
            - self.total_investments()
        )


class Entry(TimestampedModel):
    financial_month = models.ForeignKey(
        FinancialMonth,
        on_delete=models.CASCADE,
        related_name='entries',
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.description} — R$ {self.amount}'


class VariableExpense(TimestampedModel):
    financial_month = models.ForeignKey(
        FinancialMonth,
        on_delete=models.CASCADE,
        related_name='variable_expenses',
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'gasto variável'
        verbose_name_plural = 'gastos variáveis'

    def __str__(self):
        return f'{self.description} — R$ {self.amount}'


class FixedExpense(TimestampedModel):
    STATUS_PAID = 'paid'
    STATUS_UNPAID = 'unpaid'
    STATUS_CHOICES = [
        (STATUS_PAID, 'Pago'),
        (STATUS_UNPAID, 'Não pago'),
    ]

    financial_month = models.ForeignKey(
        FinancialMonth,
        on_delete=models.CASCADE,
        related_name='fixed_expenses',
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_UNPAID)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'despesa fixa'
        verbose_name_plural = 'despesas fixas'

    def __str__(self):
        return f'{self.description} — R$ {self.amount}'

    @property
    def is_paid(self):
        return self.status == self.STATUS_PAID

from decimal import Decimal

from django.conf import settings
from django.db import models

from app_core.models import TimestampedModel
from app_months.models import FinancialMonth


class InstallmentPlan(TimestampedModel):
    KIND_PAYMENT = 'payment'
    KIND_SALE = 'sale'
    KIND_LOAN = 'loan'
    KIND_CHOICES = [
        (KIND_PAYMENT, 'Pagamento'),
        (KIND_SALE, 'Venda'),
        (KIND_LOAN, 'Empréstimo'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='installment_plans',
    )
    name = models.CharField(max_length=255)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_PAYMENT)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'plano de parcelamento'
        verbose_name_plural = 'planos de parcelamento'

    def __str__(self):
        return f'{self.name} ({self.get_kind_display()})'

    # ── Summary ───────────────────────────────────────────────────────────────

    def total(self):
        result = self.installments.aggregate(total=models.Sum('amount'))['total']
        return result or Decimal('0')

    def total_paid(self):
        result = self.installments.filter(status=Installment.STATUS_PAID).aggregate(
            total=models.Sum('amount')
        )['total']
        return result or Decimal('0')

    def total_remaining(self):
        return self.total() - self.total_paid()

    def count_paid(self):
        return self.installments.filter(status=Installment.STATUS_PAID).count()

    def count_total(self):
        return self.installments.count()

    @property
    def is_payment(self):
        return self.kind == self.KIND_PAYMENT

    @property
    def is_sale(self):
        return self.kind == self.KIND_SALE

    @property
    def is_loan(self):
        return self.kind == self.KIND_LOAN


class Installment(TimestampedModel):
    STATUS_PAID = 'paid'
    STATUS_UNPAID = 'unpaid'
    STATUS_CHOICES = [
        (STATUS_PAID, 'Pago'),
        (STATUS_UNPAID, 'Pendente'),
    ]

    plan = models.ForeignKey(
        InstallmentPlan,
        on_delete=models.CASCADE,
        related_name='installments',
    )
    financial_month = models.ForeignKey(
        FinancialMonth,
        on_delete=models.CASCADE,
        related_name='installments',
    )
    number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_UNPAID)
    receipt_url = models.URLField(blank=True, default='')

    class Meta:
        ordering = ('number',)
        verbose_name = 'parcela'
        verbose_name_plural = 'parcelas'

    def __str__(self):
        return f'{self.plan.name} — Parcela {self.number}'

    @property
    def is_paid(self):
        return self.status == self.STATUS_PAID

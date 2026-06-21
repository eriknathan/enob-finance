from app_core.models import TimestampedModel
from app_months.models import FinancialMonth
from django.db import models


from django.utils import timezone

class Investment(TimestampedModel):
    financial_month = models.ForeignKey(
        FinancialMonth,
        on_delete=models.CASCADE,
        related_name='investments',
    )
    place = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'investimento'
        verbose_name_plural = 'investimentos'

    def __str__(self):
        return f'{self.place} — R$ {self.amount}'

from django.conf import settings
from django.db import models

from app_core.models import TimestampedModel
from app_months.models import FinancialMonth


class Card(TimestampedModel):
    BRAND_CHOICES = [
        ('Visa', 'Visa'),
        ('Mastercard', 'Mastercard'),
        ('Elo', 'Elo'),
        ('American Express', 'American Express'),
        ('Hipercard', 'Hipercard'),
        ('Outros', 'Outros'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cards',
    )
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES, default='Visa')
    closing_day = models.PositiveSmallIntegerField()
    due_day = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ('name',)
        verbose_name = 'cartão'
        verbose_name_plural = 'cartões'

    def __str__(self):
        return f'{self.name} ({self.brand})'


class CardInvoice(TimestampedModel):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='invoices')
    financial_month = models.ForeignKey(
        FinancialMonth,
        on_delete=models.CASCADE,
        related_name='card_invoices',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('card', 'financial_month')
        ordering = ('card__name',)
        verbose_name = 'fatura'
        verbose_name_plural = 'faturas'

    def __str__(self):
        return f'{self.card.name} — {self.financial_month}'

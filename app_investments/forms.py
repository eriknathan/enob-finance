from django import forms

from app_months.models import FinancialMonth

from .models import Investment


class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ('place', 'amount')
        labels = {
            'place': 'Onde foi investido',
            'amount': 'Valor (R$)',
        }
        widgets = {
            'place': forms.TextInput(attrs={'placeholder': 'Ex: Nubank, Tesouro Selic, XP…'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0,00', 'step': '0.01', 'min': '0.01'}),
        }


class InvestmentGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialMonth
        fields = ('investment_goal',)
        labels = {'investment_goal': 'Meta de investimento (R$)'}
        widgets = {
            'investment_goal': forms.NumberInput(
                attrs={'placeholder': '0,00', 'step': '0.01', 'min': '0'}
            ),
        }

from django import forms

from .models import Entry, FixedExpense, VariableExpense, FinancialMonth


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ('description', 'amount', 'date')
        labels = {
            'description': 'Descrição',
            'amount': 'Valor (R$)',
            'date': 'Data',
        }
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Ex: Salário, Freelance…'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0,00', 'step': '0.01', 'min': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class VariableExpenseForm(forms.ModelForm):
    class Meta:
        model = VariableExpense
        fields = ('description', 'amount', 'date')
        labels = {
            'description': 'Descrição',
            'amount': 'Valor (R$)',
            'date': 'Data',
        }
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Ex: Mercado, Combustível…'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0,00', 'step': '0.01', 'min': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class FixedExpenseForm(forms.ModelForm):
    class Meta:
        model = FixedExpense
        fields = ('description', 'amount', 'status')
        labels = {
            'description': 'Descrição',
            'amount': 'Valor (R$)',
            'status': 'Status',
        }
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Ex: Aluguel, Internet…'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0,00', 'step': '0.01', 'min': '0.01'}),
        }

class FinancialMonthConfigForm(forms.ModelForm):
    start_date = forms.DateField(
        label='Data inicial',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    end_date = forms.DateField(
        label='Data final',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    opening_balance = forms.DecimalField(
        label='Saldo inicial (mês anterior)',
        required=False,
        min_value=None,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'placeholder': 'Ex: 1500,00 — deixe em branco para calcular automaticamente',
        }),
        help_text='Preencha apenas se este for o primeiro mês do histórico e você quiser definir o saldo de abertura manualmente. Nos demais meses, o saldo é calculado automaticamente a partir do mês anterior.',
    )

    class Meta:
        model = FinancialMonth
        fields = ('start_date', 'end_date', 'opening_balance')

class InvestmentGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialMonth
        fields = ('investment_goal',)
        labels = {
            'investment_goal': 'Meta de investimento (R$)'
        }
        widgets = {
            'investment_goal': forms.NumberInput(attrs={'step': '0.01'})
        }

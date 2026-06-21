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

    class Meta:
        model = FinancialMonth
        fields = ('start_date', 'end_date')

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

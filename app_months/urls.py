from django.urls import path

from . import views

urlpatterns = [
    # Month navigation
    path('', views.MonthCurrentView.as_view(), name='month-current'),
    path('<int:year>/<int:month>/', views.MonthDetailView.as_view(), name='month-detail'),
    path('<int:year>/<int:month>/config/', views.FinancialMonthConfigUpdateView.as_view(), name='month-config'),
    path('<int:year>/<int:month>/meta/', views.InvestmentGoalUpdateView.as_view(), name='investment-goal-update'),

    # Entry CRUD
    path('<int:year>/<int:month>/entrada/nova/', views.EntryCreateView.as_view(), name='entry-create'),
    path('entrada/<int:pk>/editar/', views.EntryUpdateView.as_view(), name='entry-update'),
    path('entrada/<int:pk>/excluir/', views.EntryDeleteView.as_view(), name='entry-delete'),

    # VariableExpense CRUD
    path('<int:year>/<int:month>/gasto/novo/', views.VariableExpenseCreateView.as_view(), name='variable-expense-create'),
    path('gasto/<int:pk>/editar/', views.VariableExpenseUpdateView.as_view(), name='variable-expense-update'),
    path('gasto/<int:pk>/excluir/', views.VariableExpenseDeleteView.as_view(), name='variable-expense-delete'),

    # FixedExpense CRUD
    path('<int:year>/<int:month>/despesa-fixa/nova/', views.FixedExpenseCreateView.as_view(), name='fixed-expense-create'),
    path('despesa-fixa/<int:pk>/editar/', views.FixedExpenseUpdateView.as_view(), name='fixed-expense-update'),
    path('despesa-fixa/<int:pk>/excluir/', views.FixedExpenseDeleteView.as_view(), name='fixed-expense-delete'),
    path('despesa-fixa/<int:pk>/toggle/', views.FixedExpenseToggleStatusView.as_view(), name='fixed-expense-toggle'),
]

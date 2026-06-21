from django.urls import path

from . import views

urlpatterns = [
    # Annual view — sidebar links to 'investment-annual' (no args → redirects to current year)
    path('', views.InvestmentCurrentView.as_view(), name='investment-annual'),
    path('<int:year>/', views.InvestmentAnnualView.as_view(), name='investment-annual-year'),

    # Simulator
    path('simulador/', views.InvestmentSimulatorView.as_view(), name='investment-simulator'),

    # Investment CRUD
    path('meses/<int:year>/<int:month>/novo/', views.InvestmentCreateView.as_view(), name='investment-create'),
    path('<int:pk>/editar/', views.InvestmentUpdateView.as_view(), name='investment-update'),
    path('<int:pk>/excluir/', views.InvestmentDeleteView.as_view(), name='investment-delete'),

    # Investment goal per month
    path('meses/<int:year>/<int:month>/meta/', views.InvestmentGoalUpdateView.as_view(), name='investment-goal-update'),
]

from django.urls import path

from . import views

urlpatterns = [
    path('', views.InstallmentPlanListView.as_view(), name='installment-list'),
    path('novo/', views.InstallmentPlanCreateView.as_view(), name='installment-create'),
    path('<int:pk>/', views.InstallmentPlanDetailView.as_view(), name='installment-detail'),
    path('<int:pk>/editar/', views.InstallmentPlanUpdateView.as_view(), name='installment-update'),
    path('<int:pk>/excluir/', views.InstallmentPlanDeleteView.as_view(), name='installment-delete'),
    path('parcela/<int:pk>/pagar/', views.InstallmentPayView.as_view(), name='installment-pay'),
]

from django.urls import path

from . import views

urlpatterns = [
    # Card CRUD
    path('', views.CardListView.as_view(), name='card-list'),
    path('novo/', views.CardCreateView.as_view(), name='card-create'),
    path('<int:pk>/editar/', views.CardUpdateView.as_view(), name='card-update'),
    path('<int:pk>/excluir/', views.CardDeleteView.as_view(), name='card-delete'),

    # CardInvoice CRUD
    path('meses/<int:year>/<int:month>/fatura/nova/', views.CardInvoiceCreateView.as_view(), name='invoice-create'),
    path('fatura/<int:pk>/editar/', views.CardInvoiceUpdateView.as_view(), name='invoice-update'),
    path('fatura/<int:pk>/excluir/', views.CardInvoiceDeleteView.as_view(), name='invoice-delete'),
]

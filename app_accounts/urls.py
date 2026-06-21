from django.urls import path

from .views import RegisterView, UserLoginView, UserLogoutView

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('cadastro/', RegisterView.as_view(), name='register'),
]

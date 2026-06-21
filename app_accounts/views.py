from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import EmailAuthForm, RegisterForm

User = get_user_model()


class UserLoginView(LoginView):
    form_class = EmailAuthForm
    template_name = 'app_accounts/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, 'E-mail ou senha incorretos. Verifique seus dados.')
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'app_accounts/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Conta criada com sucesso! Faça login para continuar.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Corrija os erros abaixo e tente novamente.')
        return super().form_invalid(form)

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from app_accounts.models import User
from app_months.models import FinancialMonth

from .models import Card, CardInvoice


def make_user(email='test@test.com', password='pass1234'):
    return User.objects.create_user(email=email, password=password)


def make_card(user, name='Nubank', brand='Visa'):
    return Card.objects.create(user=user, name=name, brand=brand, closing_day=10, due_day=20)


def make_month(user, year=2026, month=6):
    fm, _ = FinancialMonth.objects.get_or_create(user=user, year=year, month=month)
    return fm


# ── Model tests ───────────────────────────────────────────────────────────────

class CardModelTest(TestCase):
    def test_str(self):
        user = make_user()
        card = make_card(user)
        self.assertIn('Nubank', str(card))
        self.assertIn('Visa', str(card))


class CardInvoiceAggregationTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.fm = make_month(self.user)
        self.card1 = make_card(self.user, 'Nubank')
        self.card2 = make_card(self.user, 'Inter', 'Mastercard')

    def test_total_card_invoices_sums(self):
        CardInvoice.objects.create(card=self.card1, financial_month=self.fm, amount=Decimal('500'))
        CardInvoice.objects.create(card=self.card2, financial_month=self.fm, amount=Decimal('300'))
        self.assertEqual(self.fm.total_card_invoices(), Decimal('800'))

    def test_card_invoices_count_as_expenses(self):
        CardInvoice.objects.create(card=self.card1, financial_month=self.fm, amount=Decimal('400'))
        self.assertEqual(self.fm.total_expenses(), Decimal('400'))

    def test_total_card_invoices_zero_when_empty(self):
        self.assertEqual(self.fm.total_card_invoices(), Decimal('0'))


# ── View: user isolation ──────────────────────────────────────────────────────

class CardIsolationTest(TestCase):
    def setUp(self):
        self.user1 = make_user('u1@test.com', 'pass1234')
        self.user2 = make_user('u2@test.com', 'pass1234')
        self.card2 = make_card(self.user2, 'Card U2')

    def test_user1_cannot_edit_user2_card(self):
        self.client.login(username='u1@test.com', password='pass1234')
        response = self.client.post(
            reverse('card-update', kwargs={'pk': self.card2.pk}),
            {'name': 'Hacked', 'brand': 'Visa', 'closing_day': 1, 'due_day': 10},
        )
        self.assertEqual(response.status_code, 404)
        self.card2.refresh_from_db()
        self.assertEqual(self.card2.name, 'Card U2')

    def test_user1_cannot_delete_user2_card(self):
        self.client.login(username='u1@test.com', password='pass1234')
        response = self.client.post(reverse('card-delete', kwargs={'pk': self.card2.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Card.objects.filter(pk=self.card2.pk).exists())

    def test_card_list_shows_only_own_cards(self):
        make_card(self.user1, 'My Card')
        self.client.login(username='u1@test.com', password='pass1234')
        response = self.client.get(reverse('card-list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('My Card', content)
        self.assertNotIn('Card U2', content)


# ── View: authentication ──────────────────────────────────────────────────────

class CardAuthTest(TestCase):
    def test_card_list_requires_login(self):
        response = self.client.get(reverse('card-list'))
        self.assertEqual(response.status_code, 302)

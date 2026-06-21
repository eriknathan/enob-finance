from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from app_accounts.models import User
from app_months.models import FinancialMonth

from .models import Investment


def make_user(email='test@test.com', password='pass1234'):
    return User.objects.create_user(email=email, password=password)


def make_month(user, year=2026, month=6):
    fm, _ = FinancialMonth.objects.get_or_create(user=user, year=year, month=month)
    return fm


# ── Model tests ───────────────────────────────────────────────────────────────

class InvestmentAggregationTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.fm = make_month(self.user)

    def test_total_investments_sums(self):
        Investment.objects.create(financial_month=self.fm, place='Tesouro', amount=Decimal('1000'))
        Investment.objects.create(financial_month=self.fm, place='CDB', amount=Decimal('500'))
        self.assertEqual(self.fm.total_investments(), Decimal('1500'))

    def test_total_investments_zero_when_empty(self):
        self.assertEqual(self.fm.total_investments(), Decimal('0'))

    def test_investments_reduce_balance(self):
        from app_months.models import Entry
        Entry.objects.create(financial_month=self.fm, description='Salário', amount=Decimal('5000'))
        Investment.objects.create(financial_month=self.fm, place='Ações', amount=Decimal('1000'))
        self.assertEqual(self.fm.current_balance(), Decimal('4000'))


class InvestmentGoalTest(TestCase):
    def test_investment_goal_persists(self):
        user = make_user()
        fm = make_month(user)
        fm.investment_goal = Decimal('2000')
        fm.save()
        fm.refresh_from_db()
        self.assertEqual(fm.investment_goal, Decimal('2000'))

    def test_goal_update_view_saves(self):
        user = make_user()
        fm = make_month(user)
        self.client.login(username='test@test.com', password='pass1234')
        self.client.post(
            reverse('investment-goal-update', kwargs={'year': 2026, 'month': 6}),
            {'investment_goal': '3000'},
        )
        fm.refresh_from_db()
        self.assertEqual(fm.investment_goal, Decimal('3000'))


# ── View: user isolation ──────────────────────────────────────────────────────

class InvestmentIsolationTest(TestCase):
    def setUp(self):
        self.user1 = make_user('u1@test.com', 'pass1234')
        self.user2 = make_user('u2@test.com', 'pass1234')
        self.fm2 = make_month(self.user2)
        self.inv2 = Investment.objects.create(
            financial_month=self.fm2, place='Poupança U2', amount=Decimal('500')
        )

    def test_user1_cannot_edit_user2_investment(self):
        self.client.login(username='u1@test.com', password='pass1234')
        response = self.client.post(
            reverse('investment-update', kwargs={'pk': self.inv2.pk}),
            {'place': 'Hacked', 'amount': '1'},
        )
        self.assertEqual(response.status_code, 404)
        self.inv2.refresh_from_db()
        self.assertEqual(self.inv2.place, 'Poupança U2')

    def test_user1_cannot_delete_user2_investment(self):
        self.client.login(username='u1@test.com', password='pass1234')
        response = self.client.post(reverse('investment-delete', kwargs={'pk': self.inv2.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Investment.objects.filter(pk=self.inv2.pk).exists())

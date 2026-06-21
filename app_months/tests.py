from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from app_accounts.models import User

from .models import Entry, FinancialMonth, FixedExpense, VariableExpense


def make_user(email='test@test.com', password='pass1234'):
    return User.objects.create_user(email=email, password=password)


def make_month(user, year=2026, month=1):
    fm, _ = FinancialMonth.objects.get_or_create(user=user, year=year, month=month)
    return fm


# ── Model tests ───────────────────────────────────────────────────────────────

class FinancialMonthTotalsTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.fm = make_month(self.user, year=2026, month=6)

    def test_total_entries_zero_when_empty(self):
        self.assertEqual(self.fm.total_entries(), Decimal('0'))

    def test_total_entries_sums_correctly(self):
        Entry.objects.create(financial_month=self.fm, description='Salário', amount=Decimal('5000'))
        Entry.objects.create(financial_month=self.fm, description='Freela', amount=Decimal('1200'))
        self.assertEqual(self.fm.total_entries(), Decimal('6200'))

    def test_total_variable_expenses_zero_when_empty(self):
        self.assertEqual(self.fm.total_variable_expenses(), Decimal('0'))

    def test_total_variable_expenses_sums(self):
        VariableExpense.objects.create(financial_month=self.fm, description='Mercado', amount=Decimal('400'))
        VariableExpense.objects.create(financial_month=self.fm, description='Restaurante', amount=Decimal('150'))
        self.assertEqual(self.fm.total_variable_expenses(), Decimal('550'))

    def test_total_fixed_expenses_sums(self):
        FixedExpense.objects.create(financial_month=self.fm, description='Aluguel', amount=Decimal('1500'))
        self.assertEqual(self.fm.total_fixed_expenses(), Decimal('1500'))

    def test_total_expenses_is_variable_only(self):
        from app_cards.models import CreditCard, CardInvoice
        VariableExpense.objects.create(financial_month=self.fm, description='Mercado', amount=Decimal('300'))
        FixedExpense.objects.create(financial_month=self.fm, description='Aluguel', amount=Decimal('1000'))
        card = CreditCard.objects.create(user=self.user, name='Nubank', last_digits='1234')
        CardInvoice.objects.create(financial_month=self.fm, card=card, amount=Decimal('500'))
        # fixed expenses and card invoices are informational — only variable expenses affect the balance
        self.assertEqual(self.fm.total_expenses(), Decimal('300'))


class BalanceCarryOverTest(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_previous_balance_zero_for_first_month(self):
        fm = make_month(self.user, year=2026, month=1)
        self.assertEqual(fm.previous_balance(), Decimal('0'))

    def test_previous_balance_zero_when_no_prior_month_exists(self):
        fm = make_month(self.user, year=2026, month=6)
        # Jan–May don't exist → carry-over should be 0
        self.assertEqual(fm.previous_balance(), Decimal('0'))

    def test_carry_over_propagates_between_months(self):
        jan = make_month(self.user, year=2026, month=1)
        Entry.objects.create(financial_month=jan, description='Salário', amount=Decimal('3000'))
        VariableExpense.objects.create(financial_month=jan, description='Gastos', amount=Decimal('1000'))
        # Jan balance = 2000
        self.assertEqual(jan.current_balance(), Decimal('2000'))

        feb = make_month(self.user, year=2026, month=2)
        self.assertEqual(feb.previous_balance(), Decimal('2000'))

    def test_current_balance_accounts_for_investments(self):
        fm = make_month(self.user, year=2026, month=3)
        Entry.objects.create(financial_month=fm, description='Salário', amount=Decimal('5000'))
        from app_investments.models import Investment
        Investment.objects.create(financial_month=fm, place='Tesouro', amount=Decimal('500'))
        self.assertEqual(fm.current_balance(), Decimal('4500'))

    def test_december_to_january_carry_over(self):
        dec = make_month(self.user, year=2025, month=12)
        Entry.objects.create(financial_month=dec, description='Bônus', amount=Decimal('1000'))
        jan = make_month(self.user, year=2026, month=1)
        self.assertEqual(jan.previous_balance(), Decimal('1000'))


class OpeningBalanceTest(TestCase):
    def setUp(self):
        self.user = make_user('ob@test.com')

    def test_opening_balance_overrides_auto_carryover(self):
        jan = make_month(self.user, year=2026, month=1)
        Entry.objects.create(financial_month=jan, description='Salário', amount=Decimal('3000'))
        # Without opening_balance, balance = 0 (prev) + 3000 = 3000
        self.assertEqual(jan.previous_balance(), Decimal('0'))

        jan.opening_balance = Decimal('5000')
        jan.save()
        # With opening_balance set, previous_balance returns that value
        self.assertEqual(jan.previous_balance(), Decimal('5000'))
        self.assertEqual(jan.current_balance(), Decimal('8000'))

    def test_opening_balance_none_falls_back_to_auto(self):
        dec = make_month(self.user, year=2025, month=12)
        Entry.objects.create(financial_month=dec, description='Bônus', amount=Decimal('2000'))
        jan = make_month(self.user, year=2026, month=1)
        jan.opening_balance = None
        jan.save()
        # Should derive from December's current_balance
        self.assertEqual(jan.previous_balance(), Decimal('2000'))

    def test_opening_balance_overrides_chained_carryover(self):
        # Jan exists with a balance, but Feb has manual opening_balance → ignores Jan
        jan = make_month(self.user, year=2026, month=1)
        Entry.objects.create(financial_month=jan, description='Salário', amount=Decimal('4000'))
        feb = make_month(self.user, year=2026, month=2)
        feb.opening_balance = Decimal('1000')
        feb.save()
        self.assertEqual(feb.previous_balance(), Decimal('1000'))


class FixedExpenseStatusTest(TestCase):
    def test_is_paid_property(self):
        user = make_user()
        fm = make_month(user)
        paid = FixedExpense.objects.create(
            financial_month=fm, description='Academia', amount=Decimal('100'), status='paid'
        )
        unpaid = FixedExpense.objects.create(
            financial_month=fm, description='Internet', amount=Decimal('80'), status='unpaid'
        )
        self.assertTrue(paid.is_paid)
        self.assertFalse(unpaid.is_paid)


# ── View tests — authentication ───────────────────────────────────────────────

class MonthViewAuthTest(TestCase):
    def test_month_detail_redirects_unauthenticated(self):
        response = self.client.get(reverse('month-detail', kwargs={'year': 2026, 'month': 6}))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('month-detail', kwargs={'year': 2026, 'month': 6})}")

    def test_month_current_redirects_unauthenticated(self):
        response = self.client.get(reverse('month-current'))
        self.assertEqual(response.status_code, 302)

    def test_month_detail_accessible_when_logged_in(self):
        user = make_user()
        self.client.login(username='test@test.com', password='pass1234')
        response = self.client.get(reverse('month-detail', kwargs={'year': 2026, 'month': 6}))
        self.assertEqual(response.status_code, 200)


# ── View tests — user isolation ───────────────────────────────────────────────

class MonthUserIsolationTest(TestCase):
    def setUp(self):
        self.user1 = make_user('user1@test.com', 'pass1234')
        self.user2 = make_user('user2@test.com', 'pass1234')
        self.fm1 = make_month(self.user1, year=2026, month=6)
        self.fm2 = make_month(self.user2, year=2026, month=6)
        Entry.objects.create(financial_month=self.fm1, description='Salário U1', amount=Decimal('5000'))
        Entry.objects.create(financial_month=self.fm2, description='Salário U2', amount=Decimal('9000'))

    def test_user1_cannot_see_user2_month_data(self):
        self.client.login(username='user1@test.com', password='pass1234')
        response = self.client.get(reverse('month-detail', kwargs={'year': 2026, 'month': 6}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Salário U1', content)
        self.assertNotIn('Salário U2', content)

    def test_entry_create_belongs_to_requesting_user(self):
        self.client.login(username='user1@test.com', password='pass1234')
        self.client.post(
            reverse('entry-create', kwargs={'year': 2026, 'month': 6}),
            {'description': 'Freela', 'amount': '1000'},
        )
        self.assertEqual(Entry.objects.filter(financial_month__user=self.user1).count(), 2)
        self.assertEqual(Entry.objects.filter(financial_month__user=self.user2).count(), 1)

    def test_user1_cannot_edit_user2_entry(self):
        entry2 = Entry.objects.get(financial_month=self.fm2)
        self.client.login(username='user1@test.com', password='pass1234')
        response = self.client.post(
            reverse('entry-update', kwargs={'pk': entry2.pk}),
            {'description': 'Hacked', 'amount': '1'},
        )
        # Should 404 because get_queryset filters by user
        self.assertEqual(response.status_code, 404)
        entry2.refresh_from_db()
        self.assertEqual(entry2.description, 'Salário U2')

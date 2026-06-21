from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from app_accounts.models import User
from app_months.models import FinancialMonth

from .models import Installment, InstallmentPlan


def make_user(email='test@test.com', password='pass1234'):
    return User.objects.create_user(email=email, password=password)


def make_plan(user, name='Test Plan', kind='payment'):
    return InstallmentPlan.objects.create(user=user, name=name, kind=kind)


def make_month(user, year=2026, month=1):
    fm, _ = FinancialMonth.objects.get_or_create(user=user, year=year, month=month)
    return fm


def add_installment(plan, fm, number, amount, status='unpaid'):
    return Installment.objects.create(
        plan=plan, financial_month=fm,
        number=number, amount=amount, status=status,
    )


# ── Model: InstallmentPlan ────────────────────────────────────────────────────

class InstallmentPlanTotalsTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.plan = make_plan(self.user)
        fm1 = make_month(self.user, 2026, 1)
        fm2 = make_month(self.user, 2026, 2)
        add_installment(self.plan, fm1, 1, Decimal('500'), 'paid')
        add_installment(self.plan, fm2, 2, Decimal('500'), 'unpaid')

    def test_total(self):
        self.assertEqual(self.plan.total(), Decimal('1000'))

    def test_total_paid(self):
        self.assertEqual(self.plan.total_paid(), Decimal('500'))

    def test_total_remaining(self):
        self.assertEqual(self.plan.total_remaining(), Decimal('500'))

    def test_count_paid(self):
        self.assertEqual(self.plan.count_paid(), 1)

    def test_count_total(self):
        self.assertEqual(self.plan.count_total(), 2)

    def test_is_payment_property(self):
        self.assertTrue(self.plan.is_payment)
        self.assertFalse(self.plan.is_sale)

    def test_is_sale_property(self):
        sale_plan = make_plan(self.user, kind='sale')
        self.assertTrue(sale_plan.is_sale)
        self.assertFalse(sale_plan.is_payment)


class InstallmentPlanEmptyTest(TestCase):
    def test_totals_zero_when_no_installments(self):
        user = make_user()
        plan = make_plan(user)
        self.assertEqual(plan.total(), Decimal('0'))
        self.assertEqual(plan.total_paid(), Decimal('0'))
        self.assertEqual(plan.total_remaining(), Decimal('0'))
        self.assertEqual(plan.count_paid(), 0)
        self.assertEqual(plan.count_total(), 0)


class InstallmentIsPaidTest(TestCase):
    def test_is_paid(self):
        user = make_user()
        plan = make_plan(user)
        fm = make_month(user)
        paid = add_installment(plan, fm, 1, Decimal('100'), 'paid')
        unpaid = add_installment(plan, fm, 2, Decimal('100'), 'unpaid')
        self.assertTrue(paid.is_paid)
        self.assertFalse(unpaid.is_paid)


# ── Business rule: installment distribution ───────────────────────────────────

class InstallmentDistributionTest(TestCase):
    """Tests the distribution logic via the create view (POST)."""

    def setUp(self):
        self.user = make_user()
        self.client.login(username='test@test.com', password='pass1234')

    def test_creates_correct_number_of_installments(self):
        self.client.post(reverse('installment-create'), {
            'name': 'Geladeira', 'kind': 'payment',
            'total_amount': '1200.00', 'installment_count': '3',
            'start_month': '1', 'start_year': '2026',
        })
        plan = InstallmentPlan.objects.get(user=self.user)
        self.assertEqual(plan.count_total(), 3)

    def test_installments_span_consecutive_months(self):
        self.client.post(reverse('installment-create'), {
            'name': 'Notebook', 'kind': 'payment',
            'total_amount': '3000.00', 'installment_count': '3',
            'start_month': '11', 'start_year': '2026',
        })
        plan = InstallmentPlan.objects.get(user=self.user)
        months = list(plan.installments.values_list('financial_month__month', 'financial_month__year').order_by('number'))
        self.assertEqual(months, [(11, 2026), (12, 2026), (1, 2027)])

    def test_amounts_sum_to_total(self):
        self.client.post(reverse('installment-create'), {
            'name': 'TV', 'kind': 'payment',
            'total_amount': '1000.00', 'installment_count': '3',
            'start_month': '1', 'start_year': '2026',
        })
        plan = InstallmentPlan.objects.get(user=self.user)
        total = sum(i.amount for i in plan.installments.all())
        self.assertEqual(total, Decimal('1000.00'))

    def test_rounding_remainder_on_last_installment(self):
        # 100 / 3 = 33.33 + 33.33 + 33.34
        self.client.post(reverse('installment-create'), {
            'name': 'Curso', 'kind': 'payment',
            'total_amount': '100.00', 'installment_count': '3',
            'start_month': '1', 'start_year': '2026',
        })
        plan = InstallmentPlan.objects.get(user=self.user)
        amounts = list(plan.installments.order_by('number').values_list('amount', flat=True))
        self.assertEqual(amounts[0], Decimal('33.33'))
        self.assertEqual(amounts[1], Decimal('33.33'))
        self.assertEqual(amounts[2], Decimal('33.34'))

    def test_financial_months_auto_created(self):
        self.client.post(reverse('installment-create'), {
            'name': 'Plano Novo', 'kind': 'payment',
            'total_amount': '600.00', 'installment_count': '2',
            'start_month': '5', 'start_year': '2027',
        })
        self.assertTrue(FinancialMonth.objects.filter(user=self.user, year=2027, month=5).exists())
        self.assertTrue(FinancialMonth.objects.filter(user=self.user, year=2027, month=6).exists())


# ── View: user isolation ──────────────────────────────────────────────────────

class InstallmentIsolationTest(TestCase):
    def setUp(self):
        self.user1 = make_user('u1@test.com', 'pass1234')
        self.user2 = make_user('u2@test.com', 'pass1234')
        self.plan2 = make_plan(self.user2, name='Plan U2')
        fm = make_month(self.user2)
        add_installment(self.plan2, fm, 1, Decimal('200'))

    def test_user1_cannot_view_user2_plan(self):
        self.client.login(username='u1@test.com', password='pass1234')
        response = self.client.get(reverse('installment-detail', kwargs={'pk': self.plan2.pk}))
        self.assertEqual(response.status_code, 404)

    def test_user1_cannot_delete_user2_plan(self):
        self.client.login(username='u1@test.com', password='pass1234')
        response = self.client.post(reverse('installment-delete', kwargs={'pk': self.plan2.pk}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(InstallmentPlan.objects.filter(pk=self.plan2.pk).exists())

    def test_user1_cannot_pay_user2_installment(self):
        inst = self.plan2.installments.first()
        self.client.login(username='u1@test.com', password='pass1234')
        response = self.client.post(
            reverse('installment-pay', kwargs={'pk': inst.pk}),
            {'status': 'paid', 'receipt_url': ''},
        )
        self.assertEqual(response.status_code, 404)
        inst.refresh_from_db()
        self.assertEqual(inst.status, 'unpaid')


# ── FinancialMonth: installment aggregation ───────────────────────────────────

class FinancialMonthInstallmentAggregationTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.fm = make_month(self.user, 2026, 6)

    def test_total_installment_payments_includes_payment_kind(self):
        plan = make_plan(self.user, kind='payment')
        add_installment(plan, self.fm, 1, Decimal('300'))
        self.assertEqual(self.fm.total_installment_payments(), Decimal('300'))

    def test_total_installment_sales_includes_sale_kind(self):
        plan = make_plan(self.user, kind='sale')
        add_installment(plan, self.fm, 1, Decimal('800'))
        self.assertEqual(self.fm.total_installment_sales(), Decimal('800'))

    def test_installment_payments_count_as_expenses(self):
        plan = make_plan(self.user, kind='payment')
        add_installment(plan, self.fm, 1, Decimal('200'))
        self.assertEqual(self.fm.total_expenses(), Decimal('200'))

    def test_installment_sales_count_as_income_in_balance(self):
        plan = make_plan(self.user, kind='sale')
        add_installment(plan, self.fm, 1, Decimal('500'))
        # balance = 0 (prev) + 0 (entries) + 500 (sales) - 0 (expenses) - 0 (investments)
        self.assertEqual(self.fm.current_balance(), Decimal('500'))

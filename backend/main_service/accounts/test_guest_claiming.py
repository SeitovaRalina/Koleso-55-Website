from datetime import date, datetime, time
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import CustomTourRequest, GiftCertificateRequest, TourOrder
from excursions.models import Category, Excursion, ExcursionInquiry, Slot

from .utils import claim_guest_records_by_verified_email
from .adapters import get_verified_social_email


class VerifiedEmailGuestClaimTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Тестовые программы', slug='test-programs')
        with patch('config.celery.app.send_task'):
            self.excursion = Excursion.objects.create(
                title='Тестовая программа', slug='test-program', category=category,
                description='Описание', short_description='Кратко', price=1000, duration=60,
            )
        self.slot = Slot.objects.create(
            excursion=self.excursion, date=date(2026, 12, 1), time=time(10), max_participants=10,
        )
        self.user = get_user_model().objects.create_user(
            email='customer@example.test', password='test-password', is_email_verified=True,
        )

    def create_guest_records(self):
        TourOrder.objects.create(
            excursion=self.excursion, slot=self.slot, first_name='Ирина', last_name='Руснак',
            phone='+79000000000', email=self.user.email, num_participants=1,
        )
        ExcursionInquiry.objects.create(
            excursion=self.excursion, name='Ирина', phone='+7 (900) 000-00-00',
            email=self.user.email, contact_method='email', question='Где будет встреча?',
        )
        CustomTourRequest.objects.create(
            name='Ирина', phone='+79000000000', email=self.user.email, description='Нужна программа',
        )
        GiftCertificateRequest.objects.create(
            buyer_name='Ирина', buyer_phone='+79000000000', buyer_email=self.user.email,
            recipient_name='Получатель', amount=3000, format='digital',
        )

    def test_confirmed_email_claims_all_unowned_matching_records_once(self):
        self.create_guest_records()
        result = claim_guest_records_by_verified_email(self.user)

        self.assertEqual(result, {
            'bookings': 1, 'inquiries': 1, 'custom_tours': 1, 'certificates': 1, 'total': 4,
        })
        self.assertEqual(claim_guest_records_by_verified_email(self.user)['total'], 0)
        self.assertEqual(TourOrder.objects.get().user, self.user)
        self.assertEqual(ExcursionInquiry.objects.get().user, self.user)
        self.assertEqual(CustomTourRequest.objects.get().user, self.user)
        self.assertEqual(GiftCertificateRequest.objects.get().user, self.user)

    def test_unverified_email_and_phone_never_claim_records(self):
        self.create_guest_records()
        self.user.is_email_verified = False
        self.user.phone = '+79000000000'
        self.user.save(update_fields=['is_email_verified', 'phone'])

        result = claim_guest_records_by_verified_email(self.user)

        self.assertEqual(result['total'], 0)
        self.assertIsNone(TourOrder.objects.get().user)
        self.assertIsNone(ExcursionInquiry.objects.get().user)
        self.assertIsNone(CustomTourRequest.objects.get().user)
        self.assertIsNone(GiftCertificateRequest.objects.get().user)

    def test_login_reconciles_verified_email_records(self):
        CustomTourRequest.objects.create(
            name='Ирина', phone='+79000000000', email=self.user.email, description='Нужна программа',
        )
        client = APIClient()
        response = client.post('/api/accounts/login/', {
            'contact': self.user.email, 'contact_type': 'email', 'password': 'test-password',
        }, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['claimed_records']['custom_tours'], 1)
        self.assertEqual(CustomTourRequest.objects.get().user, self.user)

    def test_unified_request_list_is_owned_and_contains_all_request_types(self):
        self.create_guest_records()
        claim_guest_records_by_verified_email(self.user)
        client = APIClient()
        client.force_authenticate(self.user)

        response = client.get('/api/accounts/my-requests/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(
            {item['type'] for item in response.data['results']},
            {'inquiry', 'custom_tour', 'certificate'},
        )
        self.assertTrue(all(item['status'] == 'new' for item in response.data['results']))

    def test_unified_request_list_is_newest_first_and_never_leaks_another_users_record(self):
        self.create_guest_records()
        claim_guest_records_by_verified_email(self.user)
        other_user = get_user_model().objects.create_user(
            email='other@example.test', password='test-password', is_email_verified=True,
        )
        hidden = CustomTourRequest.objects.create(
            user=other_user, name='Другой', phone='+79990000000', email=other_user.email,
            description='Не показывать',
        )
        inquiry = ExcursionInquiry.objects.get(user=self.user)
        custom_tour = CustomTourRequest.objects.get(user=self.user)
        certificate = GiftCertificateRequest.objects.get(user=self.user)
        ExcursionInquiry.objects.filter(pk=inquiry.pk).update(created_at=timezone.make_aware(datetime(2026, 1, 1, 10, 0)))
        CustomTourRequest.objects.filter(pk=custom_tour.pk).update(created_at=timezone.make_aware(datetime(2026, 1, 2, 10, 0)))
        GiftCertificateRequest.objects.filter(pk=certificate.pk).update(created_at=timezone.make_aware(datetime(2026, 1, 3, 10, 0)))

        client = APIClient()
        client.force_authenticate(self.user)
        response = client.get('/api/accounts/my-requests/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item['type'] for item in response.data['results']],
            ['certificate', 'custom_tour', 'inquiry'],
        )
        self.assertNotIn(hidden.pk, [item['id'] for item in response.data['results']])


class SocialEmailIdentityTests(TestCase):
    def test_only_explicitly_verified_social_email_can_be_identity_key(self):
        sociallogin = SimpleNamespace(email_addresses=[
            SimpleNamespace(email='unverified@example.test', verified=False),
            SimpleNamespace(email='verified@example.test', verified=True),
        ])

        self.assertEqual(get_verified_social_email(sociallogin), 'verified@example.test')

    def test_unverified_social_email_is_not_returned(self):
        sociallogin = SimpleNamespace(email_addresses=[
            SimpleNamespace(email='unverified@example.test', verified=False),
        ])

        self.assertIsNone(get_verified_social_email(sociallogin))

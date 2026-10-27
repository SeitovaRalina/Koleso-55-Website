from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .admin import GiftCertificateRequestAdmin
from .models import GiftCertificateRequest


class GiftCertificateRequestAPITests(APITestCase):
    url = reverse('bookings:certificate-request-create')
    payload = {
        'buyer_name': 'Покупатель',
        'buyer_phone': '+79000000000',
        'buyer_email': 'buyer@example.com',
        'recipient_name': 'Получатель',
        'recipient_phone': '',
        'recipient_email': '',
        'amount': 3000,
        'format': 'digital',
        'message': 'Поздравляем!',
    }

    def test_guest_request_is_saved_with_new_status(self):
        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, 201)
        request = GiftCertificateRequest.objects.get(pk=response.data['id'])
        self.assertEqual(request.buyer_email, self.payload['buyer_email'])
        self.assertEqual(request.recipient_name, self.payload['recipient_name'])
        self.assertEqual(request.amount, 3000)
        self.assertEqual(request.format, 'digital')
        self.assertEqual(request.status, GiftCertificateRequest.Status.NEW)
        self.assertNotIn('status', response.data)

    def test_invalid_fields_do_not_create_request(self):
        for field, value in [('amount', 1234), ('format', 'unknown'), ('buyer_email', 'bad'), ('buyer_name', '   ')]:
            with self.subTest(field=field):
                payload = {**self.payload, field: value}
                response = self.client.post(self.url, payload, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
        self.assertEqual(GiftCertificateRequest.objects.count(), 0)

    def test_public_list_is_not_available(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_client_cannot_set_processing_status(self):
        response = self.client.post(self.url, {**self.payload, 'status': 'completed'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(GiftCertificateRequest.objects.get(pk=response.data['id']).status, 'new')

    def test_repeat_submission_creates_separate_requests(self):
        first = self.client.post(self.url, self.payload, format='json')
        second = self.client.post(self.url, self.payload, format='json')
        self.assertEqual((first.status_code, second.status_code), (201, 201))
        self.assertNotEqual(first.data['id'], second.data['id'])
        self.assertEqual(GiftCertificateRequest.objects.count(), 2)


class GiftCertificateRequestAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.request = GiftCertificateRequest.objects.create(
            buyer_name='Покупатель', buyer_phone='+79000000000',
            buyer_email='buyer@example.com', recipient_name='Получатель',
            amount=5000, format='printed',
        )
        cls.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com', password='test-password',
        )

    def test_view_permission_is_required(self):
        list_url = reverse('admin:bookings_giftcertificaterequest_changelist')
        detail_url = reverse('admin:bookings_giftcertificaterequest_change', args=[self.request.pk])
        self.assertEqual(self.client.get(list_url).status_code, 302)

        user = get_user_model().objects.create_user(
            email='viewer@example.com', password='test-password', is_staff=True,
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(list_url).status_code, 403)
        self.assertEqual(self.client.get(detail_url).status_code, 403)

        from django.contrib.auth.models import Permission
        permission = Permission.objects.get(codename='view_giftcertificaterequest')
        user.user_permissions.add(permission)
        user = get_user_model().objects.get(pk=user.pk)
        self.client.force_login(user)
        self.assertEqual(self.client.get(list_url).status_code, 200)
        self.assertEqual(self.client.get(detail_url).status_code, 200)
        self.assertEqual(self.client.post(detail_url, {'buyer_name': 'Подмена'}).status_code, 403)

    def test_admin_displays_requests_without_editing_controls(self):
        model_admin = admin.site._registry[GiftCertificateRequest]
        self.assertIsInstance(model_admin, GiftCertificateRequestAdmin)
        self.assertIn('buyer_email', model_admin.readonly_fields)
        self.assertIn('amount', model_admin.readonly_fields)
        self.assertIsNone(model_admin.actions)

        self.client.force_login(self.admin_user)
        list_url = reverse('admin:bookings_giftcertificaterequest_changelist')
        response = self.client.get(list_url)
        self.assertContains(response, 'Покупатель')
        self.assertContains(response, 'Получатель')
        self.assertContains(response, '5000')
        self.assertNotContains(response, 'Создать заявку')
        self.assertNotContains(response, 'Удалить выбранные заявки')

        detail_url = reverse('admin:bookings_giftcertificaterequest_change', args=[self.request.pk])
        response = self.client.get(detail_url)
        self.assertContains(response, 'Просмотр заявки на подарочный сертификат')
        self.assertContains(response, 'buyer@example.com')
        self.assertContains(response, 'Дата создания')
        self.assertNotContains(response, 'name="buyer_email"')
        self.assertNotContains(response, 'name="_save"')

    def test_admin_cannot_create_change_or_delete_requests(self):
        self.client.force_login(self.admin_user)
        add_url = reverse('admin:bookings_giftcertificaterequest_add')
        detail_url = reverse('admin:bookings_giftcertificaterequest_change', args=[self.request.pk])
        delete_url = reverse('admin:bookings_giftcertificaterequest_delete', args=[self.request.pk])

        self.assertEqual(self.client.get(add_url).status_code, 403)
        self.assertEqual(self.client.post(add_url, {'buyer_name': 'Новая заявка'}).status_code, 403)
        self.assertEqual(self.client.post(detail_url, {
            'buyer_name': 'Подмена', 'status': GiftCertificateRequest.Status.COMPLETED,
        }).status_code, 403)
        self.assertEqual(self.client.get(delete_url).status_code, 403)
        self.assertEqual(self.client.post(delete_url, {'post': 'yes'}).status_code, 403)

        self.request.refresh_from_db()
        self.assertEqual(self.request.buyer_name, 'Покупатель')
        self.assertEqual(self.request.status, GiftCertificateRequest.Status.NEW)
        self.assertEqual(GiftCertificateRequest.objects.count(), 1)
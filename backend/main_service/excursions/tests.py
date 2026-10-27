import uuid
from datetime import date, time
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Category, Excursion, ExcursionInquiry, Slot, TicketType
from .serializers import ExcursionListSerializer, SlotSerializer


class ExcursionInquiryTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        category = Category.objects.create(name='Город', slug='city')
        with patch('config.celery.app.send_task'):
            self.excursion = Excursion.objects.create(
                title='Программа', slug='program', category=category,
                description='Описание', short_description='Кратко', price=1000, duration=60,
            )
        self.payload = {
            'request_id': str(uuid.uuid4()), 'excursion': self.excursion.pk,
            'name': 'Иван', 'phone': '+7 (999) 123-45-67',
            'contact_method': 'telegram', 'question': 'Где встречаемся?',
        }

    def test_guest_creates_inquiry_and_admin_can_process_it(self):
        response = self.client.post('/api/excursions/inquiries/', self.payload, format='json')
        self.assertEqual(response.status_code, 201)
        inquiry = ExcursionInquiry.objects.get(pk=response.data['id'])
        self.assertEqual(inquiry.excursion, self.excursion)
        self.assertEqual(inquiry.phone, self.payload['phone'])
        self.assertEqual(inquiry.status, 'new')
        self.assertIsNotNone(inquiry.created_at)
        admin = get_user_model().objects.create_superuser('admin@example.com', 'password')
        self.client.force_login(admin)
        page = self.client.get('/admin/excursions/excursioninquiry/')
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'Программа')
        change = self.client.get(f'/admin/excursions/excursioninquiry/{inquiry.pk}/change/')
        self.assertEqual(change.status_code, 200)
        self.assertContains(change, 'Где встречаемся?')
        update = self.client.post(
            f'/admin/excursions/excursioninquiry/{inquiry.pk}/change/',
            {'status': 'in_progress', '_save': 'Save'},
        )
        self.assertEqual(update.status_code, 302)
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.status, 'in_progress')

    def test_public_cannot_read_or_set_processing_status(self):
        payload = {**self.payload, 'status': 'closed'}
        response = self.client.post('/api/excursions/inquiries/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        inquiry = ExcursionInquiry.objects.get(pk=response.data['id'])
        self.assertEqual(inquiry.status, 'new')
        self.assertEqual(self.client.get('/api/excursions/inquiries/').status_code, 401)
        self.assertEqual(self.client.get(f'/api/excursions/inquiries/{inquiry.pk}/').status_code, 404)
        self.assertEqual(self.client.get('/admin/excursions/excursioninquiry/').status_code, 302)

    def test_admin_permissions_and_invalid_status(self):
        response = self.client.post('/api/excursions/inquiries/', self.payload, format='json')
        inquiry = ExcursionInquiry.objects.get(pk=response.data['id'])
        staff = get_user_model().objects.create_user('staff@example.com', 'password', is_staff=True)
        self.client.force_login(staff)
        list_url = '/admin/excursions/excursioninquiry/'
        change_url = f'/admin/excursions/excursioninquiry/{inquiry.pk}/change/'
        self.assertEqual(self.client.get(list_url).status_code, 403)
        self.assertEqual(self.client.get(change_url).status_code, 403)
        self.assertEqual(self.client.post(change_url, {'status': 'closed', '_save': 'Save'}).status_code, 403)
        staff.user_permissions.add(Permission.objects.get(codename='view_excursioninquiry'))
        self.client.logout()
        self.client.force_login(staff)
        self.assertEqual(self.client.get(list_url).status_code, 200)
        self.assertEqual(self.client.get(change_url).status_code, 200)
        self.assertEqual(self.client.post(change_url, {'status': 'closed', '_save': 'Save'}).status_code, 403)
        staff.user_permissions.add(Permission.objects.get(codename='change_excursioninquiry'))
        self.client.logout()
        self.client.force_login(staff)
        invalid = self.client.post(change_url, {'status': 'unknown', '_save': 'Save'})
        self.assertEqual(invalid.status_code, 200)
        self.assertContains(invalid, 'Выберите корректный вариант')
        inquiry.refresh_from_db()
        self.assertEqual(inquiry.status, 'new')

    def test_duplicate_key_is_idempotent_and_conflict_is_rejected(self):
        self.assertEqual(self.client.post('/api/excursions/inquiries/', self.payload, format='json').status_code, 201)
        self.assertEqual(self.client.post('/api/excursions/inquiries/', self.payload, format='json').status_code, 201)
        self.assertEqual(ExcursionInquiry.objects.count(), 1)
        changed = {**self.payload, 'question': 'Другой вопрос'}
        self.assertEqual(self.client.post('/api/excursions/inquiries/', changed, format='json').status_code, 400)
        self.assertEqual(ExcursionInquiry.objects.count(), 1)

    def test_invalid_input_and_unknown_or_inactive_program_are_rejected(self):
        self.assertEqual(self.client.get('/api/excursions/inquiries/').status_code, 401)
        invalid = {**self.payload, 'phone': '123', 'question': 'x'}
        self.assertEqual(self.client.post('/api/excursions/inquiries/', invalid, format='json').status_code, 400)
        unknown = {**self.payload, 'excursion': 999999}
        self.assertEqual(self.client.post('/api/excursions/inquiries/', unknown, format='json').status_code, 400)
        self.excursion.is_active = False
        self.excursion.save()
        self.assertEqual(self.client.post('/api/excursions/inquiries/', self.payload, format='json').status_code, 400)
        self.assertEqual(ExcursionInquiry.objects.count(), 0)

    def test_rate_limit(self):
        for _ in range(5):
            payload = {**self.payload, 'request_id': str(uuid.uuid4())}
            self.assertEqual(self.client.post('/api/excursions/inquiries/', payload, format='json').status_code, 201)
        self.assertEqual(self.client.post('/api/excursions/inquiries/', {**self.payload, 'request_id': str(uuid.uuid4())}, format='json').status_code, 429)
        self.assertEqual(ExcursionInquiry.objects.count(), 5)

    def test_authenticated_inquiry_belongs_only_to_signed_in_account(self):
        owner = get_user_model().objects.create_user('owner@example.com', 'password')
        other = get_user_model().objects.create_user('other@example.com', 'password')
        guest = self.client.post('/api/excursions/inquiries/', self.payload, format='json')
        self.assertEqual(guest.status_code, 201)
        payload = {**self.payload, 'request_id': str(uuid.uuid4()), 'email': 'edited@example.com', 'user_id': other.pk}
        self.client.force_authenticate(user=owner)
        created = self.client.post('/api/excursions/inquiries/', payload, format='json')
        self.assertEqual(created.status_code, 201)
        inquiry = ExcursionInquiry.objects.get(pk=created.data['id'])
        self.assertEqual(inquiry.user, owner)
        self.assertEqual(inquiry.email, 'edited@example.com')
        listing = self.client.get('/api/excursions/inquiries/')
        self.assertEqual(listing.status_code, 200)
        self.assertEqual([item['id'] for item in listing.data['results']], [inquiry.pk])
        self.assertEqual(listing.data['results'][0]['excursion_title'], self.excursion.title)
        self.assertEqual(listing.data['results'][0]['public_status'], 'Новое')
        self.assertNotIn('email', listing.data['results'][0])
        self.assertNotIn('phone', listing.data['results'][0])
        inquiry.status = 'in_progress'
        inquiry.save(update_fields=['status'])
        self.assertEqual(self.client.get('/api/excursions/inquiries/').data['results'][0]['public_status'], 'В работе')
        self.client.force_authenticate(user=other)
        self.assertEqual(self.client.get('/api/excursions/inquiries/').data['count'], 0)
        self.assertEqual(self.client.get(f'/api/excursions/inquiries/{inquiry.pk}/').status_code, 404)

    def test_duplicate_request_cannot_claim_another_account_or_guest_inquiry(self):
        owner = get_user_model().objects.create_user('owner@example.com', 'password')
        other = get_user_model().objects.create_user('other@example.com', 'password')
        self.client.force_authenticate(user=owner)
        self.assertEqual(self.client.post('/api/excursions/inquiries/', self.payload, format='json').status_code, 201)
        self.client.force_authenticate(user=other)
        self.assertEqual(self.client.post('/api/excursions/inquiries/', self.payload, format='json').status_code, 400)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.post('/api/excursions/inquiries/', self.payload, format='json').status_code, 400)
        self.assertEqual(ExcursionInquiry.objects.count(), 1)

    def test_invalid_email_does_not_create_inquiry(self):
        payload = {**self.payload, 'email': 'invalid'}
        self.assertEqual(self.client.post('/api/excursions/inquiries/', payload, format='json').status_code, 400)
        self.assertEqual(ExcursionInquiry.objects.count(), 0)
class SlotContractTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Программы', slug='programs')
        with patch('config.celery.app.send_task'):
            cls.excursion = Excursion.objects.create(
                title='Программа', slug='program', category=category,
                description='Описание', short_description='Кратко',
                price=Decimal('1000.00'), duration=2040,
            )

    def make_slot(self, **overrides):
        values = dict(excursion=self.excursion, date=date(2026, 10, 14), time=time(10))
        values.update(overrides)
        return Slot(**values)

    def test_overnight_end_is_valid_and_serialized(self):
        slot = self.make_slot(end_date=date(2026, 10, 15), end_time=time(2))
        slot.full_clean()
        slot.save()
        data = SlotSerializer(slot).data
        self.assertEqual(data['end_date'], '2026-10-15')
        self.assertTrue(data['end_time'].startswith('02:00'))

    def test_missing_end_is_kept_unknown(self):
        slot = self.make_slot()
        slot.full_clean()
        self.assertIsNone(SlotSerializer(slot).data['end_date'])
        self.assertIsNone(SlotSerializer(slot).data['end_time'])

    def test_incomplete_or_earlier_end_is_rejected(self):
        for end_date, end_time in [
            (date(2026, 10, 14), None),
            (None, time(11)),
            (date(2026, 10, 14), time(10)),
            (date(2026, 10, 13), time(18)),
        ]:
            with self.subTest(end_date=end_date, end_time=end_time):
                slot = self.make_slot(end_date=end_date, end_time=end_time)
                with self.assertRaises(ValidationError):
                    slot.full_clean()
                serializer = SlotSerializer(data={
                    'date': '2026-10-14', 'time': '10:00',
                    'end_date': end_date.isoformat() if end_date else None,
                    'end_time': end_time.isoformat() if end_time else None,
                    'max_participants': 20,
                })
                self.assertFalse(serializer.is_valid())

    def test_list_exposes_tariffs_and_override_for_price_display(self):
        TicketType.objects.create(excursion=self.excursion, name='Взрослый', price=1500)
        TicketType.objects.create(excursion=self.excursion, name='Детский', price=800)
        TicketType.objects.create(excursion=self.excursion, name='Архив', price=100, is_active=False)
        slot = self.make_slot(date=date(2027, 10, 14), price_override=Decimal('700.00'))
        slot.save()
        data = ExcursionListSerializer(self.excursion).data
        self.assertEqual(len(data['ticket_types']), 3)
        self.assertEqual(data['nearest_slots'][0]['price_override'], '700.00')

    def test_list_exposes_single_active_tariff_without_override(self):
        TicketType.objects.create(excursion=self.excursion, name='Основной', price=1200)
        TicketType.objects.create(excursion=self.excursion, name='Скрытый', price=500, is_active=False)
        self.make_slot(date=date(2027, 10, 14)).save()

        data = ExcursionListSerializer(self.excursion).data
        self.assertEqual([ticket['price'] for ticket in data['ticket_types'] if ticket['is_active']], ['1200.00'])
        self.assertIsNone(data['nearest_slots'][0]['price_override'])

    def test_list_exposes_multiple_tariffs_without_override(self):
        TicketType.objects.create(excursion=self.excursion, name='Взрослый', price=1500)
        TicketType.objects.create(excursion=self.excursion, name='Детский', price=800)
        self.make_slot(date=date(2027, 10, 14)).save()

        data = ExcursionListSerializer(self.excursion).data
        self.assertEqual(sorted(float(ticket['price']) for ticket in data['ticket_types']), [800, 1500])
        self.assertIsNone(data['nearest_slots'][0]['price_override'])


class AdminSlotTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = get_user_model().objects.create_superuser(
            email='admin@example.test', password='test-only-password',
        )
        cls.staff = get_user_model().objects.create_user(
            email='staff@example.test', password='test-only-password', is_staff=True,
        )
        category = Category.objects.create(name='Программы', slug='programs')
        with patch('config.celery.app.send_task'):
            cls.excursion = Excursion.objects.create(
                title='Тестовая программа', slug='test-program', category=category,
                description='Описание', short_description='Кратко',
                price=Decimal('1000.00'), duration=2040,
                is_multi_day=True,
            )

    def setUp(self):
        self.client.force_login(self.admin)

    def slot_data(self, **overrides):
        data = {
            'excursion': self.excursion.pk, 'date': '2027-10-14', 'time': '10:00',
            'end_date': '2027-10-15', 'end_time': '15:00',
            'max_participants': 20, 'booked_participants': 0,
            'price_override': '',
        }
        data.update(overrides)
        return data

    def test_admin_labels_and_slot_fields(self):
        self.assertEqual(Excursion._meta.verbose_name_plural, 'Программы и экскурсии')
        self.assertEqual(Excursion._meta.verbose_name, 'Программа или экскурсия')
        response = self.client.get(reverse('admin:excursions_excursion_add'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Добавить программу или экскурсию')
        self.assertContains(response, 'Название программы или экскурсии')
        self.assertContains(response, 'Многодневная программа')
        self.assertContains(response, 'Дата окончания')
        self.assertContains(response, 'Время окончания')
        change_response = self.client.get(reverse('admin:excursions_excursion_change', args=[self.excursion.pk]))
        self.assertContains(change_response, 'Изменить программу или экскурсию')

    def test_create_and_edit_slots_through_admin(self):
        add_url = reverse('admin:excursions_slot_add')
        response = self.client.post(add_url, self.slot_data())
        self.assertEqual(response.status_code, 302)
        slot = Slot.objects.get(excursion=self.excursion)
        self.assertEqual(slot.end_date, date(2027, 10, 15))

        change_url = reverse('admin:excursions_slot_change', args=[slot.pk])
        response = self.client.post(change_url, self.slot_data(
            end_date='2027-10-14', end_time='15:00',
        ))
        self.assertEqual(response.status_code, 302)
        slot.refresh_from_db()
        self.assertEqual(slot.end_date, date(2027, 10, 14))
        self.assertEqual(slot.end_time, time(15))

    def test_invalid_end_and_duplicate_slot_are_rejected(self):
        add_url = reverse('admin:excursions_slot_add')
        for data in [
            self.slot_data(end_date='2027-10-14', end_time='10:00'),
            self.slot_data(end_date='', end_time='15:00'),
        ]:
            with self.subTest(data=data):
                response = self.client.post(add_url, data)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(Slot.objects.count(), 0)

        self.assertEqual(self.client.post(add_url, self.slot_data()).status_code, 302)
        response = self.client.post(add_url, self.slot_data(end_time='16:00'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Slot.objects.count(), 1)

    def test_staff_without_permissions_cannot_change_slots(self):
        slot = Slot.objects.create(
            excursion=self.excursion, date=date(2027, 10, 14), time=time(10),
        )
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('admin:excursions_slot_change', args=[slot.pk])).status_code, 403)
        self.assertEqual(self.client.post(
            reverse('admin:excursions_slot_change', args=[slot.pk]), self.slot_data(),
        ).status_code, 403)
        slot.refresh_from_db()
        self.assertIsNone(slot.end_date)

    def test_excursion_admin_status_actions(self):
        list_url = reverse('admin:excursions_excursion_changelist')
        for action, expected in [('deactivate_excursions', False), ('activate_excursions', True)]:
            with self.subTest(action=action):
                response = self.client.post(list_url, {
                    'action': action, '_selected_action': [self.excursion.pk],
                })
                self.assertEqual(response.status_code, 302)
                self.excursion.refresh_from_db()
                self.assertEqual(self.excursion.is_active, expected)
class CatalogFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        city = Category.objects.create(name="City", slug="city")
        nature = Category.objects.create(name="Nature", slug="nature")
        other = Category.objects.create(name="Other", slug="other")
        with patch("config.celery.app.send_task"):
            for title, category, location, duration, price in [
                ("Museum walk", city, "city", 90, 1000),
                ("Forest walk", nature, "suburban", 180, 2000),
                ("Russia trip", other, "russia", 300, 3000),
            ]:
                Excursion.objects.create(title=title, category=category, location_type=location,
                                         duration=duration, price=price, description=title,
                                         short_description=title)
        Slot.objects.create(excursion=Excursion.objects.get(title="Museum walk"),
                            date=date(2026, 11, 1), time=time(10))
        Slot.objects.create(excursion=Excursion.objects.get(title="Museum walk"),
                            date=date(2026, 12, 1), time=time(10))
        Slot.objects.create(excursion=Excursion.objects.get(title="Forest walk"),
                            date=date(2026, 11, 15), time=time(10))

    def titles(self, query):
        response = self.client.get(reverse("excursions:excursion-list") + query)
        self.assertEqual(response.status_code, 200)
        return {item["title"] for item in response.data["results"]}

    def test_repeated_values_are_or_within_section_and_and_across_sections(self):
        self.assertEqual(self.titles("?category=city&category=nature&location_type=city&location_type=suburban&duration=under_2h&duration=2_to_4h"),
                         {"Museum walk", "Forest walk"})
        self.assertEqual(self.titles("?category=city&category=nature&location_type=city&duration=2_to_4h"), set())

    def test_date_bounds_must_match_one_slot(self):
        self.assertEqual(self.titles("?date_from=2026-11-10&date_to=2026-11-20"), {"Forest walk"})
        self.assertEqual(self.titles("?date_from=2026-11-20"), {"Museum walk"})
        self.assertEqual(self.titles("?date_to=2026-11-10"), {"Museum walk"})
        self.assertEqual(self.titles("?date_from=2026-12-02&date_to=2026-11-01"), set())

    def test_search_price_and_legacy_single_filters(self):
        self.assertEqual(self.titles("?search=walk&min_price=1500&max_price=2500&location_type=suburban&min_duration=120"), {"Forest walk"})
        self.assertEqual(self.titles("?category=city&max_duration=120"), {"Museum walk"})

    def test_empty_and_invalid_values_do_not_expand_to_all(self):
        self.assertEqual(self.titles("?category="), set())
        self.assertEqual(self.titles("?location_type=unknown"), set())
        self.assertEqual(self.titles("?duration=unknown"), set())
        response = self.client.get(reverse("excursions:excursion-list") + "?date_from=invalid")
        self.assertEqual(response.status_code, 400)

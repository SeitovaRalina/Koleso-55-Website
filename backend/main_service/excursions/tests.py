from datetime import date, time
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Excursion, Slot, TicketType
from .serializers import ExcursionListSerializer, SlotSerializer


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

from datetime import date, time
from decimal import Decimal
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.test import TestCase

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

from datetime import date, time
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import Category, Excursion, Slot


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

from django.test import TestCase
from .models import Category


class CategoryModelTest(TestCase):

    def test_category_creation(self):
        category = Category.objects.create(
            vk_id=1,
            title="Тест",
            image="http://test.com/img.jpg"
        )
        self.assertEqual(category.title, "Тест")
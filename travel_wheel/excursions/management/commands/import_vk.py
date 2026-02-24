# excursions/management/commands/import_vk_products.py

import json
from django.core.management.base import BaseCommand
from excursions.models import Product, Category, ProductImage

def get_or_create_category(cat_json):
    """Рекурсивно создаёт категорию и всех родителей"""
    if not cat_json:
        return None
    parent = get_or_create_category(cat_json.get("parent"))
    category, _ = Category.objects.get_or_create(
        vk_id=cat_json["id"],
        defaults={
            "name": cat_json.get("name"),
            "parent": parent
        }
    )
    return category

class Command(BaseCommand):
    help = "Импорт товаров из vk_data_products.json с изображениями"

    def handle(self, *args, **options):
        file_path = "data/*.json"  # Укажите путь к JSON

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        items = data.get("response", {}).get("items", [])
        if not items:
            self.stdout.write(self.style.WARNING("Нет товаров для импорта"))
            return

        for item in items:
            # Категория
            category_json = item.get("category")
            category = get_or_create_category(category_json) if category_json else None

            # Цена и валюта
            price_data = item.get("price", {})
            price_amount = int(price_data.get("amount", 0))
            price_text = price_data.get("text", "")
            currency = price_data.get("currency", {}).get("name", "RUB")

            # Основной товар
            product, created = Product.objects.update_or_create(
                vk_id=item["id"],
                defaults={
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "category": category,
                    "owner_id": item.get("owner_id"),
                    "availability": item.get("availability"),
                    "thumb_photo": item.get("thumb_photo", ""),
                    "price_amount": price_amount,
                    "price_text": price_text,
                    "currency": currency,
                    "seo_slug": item.get("seo_slug"),
                    "market_url": item.get("market_url"),
                    "item_rating": item.get("item_rating", {}).get("rating", 0.0),
                    "reviews_count": item.get("item_rating", {}).get("reviews_count", 0),
                }
            )

            # Очистка старых изображений
            product.images.all().delete()

            # Добавляем все изображения из "thumbs" (массив массивов)
            for thumb_group in item.get("thumbs", []):
                for thumb in thumb_group:
                    ProductImage.objects.create(
                        product=product,
                        url=thumb.get("url"),
                        width=thumb.get("width"),
                        height=thumb.get("height"),
                        vk_id=thumb.get("id")
                    )

            # Дополнительно добавляем "thumb" (если есть)
            for thumb in item.get("thumb", []):
                ProductImage.objects.create(
                    product=product,
                    url=thumb.get("url"),
                    width=thumb.get("width"),
                    height=thumb.get("height")
                )

            action = "Создан" if created else "Обновлён"
            self.stdout.write(f"{action} товар: {product.title} (vk_id={product.vk_id})")

        self.stdout.write(self.style.SUCCESS("Импорт товаров завершен!"))
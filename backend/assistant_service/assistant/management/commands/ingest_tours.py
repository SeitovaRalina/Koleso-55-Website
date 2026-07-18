import os

import psycopg2
from django.core.management.base import BaseCommand
from django.db import transaction

from backend.assistant_service.assistant.models import Category, Excursion, Slot
from backend.assistant_service.assistant.services.chroma_db import VectorStore
from backend.assistant_service.assistant.services.embeddings import EmbeddingsClient


def join_lines(values):
    return "\n".join(str(value) for value in values if value)


class Command(BaseCommand):
    help = "Index active excursions from main database into assistant ChromaDB."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sync-only",
            action="store_true",
            help="Only sync assistant tables from main DB; do not call embeddings or ChromaDB.",
        )

    def get_db_connection(self):
        return psycopg2.connect(
            dbname=os.environ.get("DB_NAME", "excursions"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", "postgres"),
            host=os.environ.get("DB_HOST", "localhost"),
            port=os.environ.get("DB_PORT", "5432"),
        )

    def fetch_rows(self, cursor, query, params=None):
        cursor.execute(query, params or [])
        return cursor.fetchall()

    def build_document(self, item):
        parts = [
            f"Экскурсия: {item['title']}",
            f"Цена от: {item['price']} руб.",
            f"Категория: {item['category_name'] or 'Без категории'}",
            f"Тип: {item['location_type']}",
            f"Формат: {item['tour_format']}",
            f"Размер группы: {item['group_size']} человек.",
            f"Длительность: {item['duration']} минут.",
            f"Место встречи: {item['meeting_point'] or 'уточняется после бронирования'}.",
            f"Кратко: {item['short_description'] or ''}",
            f"Описание: {item['description'] or ''}",
            f"Входит в стоимость:\n{item['included_in_price'] or 'уточняется у менеджера'}",
            f"Не входит в стоимость:\n{item['not_included_in_price'] or 'личные расходы'}",
            f"Что взять с собой:\n{item['what_to_bring'] or 'уточняется у менеджера'}",
        ]

        if item["tickets"]:
            parts.append("Типы билетов:\n" + join_lines(f"- {name}: {price} руб." for name, price in item["tickets"]))
        if item["slots"]:
            parts.append("Даты и время:\n" + join_lines(f"- {slot_date} {slot_time}" for slot_date, slot_time in item["slots"]))
        if item["program"]:
            parts.append("Программа:\n" + join_lines(f"День {day_number}. {title}\n{description}" for day_number, title, description in item["program"]))
        if item["reviews"]:
            parts.append("Отзывы путешественников:\n" + join_lines(f"- {rating}/5: {text}" for rating, text in item["reviews"]))

        return "\n\n".join(parts)

    @transaction.atomic
    def sync_assistant_tables(self, item):
        category, _ = Category.objects.update_or_create(
            slug=item["category_slug"] or f"category-{item['category_id']}",
            defaults={
                "name": item["category_name"] or "Без категории",
                "description": item["category_description"] or "",
            },
        )
        fallback_description = item["description"] or item["short_description"] or ""
        excursion, _ = Excursion.objects.update_or_create(
            slug=item["slug"],
            defaults={
                "title": item["title"],
                "category": category,
                "location_type": item["location_type"],
                "description": fallback_description,
                "short_description": item["short_description"] or fallback_description[:500],
                "price": item["price"],
                "duration": item["duration"],
                "is_active": item["is_active"],
            },
        )
        Slot.objects.filter(excursion=excursion).delete()
        for slot_date, slot_time in item["slots"]:
            Slot.objects.create(
                excursion=excursion,
                date=slot_date,
                time=slot_time,
                max_participants=item["group_size"],
                booked_participants=0,
                price_override=None,
            )

    def handle(self, *args, **options):
        sync_only = options["sync_only"]
        vector_store = None if sync_only else VectorStore()
        embedding_service = None if sync_only else EmbeddingsClient()

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            excursions = self.fetch_rows(
                cursor,
                """
                SELECT
                    e.id,
                    e.slug,
                    e.title,
                    e.short_description,
                    e.description,
                    e.included_in_price,
                    e.not_included_in_price,
                    e.what_to_bring,
                    e.meeting_point,
                    e.price,
                    e.duration,
                    e.location_type,
                    e.tour_format,
                    e.group_size,
                    e.is_active,
                    c.id,
                    c.slug,
                    c.name,
                    c.description
                FROM excursions_excursion e
                LEFT JOIN excursions_category c ON e.category_id = c.id
                WHERE e.is_active = TRUE
                ORDER BY e.id
                """,
            )

            if not excursions:
                self.stdout.write(self.style.WARNING("Нет активных экскурсий для индексации."))
                cursor.close()
                conn.close()
                return

            items = []
            for row in excursions:
                (
                    excursion_id,
                    slug,
                    title,
                    short_description,
                    description,
                    included_in_price,
                    not_included_in_price,
                    what_to_bring,
                    meeting_point,
                    price,
                    duration,
                    location_type,
                    tour_format,
                    group_size,
                    is_active,
                    category_id,
                    category_slug,
                    category_name,
                    category_description,
                ) = row

                slots = self.fetch_rows(
                    cursor,
                    "SELECT date, time FROM excursions_slot WHERE excursion_id = %s ORDER BY date, time",
                    [excursion_id],
                )
                tickets = self.fetch_rows(
                    cursor,
                    "SELECT name, price FROM excursions_tickettype WHERE excursion_id = %s AND is_active = TRUE ORDER BY id",
                    [excursion_id],
                )
                program = self.fetch_rows(
                    cursor,
                    "SELECT day_number, title, description FROM excursions_excursionprogramday WHERE excursion_id = %s ORDER BY day_number",
                    [excursion_id],
                )
                reviews = self.fetch_rows(
                    cursor,
                    "SELECT rating, text FROM reviews_review WHERE excursion_id = %s AND status = 'approved' ORDER BY created_at DESC LIMIT 5",
                    [excursion_id],
                )

                items.append(
                    {
                        "id": excursion_id,
                        "slug": slug,
                        "title": title,
                        "short_description": short_description,
                        "description": description,
                        "included_in_price": included_in_price,
                        "not_included_in_price": not_included_in_price,
                        "what_to_bring": what_to_bring,
                        "meeting_point": meeting_point,
                        "price": price,
                        "duration": duration,
                        "location_type": location_type,
                        "tour_format": tour_format,
                        "group_size": group_size,
                        "is_active": is_active,
                        "category_id": category_id,
                        "category_slug": category_slug,
                        "category_name": category_name,
                        "category_description": category_description,
                        "slots": slots,
                        "tickets": tickets,
                        "program": program,
                        "reviews": reviews,
                    }
                )

            cursor.close()
            conn.close()
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Ошибка чтения основной БД: {exc}"))
            return

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        self.stdout.write(f"Найдено активных экскурсий: {len(items)}")
        for item in items:
            self.sync_assistant_tables(item)
            if sync_only:
                self.stdout.write(f"Синхронизировано: {item['title']}")
                continue

            document = self.build_document(item)
            embedding = embedding_service.get_embedding(document)
            ids.append(str(item["id"]))
            documents.append(document)
            embeddings.append(embedding)
            metadatas.append(
                {
                    "slug": item["slug"],
                    "title": item["title"],
                    "category": item["category_name"] or "",
                    "location_type": item["location_type"],
                    "tour_format": item["tour_format"],
                    "duration": item["duration"],
                    "price": float(item["price"]),
                }
            )
            self.stdout.write(f"Индексировано: {item['title']}")

        if sync_only:
            self.stdout.write(self.style.SUCCESS(f"Готово: {len(items)} экскурсий синхронизировано с assistant DB."))
            return

        try:
            vector_store.add_tours(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Ошибка сохранения в ChromaDB: {exc}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Готово: {len(ids)} экскурсий синхронизировано с assistant и ChromaDB."))

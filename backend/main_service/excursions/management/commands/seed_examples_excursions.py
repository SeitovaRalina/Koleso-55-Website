from datetime import date, time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import CustomUser
from bookings.models import ContactMethod, OrderStatus, TourOrder
from excursions.models import Category, Excursion, ExcursionProgramDay, Slot, TicketType
from reviews.models import Review, ReviewStatus


def lines(*items):
    return "\n".join(items)


EXCURSIONS = [
    {
        "slug": "ozero-ebeyty-2026",
        "category": ("priroda", "Природа", "Природные маршруты Омской области."),
        "title": "Жемчужина Омской степи озеро ЭБЕЙТЫ 2026 - все даты на это лето!",
        "price": Decimal("3400.00"),
        "location_type": Excursion.LocationType.SUBURBAN,
        "tour_format": Excursion.TourFormat.COMBINED,
        "group_size": 20,
        "duration": 795,
        "departure_time": time(8, 15),
        "meeting_point": "Омск, точка сбора сообщается после бронирования.",
        "short_description": "Однодневная поездка к соленому озеру Эбейты с купанием, грязями и культурной программой.",
        "description": lines(
            "Озеро Эбейты называют жемчужиной Омской степи: это место с соленой водой, лечебной грязью и просторными степными видами.",
            "Маршрут подходит тем, кто хочет за один день выбраться из города, отдохнуть на природе, узнать больше о местных традициях и вернуться вечером в Омск.",
            "В программе предусмотрены купание, свободное время у озера, обед и сопровождение гида.",
        ),
        "included_in_price": lines(
            "Транспортное обслуживание.",
            "Культурная программа.",
            "Питание в дороге.",
            "Обед.",
            "Сопровождение гида.",
        ),
        "not_included_in_price": "Личные расходы.",
        "what_to_bring": lines(
            "Головной убор, купальник, полотенце.",
            "Сланцы или обувь для берега.",
            "Питьевая вода.",
            "Наличные деньги.",
            "Солнцезащитный крем.",
            "Плотная одежда: вечером в степи бывает прохладно.",
        ),
        "slots": [(date(2026, 6, 21), time(8, 15)), (date(2026, 7, 11), time(8, 15)), (date(2026, 7, 12), time(8, 15)), (date(2026, 7, 18), time(8, 15)), (date(2026, 7, 25), time(8, 15)), (date(2026, 7, 26), time(8, 15)), (date(2026, 8, 8), time(8, 15)), (date(2026, 8, 9), time(8, 15)), (date(2026, 8, 15), time(8, 15)), (date(2026, 8, 16), time(8, 15)), (date(2026, 8, 22), time(8, 15)), (date(2026, 8, 23), time(8, 15))],
        "tickets": [("Взрослый", Decimal("3400.00")), ("Дети до 12 лет и пенсионеры", Decimal("3200.00"))],
        "program": [
            ("День у озера Эбейты", lines("08:15 - выезд из Омска.", "Дорога с рассказом гида и питанием в пути.", "Приезд к озеру, купание, лечебные грязи и свободное время.", "Обед и культурная программа.", "21:30 - ориентировочное возвращение в Омск.")),
        ],
        "reviews": [
            ("Анна", "Соколова", 5, "Очень насыщенный день: дорога прошла легко, на озере было достаточно времени и для прогулки, и для купания. Хорошо, что заранее предупредили, что взять с собой."),
            ("Марина", "Федорова", 5, "Эбейты впечатляет масштабом и тишиной. Организация четкая: питание, остановки, рассказ гида, возвращение по времени."),
        ],
    },
    {
        "slug": "ligo-yanov-den",
        "category": ("etnokultura", "Этнокультура", "Праздники, традиции и культурные поездки."),
        "title": "ЛИГО Янов день - латышский народный праздник летнего солнцестояния",
        "price": Decimal("8500.00"),
        "location_type": Excursion.LocationType.RUSSIA,
        "tour_format": Excursion.TourFormat.COMBINED,
        "group_size": 30,
        "duration": 2160,
        "departure_time": time(8, 0),
        "meeting_point": "Омск, точка сбора сообщается после бронирования.",
        "short_description": "Двухдневная поездка на латышский праздник летнего солнцестояния в Бобровку и Тарский район.",
        "description": lines(
            "Лиго, или Янов день, - народный праздник летнего солнцестояния с песнями, угощениями, кострами и традиционными обрядами.",
            "Поездка объединяет этнокультурную программу, знакомство с Бобровкой, отдых на природе и сопровождение организатора.",
        ),
        "included_in_price": lines("Транспорт.", "Проживание.", "Этнокультурная программа.", "Сопровождение гида.", "Питание по программе."),
        "not_included_in_price": lines("Питание в дороге.", "Питание на фестивале вне программы.", "Сувениры и личные расходы."),
        "what_to_bring": "Удобная одежда и обувь для природы, средства от насекомых, документы, наличные деньги.",
        "slots": [(date(2026, 6, 20), time(8, 0))],
        "tickets": [("Участник", Decimal("8500.00"))],
        "program": [
            ("Бобровка и праздник Лиго", lines("Выезд из Омска.", "Дорога в Тарский район.", "Размещение.", "Знакомство с местом, этнокультурная программа и участие в празднике Лиго.")),
            ("Традиции и возвращение", lines("Завтрак.", "Продолжение программы, прогулки и свободное время.", "Выезд обратно в Омск.", "Возвращение вечером.")),
        ],
        "reviews": [
            ("Ольга", "Иванова", 5, "Редкий формат: не просто экскурсия, а настоящее погружение в праздник. Проживание и программа были организованы спокойно и понятно."),
            ("Светлана", "Кузнецова", 4, "Понравилась атмосфера Лиго и рассказы о традициях. Поездка длинная, но впечатлений много."),
        ],
    },
    {
        "slug": "pro-process-pivovarenny-zavod",
        "category": ("gorodskie", "Городские экскурсии", "Маршруты по Омску и городские события."),
        "title": "Про процесс понятным языком, городская экскурсия",
        "price": Decimal("900.00"),
        "location_type": Excursion.LocationType.CITY,
        "tour_format": Excursion.TourFormat.BUS,
        "group_size": 20,
        "duration": 240,
        "departure_time": time(15, 0),
        "meeting_point": "Красный путь, 11.",
        "short_description": "Городская экскурсия 18+ на производство с понятным рассказом о процессе и дегустацией.",
        "description": lines(
            "Экскурсия для взрослых гостей, которым интересно увидеть производство изнутри и простым языком разобраться, как устроен процесс.",
            "Маршрут включает трансфер, посещение производства, рассказ специалиста и дегустацию.",
        ),
        "included_in_price": lines("Трансфер.", "Экскурсия по производству.", "Дегустация.", "Сопровождение организатора."),
        "not_included_in_price": "Личные расходы.",
        "what_to_bring": "Документ, подтверждающий возраст 18+.",
        "slots": [(date(2026, 6, 11), time(15, 0))],
        "tickets": [("Участник 18+", Decimal("900.00"))],
        "program": [
            ("Производство и дегустация", lines("15:00 - сбор группы.", "15:15 - отправление.", "16:00-18:00 - экскурсия по производству и дегустация.", "19:00 - возвращение.")),
        ],
        "reviews": [
            ("Дмитрий", "Орлов", 5, "Коротко, понятно и без скучной лекции. Особенно понравилось, что на производстве отвечали на вопросы."),
            ("Елена", "Миронова", 5, "Хорошая городская экскурсия на вечер: трансфер удобный, дегустация аккуратная, тайминг выдержали."),
        ],
    },
    {
        "slug": "holodnyy-farfor-teatralno-omsk",
        "category": ("tvorchestvo", "Творчество", "Мастер-классы и авторские городские встречи."),
        "title": "Мастер-класс по холодному фарфору, Т. Жарова и Театрально! Омск",
        "price": Decimal("1300.00"),
        "location_type": Excursion.LocationType.CITY,
        "tour_format": Excursion.TourFormat.WALKING,
        "group_size": 15,
        "duration": 90,
        "departure_time": time(12, 30),
        "meeting_point": "Ресторан Мишкин&Мишкин, ул. Кемеровская, 1/2.",
        "short_description": "Творческая встреча и мастер-класс по холодному фарфору в камерном городском формате.",
        "description": lines(
            "Мастер-класс подходит тем, кто хочет провести день творчески и унести с собой собственную работу.",
            "Встреча проходит в уютном городском пространстве с участием Т. Жаровой и проекта Театрально! Омск.",
        ),
        "included_in_price": lines("Мастер-класс.", "Материалы для работы.", "Сопровождение организатора."),
        "not_included_in_price": "Еда и напитки в ресторане.",
        "what_to_bring": "Хорошее настроение; специальные материалы предоставляются.",
        "slots": [(date(2026, 6, 12), time(12, 30))],
        "tickets": [("Участник", Decimal("1300.00"))],
        "program": [
            ("Творческая встреча", lines("12:30 - сбор участников.", "Знакомство с техникой холодного фарфора.", "Практическая часть мастер-класса.", "14:00 - завершение встречи.")),
        ],
        "reviews": [
            ("Наталья", "Беляева", 5, "Очень теплый мастер-класс. Материалы подготовлены заранее, объясняли спокойно, работа получилась даже у новичка."),
            ("Ирина", "Павлова", 5, "Камерная творческая встреча без спешки. Удобное место и приятная атмосфера."),
        ],
    },
    {
        "slug": "iskusstvo-otdyha-irtyshskaya-riviera",
        "category": ("relaks", "Релакс", "Поездки для отдыха и восстановления."),
        "title": "Искусство отдыха - банный комплекс Иртышская ривьера",
        "price": Decimal("5500.00"),
        "location_type": Excursion.LocationType.SUBURBAN,
        "tour_format": Excursion.TourFormat.COMBINED,
        "group_size": 7,
        "duration": 390,
        "departure_time": time(13, 0),
        "meeting_point": "Красный путь, 11.",
        "short_description": "Женский VIP-день отдыха в комплексе Иртышская ривьера с трансфером и сопровождением.",
        "description": lines(
            "Формат для небольшой женской группы: спокойный день в банном комплексе Sultan на территории Иртышской ривьеры.",
            "В программе трансфер, сопровождение, отдых в комплексе и возможность добавить индивидуальные услуги на месте.",
        ),
        "included_in_price": lines("Трансфер.", "Посещение комплекса Sultan.", "Сопровождение организатора."),
        "not_included_in_price": lines("Питание.", "Дополнительные услуги комплекса.", "Личные расходы."),
        "what_to_bring": "Купальник, полотенце, сланцы, средства ухода, наличные деньги для дополнительных услуг.",
        "slots": [(date(2026, 6, 21), time(13, 0))],
        "tickets": [("Участница", Decimal("5500.00"))],
        "program": [
            ("День отдыха", lines("13:00 - сбор группы на Красном пути, 11.", "Трансфер в комплекс.", "Отдых в банном комплексе Sultan.", "Свободное время и дополнительные услуги по желанию.", "19:30 - ориентировочное завершение.")),
        ],
        "reviews": [
            ("Виктория", "Романова", 5, "Маленькая группа - это большой плюс. Все было спокойно, без суеты, трансфер удобный."),
            ("Алина", "Громова", 5, "Хороший формат перезагрузки на один день. Понравилось, что сразу понятно, что входит, а что оплачивается отдельно."),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed excursions from examples/excursions.txt into the current database."

    @transaction.atomic
    def handle(self, *args, **options):
        excursion_count = 0
        review_count = 0

        for item in EXCURSIONS:
            category_slug, category_name, category_description = item["category"]
            category, _ = Category.objects.update_or_create(
                slug=category_slug,
                defaults={"name": category_name, "description": category_description},
            )
            excursion, _ = Excursion.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "category": category,
                    "title": item["title"],
                    "location_type": item["location_type"],
                    "tour_format": item["tour_format"],
                    "group_size": item["group_size"],
                    "is_multi_day": len(item["program"]) > 1,
                    "description": item["description"],
                    "short_description": item["short_description"],
                    "included_in_price": item["included_in_price"],
                    "not_included_in_price": item["not_included_in_price"],
                    "what_to_bring": item["what_to_bring"],
                    "meeting_point": item["meeting_point"],
                    "departure_time": item["departure_time"],
                    "price": item["price"],
                    "duration": item["duration"],
                    "is_active": True,
                },
            )
            excursion_count += 1

            first_slot = None
            for slot_date, slot_time in item["slots"]:
                slot, _ = Slot.objects.update_or_create(
                    excursion=excursion,
                    date=slot_date,
                    time=slot_time,
                    defaults={
                        "max_participants": item["group_size"],
                        "booked_participants": 0,
                        "price_override": None,
                    },
                )
                first_slot = first_slot or slot

            for name, price in item["tickets"]:
                TicketType.objects.update_or_create(
                    excursion=excursion,
                    name=name,
                    defaults={"price": price, "is_active": True},
                )

            for index, (title, description) in enumerate(item["program"], start=1):
                ExcursionProgramDay.objects.update_or_create(
                    excursion=excursion,
                    day_number=index,
                    defaults={"title": title, "description": description},
                )

            for review_index, (first_name, last_name, rating, text) in enumerate(item["reviews"], start=1):
                email = f"review.{item['slug']}.{review_index}@example.com"
                user, _ = CustomUser.objects.update_or_create(
                    email=email,
                    defaults={
                        "first_name": first_name,
                        "last_name": last_name,
                        "is_email_verified": True,
                    },
                )
                if not user.has_usable_password():
                    user.set_unusable_password()
                    user.save(update_fields=["password"])

                order = TourOrder.objects.filter(user=user, excursion=excursion, slot=first_slot).first()
                if order is None:
                    order = TourOrder.objects.create(
                        user=user,
                        excursion=excursion,
                        slot=first_slot,
                        first_name=first_name,
                        last_name=last_name,
                        phone=f"+7900555{excursion_count:02d}{review_index:02d}",
                        contact_method=ContactMethod.TELEGRAM,
                        email=email,
                        num_participants=1,
                        status=OrderStatus.COMPLETED,
                        comment="Seed order: участник посетил экскурсию.",
                    )

                Review.objects.update_or_create(
                    user=user,
                    excursion=excursion,
                    defaults={
                        "order": order,
                        "rating": rating,
                        "text": text,
                        "status": ReviewStatus.APPROVED,
                        "is_toxic": False,
                        "toxicity_score": 0.0,
                        "show_on_homepage": review_index == 1,
                        "homepage_author_name": f"{first_name} {last_name}",
                        "homepage_order": excursion_count,
                    },
                )
                review_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {excursion_count} excursions and {review_count} reviews."))

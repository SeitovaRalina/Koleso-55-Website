from datetime import date, timedelta, time
from decimal import Decimal

from django.core.management.base import BaseCommand

from accounts.models import CustomUser
from excursions.models import Category, Excursion, Slot
from reviews.models import Review, ReviewStatus


class Command(BaseCommand):
    help = 'Seed demo excursions, slots, and homepage reviews for local development.'

    def handle(self, *args, **options):
        categories = {
            'overview': Category.objects.update_or_create(
                slug='overview',
                defaults={
                    'name': 'Обзорные экскурсии',
                    'description': 'Городские и выездные маршруты для первого знакомства.',
                },
            )[0],
            'active': Category.objects.update_or_create(
                slug='active',
                defaults={
                    'name': 'Активный отдых',
                    'description': 'Маршруты с прогулками, природой и движением.',
                },
            )[0],
            'tasting': Category.objects.update_or_create(
                slug='tasting',
                defaults={
                    'name': 'Дегустации',
                    'description': 'Гастрономические маршруты и локальные производства.',
                },
            )[0],
        }

        excursions = [
            {
                'title': 'Омск купеческий: прогулка по историческому центру',
                'slug': 'omsk-kupecheskiy',
                'category': categories['overview'],
                'location_type': Excursion.LocationType.CITY,
                'price': Decimal('1200.00'),
                'duration': 150,
                'short_description': 'Главные улицы, особняки и истории старого Омска за одну прогулку.',
                'description': 'Маршрут по центру Омска с архитектурой, городскими легендами и спокойным темпом.',
            },
            {
                'title': 'Загородная экскурсия с дегустацией на производство',
                'slug': 'zagorodnaya-degustatsiya',
                'category': categories['tasting'],
                'location_type': Excursion.LocationType.SUBURBAN,
                'price': Decimal('1900.00'),
                'duration': 240,
                'short_description': 'Выезд за город, знакомство с производством и дегустация.',
                'description': 'Насыщенный загородный маршрут для небольшой группы с дегустацией и сопровождением гида.',
            },
            {
                'title': 'Тара историческая: поездка на день',
                'slug': 'tara-istoricheskaya',
                'category': categories['overview'],
                'location_type': Excursion.LocationType.SUBURBAN,
                'price': Decimal('3200.00'),
                'duration': 480,
                'short_description': 'Однодневная поездка в старинный город Омской области.',
                'description': 'История, архитектура и спокойный день вне города с организованным маршрутом.',
            },
            {
                'title': 'Тур по России: выходные в Тюмени',
                'slug': 'tyumen-weekend',
                'category': categories['active'],
                'location_type': Excursion.LocationType.RUSSIA,
                'price': Decimal('8900.00'),
                'duration': 1320,
                'short_description': 'Короткий тур по России с продуманной программой на выходные.',
                'description': 'Городской отдых, прогулки, термальные источники и сопровождение группы.',
            },
        ]

        created_excursions = []
        for item in excursions:
            slug = item['slug']
            defaults = {key: value for key, value in item.items() if key != 'slug'}
            excursion, _ = Excursion.objects.update_or_create(
                slug=slug,
                defaults={**defaults, 'is_active': True},
            )
            created_excursions.append(excursion)

        start = date.today()
        slot_times = [time(10, 0), time(14, 0), time(18, 0)]
        for index, excursion in enumerate(created_excursions):
            for offset in range(1, 8, 2):
                Slot.objects.update_or_create(
                    excursion=excursion,
                    date=start + timedelta(days=offset + index % 2),
                    time=slot_times[index % len(slot_times)],
                    defaults={
                        'max_participants': 18,
                        'booked_participants': index,
                        'price_override': None,
                    },
                )

        users = [
            ('demo.natalia@example.com', 'Наталья', 'Климон'),
            ('demo.irina@example.com', 'Ирина', 'Петрова'),
            ('demo.alexey@example.com', 'Алексей', 'Морозов'),
        ]
        created_users = []
        for email, first_name, last_name in users:
            user, _ = CustomUser.objects.update_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_email_verified': True,
                },
            )
            if not user.has_usable_password():
                user.set_password('demo-password-123')
                user.save(update_fields=['password'])
            created_users.append(user)

        reviews = [
            (
                created_users[0],
                created_excursions[1],
                5,
                'От всей души благодарим за организацию поездки. Маршрут был понятный, гид держал темп и отвечал на вопросы всей группы.',
                1,
            ),
            (
                created_users[1],
                created_excursions[0],
                5,
                'Омск открылся совсем иначе: живые истории, красивые места и спокойная организация без суеты.',
                2,
            ),
            (
                created_users[2],
                created_excursions[2],
                5,
                'Поездка в Тару получилась насыщенной, но не утомительной. Хороший баланс дороги, прогулок и рассказа гида.',
                3,
            ),
        ]

        for user, excursion, rating, text, order in reviews:
            Review.objects.update_or_create(
                user=user,
                excursion=excursion,
                defaults={
                    'rating': rating,
                    'text': text,
                    'status': ReviewStatus.APPROVED,
                    'show_on_homepage': True,
                    'homepage_author_name': user.get_full_name(),
                    'homepage_order': order,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {len(created_excursions)} excursions, demo slots, and {len(reviews)} homepage reviews.'
        ))

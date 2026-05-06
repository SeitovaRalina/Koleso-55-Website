import os
from django.core.management.base import BaseCommand
from assistant.services.chroma_db import VectorStore
from assistant.services.embeddings import EmbeddingsClient

class Command(BaseCommand):
    help = 'Тестовый поиск по векторной базе туров'

    def handle(self, *args, **options):
        #иниц хранилище и клиент Yandex Cloud
        vector_store = VectorStore()
        embedding_service = EmbeddingsClient()

        self.stdout.write(self.style.SUCCESS('--- ТЕСТОВЫЙ ПОИСК ЗАПУЩЕН (Yandex Embeddings) ---'))
        self.stdout.write('Введите запрос для поиска или "exit" для выхода.')
        
        while True:
            try:
                query_text = input("\nЧто ищем?: ").strip()
            except EOFError:
                break
                
            if query_text.lower() in ['exit', 'quit', 'выход']:
                break

            if not query_text:
                continue

            self.stdout.write(f"Отправка запроса в Yandex Cloud: {query_text}...")

            try:
                query_vector = embedding_service.get_embedding(query_text)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка API Yandex: {e}"))
                continue

            #ближайшие векторы 
            results = vector_store.search(query_vector, top_k=2)

            if not results:
                self.stdout.write(self.style.WARNING("В базе пока ничего не найдено."))
            else:
                self.stdout.write(self.style.SUCCESS(f"Найдено совпадений: {len(results)}"))
                for i, doc in enumerate(results, 1):
                    self.stdout.write(self.style.MIGRATE_HEADING(f"\n[Результат {i}]:"))
                    self.stdout.write(f"{doc[:400]}...") 
                    self.stdout.write("-" * 40)
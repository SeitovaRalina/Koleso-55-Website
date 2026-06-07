import os
import psycopg2
from django.core.management.base import BaseCommand
from assistant.services.chroma_db import VectorStore
from assistant.services.embeddings import EmbeddingsClient


class Command(BaseCommand):
    help = 'Индексация реальных экскурсий из базы данных в векторную базу ChromaDB'

    def get_db_connection(self):
        """Получаем подключение к базе данных"""
        return psycopg2.connect(
            dbname=os.environ.get('DB_NAME', 'excursions'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', 'postgres'),
            host=os.environ.get('DB_HOST', 'localhost'),
            port=os.environ.get('DB_PORT', '5432')
        )

    def handle(self, *args, **options):
        vector_store = VectorStore()
        embedding_service = EmbeddingsClient()

        # Получаем реальные экскурсии из базы данных
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()

            # SQL запрос для получения экскурсий с категориями
            query = """
                SELECT 
                    e.id,
                    e.title,
                    COALESCE(e.description, e.short_description) as description,
                    e.price,
                    e.duration,
                    e.location_type,
                    c.name as category_name
                FROM excursions_excursion e
                LEFT JOIN excursions_category c ON e.category_id = c.id
                WHERE e.is_active = TRUE
                ORDER BY e.id
            """
            
            cursor.execute(query)
            excursions = cursor.fetchall()
            total_count = len(excursions)
            
            if total_count == 0:
                self.stdout.write(self.style.WARNING('В базе данных нет активных экскурсий для индексации'))
                cursor.close()
                conn.close()
                return
            
            self.stdout.write(f'Найдено {total_count} активных экскурсий в базе данных')
            
            tours = []
            location_type_map = {
                'city': 'Городские экскурсии',
                'suburban': 'Загородные экскурсии', 
                'russia': 'Туры по России'
            }
            
            for excursion in excursions:
                (excursion_id, title, description, price, duration, location_type, category_name) = excursion
                tours.append({
                    "id": str(excursion_id),
                    "title": title,
                    "description": description or "",
                    "price": float(price),
                    "metadata": {
                        "category": category_name or "Без категории",
                        "location_type": location_type_map.get(location_type, location_type),
                        "duration": duration
                    }
                })
            
            cursor.close()
            conn.close()
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при получении данных из базы данных: {str(e)}'))
            return
        
        self.stdout.write('--- СТАРТ ИНДЕКСАЦИИ ---')
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for tour in tours:
            self.stdout.write(f"Обработка: {tour['title']}")
            
            text_chunk = f"Тур: {tour['title']}. Цена от: {tour['price']} руб. Описание: {tour['description']}"
            
            # Получаем вектор от Яндекса
            embedding = embedding_service.get_embedding(text_chunk)
            
            ids.append(tour['id'])
            documents.append(text_chunk)
            embeddings.append(embedding)
            metadatas.append(tour['metadata'])

        self.stdout.write('--- СОХРАНЕНИЕ В CHROMADB ---')
        
        try:
            vector_store.add_tours(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            self.stdout.write(self.style.SUCCESS(f'Успешно проиндексировано {len(ids)} экскурсий'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при сохранении в ChromaDB: {str(e)}'))
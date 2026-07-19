import os
import logging
import psycopg2
import chromadb
import requests
import shutil
from celery import shared_task

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VectorStore:
    """Класс для работы с ChromaDB, аналогично assistant сервису"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.persist_directory = "/app/chroma_data"
        self.collection_name = "tours_collection"
        
        # Проверяем работоспособность существующей базы
        self._init_chroma_db()
        self._initialized = True
    
    def _init_chroma_db(self):
        """Инициализация ChromaDB с обработкой ошибок схемы"""
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            
            # Проверяем работоспособность коллекции
            self.collection.count()
            logger.info("ChromaDB коллекция работоспособна")
        except Exception as e:
            logger.warning(f"Проблема с ChromaDB: {e}. Пересоздаем базу данных.")
            
            # Удаляем повреждённую базу данных
            try:
                if os.path.exists(self.persist_directory):
                    logger.warning(f"Удаляем существующую директорию ChromaDB: {self.persist_directory}")
                    shutil.rmtree(self.persist_directory)
                os.makedirs(self.persist_directory, exist_ok=True)
            except Exception as delete_error:
                logger.error(f"Ошибка при удалении директории ChromaDB: {delete_error}")
            
            # Создаём новую базу данных
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            logger.info("ChromaDB база данных пересоздана успешно")

    def add_tour(self, tour_id, embedding, document, metadata):
        """Метод для добавления одного тура в базу"""
        # Проверяем, существует ли уже документ с таким ID
        try:
            existing_doc = self.collection.get(ids=[tour_id])
            if existing_doc and existing_doc.get('ids'):
                logger.info(f"Документ с ID {tour_id} существует, обновляем")
                self.collection.delete(ids=[tour_id])
        except Exception as e:
            logger.warning(f"Ошибка при проверке существования документа: {e}")

        # Добавляем в ChromaDB
        self.collection.add(
            ids=[tour_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata]
        )


def get_db_connection():
    """Получаем подключение к базе данных"""
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'excursions'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', '5432')
    )


def get_excursion_by_id(excursion_id):
    """Получает данные экскурсии по ID"""
    try:
        logger.info(f"Подключение к базе данных для экскурсии {excursion_id}")
        logger.info(f"DB_HOST: {os.environ.get('DB_HOST')}, DB_NAME: {os.environ.get('DB_NAME')}")
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Сначала проверим, есть ли вообще экскурсии в базе
        check_query = "SELECT id, title, is_active FROM excursions_excursion ORDER BY id DESC LIMIT 5"
        cursor.execute(check_query)
        all_excursions = cursor.fetchall()
        logger.info(f"Последние 5 экскурсий в базе: {all_excursions}")
        
        # Теперь ищем конкретную экскурсию
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
            WHERE e.id = %s AND e.is_active = TRUE
        """
        
        logger.info(f"Выполняем SQL запрос для excursion_id={excursion_id}")
        cursor.execute(query, (excursion_id,))
        excursion = cursor.fetchone()
        
        logger.info(f"Результат запроса для excursion_id={excursion_id}: {excursion}")
        
        cursor.close()
        conn.close()
        
        return excursion
    except Exception as e:
        logger.error(f"Ошибка при получении экскурсии {excursion_id}: {str(e)}")
        raise


def get_embedding(text):
    """Получает эмбеддинг от Yandex API"""
    yandex_api_key = os.environ.get('YANDEX_API_KEY')
    yandex_folder_id = os.environ.get('YANDEX_FOLDER_ID')
    
    if not yandex_api_key or not yandex_folder_id:
        raise ValueError("YANDEX_API_KEY и YANDEX_FOLDER_ID должны быть установлены")
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"
    headers = {
        "Authorization": f"Api-Key {yandex_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "modelUri": f"emb://{yandex_folder_id}/text-search-query/latest",
        "text": text
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    result = response.json()
    embedding = result.get('embedding')
    
    if not embedding:
        raise ValueError("Не удалось получить эмбеддинг от Yandex API")
    
    return embedding


def get_vector_store():
    """Получает доступ к ChromaDB через VectorStore класс"""
    return VectorStore()


@shared_task(name='vectorize_excursion')
def vectorize_excursion(excursion_id):
    """
    Задача для векторизации отдельной экскурсии
    """
    logger.info(f"Начало векторизации экскурсии ID: {excursion_id}")
    
    try:
        # Получаем данные экскурсии из базы данных
        logger.info(f"Получение данных экскурсии {excursion_id} из базы данных")
        excursion = get_excursion_by_id(excursion_id)
        
        if not excursion:
            logger.warning(f"Экскурсия {excursion_id} не найдена или не активна")
            return {'status': 'failed', 'message': 'Excursion not found or inactive'}
        
        (excursion_id_db, title, description, price, duration, location_type, category_name) = excursion
        
        location_type_map = {
            'city': 'Городские экскурсии',
            'suburban': 'Загородные экскурсии', 
            'russia': 'Туры по России'
        }
        
        tour_data = {
            "id": str(excursion_id_db),
            "title": title,
            "description": description or "",
            "price": float(price),
            "metadata": {
                "category": category_name or "Без категории",
                "location_type": location_type_map.get(location_type, location_type),
                "duration": duration
            }
        }
        
        logger.info(f"Данные экскурсии получены: {tour_data['title']}")
        
        # Подготовка текста для векторизации
        text_chunk = f"Тур: {tour_data['title']}. Цена от: {tour_data['price']} руб. Описание: {tour_data['description']}"
        logger.info(f"Подготовка текста для векторизации: {text_chunk[:100]}...")
        
        # Получаем вектор от Яндекса
        logger.info(f"Получение эмбеддинга от Yandex API")
        embedding = get_embedding(text_chunk)
        logger.info(f"Эмбеддинг получен успешно, размер: {len(embedding)}")
        
        # Получаем доступ к ChromaDB через VectorStore
        logger.info(f"Получение доступа к ChromaDB")
        vector_store = get_vector_store()
        
        # Добавляем в ChromaDB через VectorStore
        logger.info(f"Добавление документа в ChromaDB")
        vector_store.add_tour(
            tour_id=tour_data['id'],
            embedding=embedding,
            document=text_chunk,
            metadata=tour_data['metadata']
        )
        
        logger.info(f"Успешная векторизация экскурсии ID: {excursion_id}")
        return {
            'status': 'success',
            'excursion_id': excursion_id,
            'title': tour_data['title']
        }
        
    except Exception as e:
        logger.error(f"Ошибка при векторизации экскурсии {excursion_id}: {str(e)}")
        return {
            'status': 'failed',
            'excursion_id': excursion_id,
            'error': str(e)
        }
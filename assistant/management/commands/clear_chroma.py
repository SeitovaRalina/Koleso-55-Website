import shutil
import os
from django.core.management.base import BaseCommand
from assistant.services.chroma_db import VectorStore


class Command(BaseCommand):
    help = 'Полная очистка ChromaDB (удаление всех данных)'

    def handle(self, *args, **options):
        vector_store = VectorStore()
        
        try:
            # Получаем все документы в коллекции
            result = vector_store.collection.get()
            
            if result and result.get('ids'):
                ids_to_delete = result['ids']
                count = len(ids_to_delete)
                
                # Удаляем все документы по ID
                vector_store.collection.delete(ids=ids_to_delete)
                self.stdout.write(self.style.SUCCESS(f'Удалено {count} документов из коллекции'))
            else:
                self.stdout.write(self.style.WARNING('Коллекция уже пуста'))
            
            # Полностью удаляем и пересоздаем клиент (для исправления поврежденных данных)
            persist_dir = vector_store.persist_directory
            if os.path.exists(persist_dir):
                shutil.rmtree(persist_dir)
                os.makedirs(persist_dir, exist_ok=True)
                self.stdout.write(self.style.SUCCESS(f'Удалены все данные из {persist_dir}'))
                
                # Пересоздаем клиент и коллекцию
                vector_store.client = vector_store.client.__class__(path=persist_dir)
                vector_store.collection = vector_store.client.get_or_create_collection(name=vector_store.collection_name)
                self.stdout.write(self.style.SUCCESS('Клиент и коллекция пересозданы'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при очистке коллекции: {str(e)}'))
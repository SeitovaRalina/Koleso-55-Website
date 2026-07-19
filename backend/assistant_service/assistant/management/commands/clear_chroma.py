import chromadb
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Очистка коллекции в ChromaDB'

    def handle(self, *args, **options):
        persist_directory = settings.CHROMA_PERSIST_DIR
        
        try:
            # Создаем новый клиент и получаем коллекцию
            client = chromadb.PersistentClient(path=persist_directory)
            collection = client.get_or_create_collection(name="tours_collection")
            
            # Получаем все документы в коллекции
            result = collection.get()
            
            if result and result.get('ids'):
                ids_to_delete = result['ids']
                count = len(ids_to_delete)
                
                # Удаляем все документы по ID
                collection.delete(ids=ids_to_delete)
                self.stdout.write(self.style.SUCCESS(f'Удалено {count} документов из коллекции'))
            else:
                self.stdout.write(self.style.WARNING('Коллекция уже пуста'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при очистке коллекции: {str(e)}'))

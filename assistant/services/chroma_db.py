import os
import chromadb
from django.conf import settings

class VectorStore:
    def __init__(self):
        self.persist_directory = "/app/chroma_data"
        
        self.client = chromadb.PersistentClient(path=self.persist_directory) #cоздаем клиента базы данных
        
        self.collection_name = "tours_collection" 
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_tours(self, ids, embeddings, documents, metadatas): #Метод для добавления данных в базу(вызывается в ingest_tours)
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(self, query_vector, top_k=2): #Поиск ближайших векторов
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k
        )
        
        if results and results.get('documents') and results['documents']:
            return results['documents'][0]
        return []
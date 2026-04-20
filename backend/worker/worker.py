import pika
import json
import os
import logging
from transformers import AutoTokenizer, AutoModel
import torch
import chromadb
from chromadb.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcursionVectorizer:
    def __init__(self):
        self.rubert_model_name = "cointegrated/rubert-tiny2"
        self.tokenizer = None
        self.model = None
        self.chroma_client = None
        self.collection = None
        
    def load_models(self):
        logger.info("Loading RuBERT model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.rubert_model_name)
        self.model = AutoModel.from_pretrained(self.rubert_model_name)
        logger.info("RuBERT model loaded successfully")
        
    def init_chromadb(self):
        chromadb_url = os.getenv('CHROMADB_URL', 'http://localhost:8000')
        logger.info(f"Connecting to ChromaDB at {chromadb_url}")
        
        # Use Settings to disable authentication
        settings = chromadb.config.Settings(
            allow_reset=False,
            anonymized_telemetry=False
        )
        
        self.chroma_client = chromadb.HttpClient(
            host=chromadb_url.split('//')[1].split(':')[0], 
            port=int(chromadb_url.split(':')[-1]),
            settings=settings
        )
        
        try:
            self.collection = self.chroma_client.get_or_create_collection("excursions")
            logger.info("Connected to 'excursions' collection")
        except Exception as e:
            logger.error(f"Error creating/getting collection: {e}")
            self.collection = self.chroma_client.create_collection("excursions")
            logger.info("Created new 'excursions' collection")
    
    def vectorize_text(self, text):
        if not self.tokenizer or not self.model:
            self.load_models()
            
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state[:, 0, :].numpy()
        
        return embeddings[0].tolist()
    
    def store_vector(self, excursion_id, text, vector):
        if not self.collection:
            self.init_chromadb()
            
        try:
            self.collection.add(
                ids=[str(excursion_id)],
                embeddings=[vector],
                documents=[text],
                metadatas=[{"excursion_id": excursion_id}]
            )
            logger.info(f"Stored vector for excursion {excursion_id}")
        except Exception as e:
            logger.error(f"Error storing vector: {e}")
    
    def process_message(self, message):
        try:
            data = json.loads(message)
            excursion_id = data['excursion_id']
            short_description = data['short_description']
            
            logger.info(f"Processing excursion {excursion_id}: {short_description[:50]}...")
            
            vector = self.vectorize_text(short_description)
            self.store_vector(excursion_id, short_description, vector)
            
            logger.info(f"Successfully processed excursion {excursion_id}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")

def main():
    vectorizer = ExcursionVectorizer()
    vectorizer.load_models()
    vectorizer.init_chromadb()
    
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')
    
    try:
        connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        channel = connection.channel()
        
        channel.queue_declare(queue='excursion_vectorization', durable=True)
        logger.info("Waiting for messages...")
        
        def callback(ch, method, properties, body):
            logger.info(f"Received message: {body}")
            vectorizer.process_message(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='excursion_vectorization', on_message_callback=callback)
        
        channel.start_consuming()
        
    except Exception as e:
        logger.error(f"Error connecting to RabbitMQ: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    main()

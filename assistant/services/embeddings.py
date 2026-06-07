import requests
from typing import List
from django.conf import settings

class EmbeddingsClient:
    def __init__(self):
        self.folder_id = settings.YANDEX_FOLDER_ID
        self.api_key = settings.YANDEX_API_KEY
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id,
            "Content-Type": "application/json"
        }

    def get_embedding(self, text: str) -> List[float]:
        payload = {
            "modelUri": f"emb://{self.folder_id}/text-search-query/latest",
            "text": text
        }
        response = requests.post(self.url, headers=self.headers, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()['embedding']
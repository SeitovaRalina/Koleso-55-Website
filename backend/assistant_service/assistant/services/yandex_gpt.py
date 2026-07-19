import requests
from typing import List, Dict

class YandexGPTClient:
    #Интеграция с Yandex Cloud LLM API
    def __init__(self, folder_id: str, api_key: str):
        self.folder_id = folder_id
        self.api_key = api_key 
        self.url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        self.headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "x-folder-id": self.folder_id,
            "Content-Type": "application/json"
        }

    def generate_response(self, messages: List[Dict[str, str]]) -> str: #контекст+история+новый вопросв YandexGPT

        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.2, 
                "maxTokens": "1000"
            },
            "messages": messages
        }
        
        response = requests.post(self.url, headers=self.headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        return data['result']['alternatives'][0]['message']['text']
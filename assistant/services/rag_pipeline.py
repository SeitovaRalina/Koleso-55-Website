import re
import requests
from django.conf import settings
from .chroma_db import VectorStore
from .embeddings import EmbeddingsClient

class RAGPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        self.embeddings_client = EmbeddingsClient()
        self.yandex_api_key = settings.YANDEX_API_KEY
        self.folder_id = settings.YANDEX_FOLDER_ID
        self.llm_url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    def _get_headers(self):
        """Вспомогательный метод для заголовков API"""
        return {
            "Authorization": f"Api-Key {self.yandex_api_key}",
            "x-folder-id": self.folder_id,
            "Content-Type": "application/json"
        }

    def _rewrite_query(self, user_question: str, history: list) -> str:
        if not history:
            return user_question

        system_prompt = (
            "Ты — технический фильтр. Твоя задача — восстановить контекст вопроса.\n"
            "ИНСТРУКЦИЯ:\n"
            "1. Если пользователь пишет '2 тур', 'этот', 'туда', 'детали', замени эти слова на конкретное название тура из истории диалога.\n"
            "2. Если сообщение состоит из имени и цифр ('алина 56789'), бессмысленных букв ('вапр') или короткого согласия ('да'), верни текст БЕЗ ИЗМЕНЕНИЙ.\n"
            "3. Выведи только финальный текст запроса. Точка."
        )
        
        messages = [{"role": "system", "text": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "text": msg["text"]})
        messages.append({"role": "user", "text": user_question})

        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite/latest",
            "completionOptions": {"stream": False, "temperature": 0.1, "maxTokens": "50"},
            "messages": messages
        }
        
        try:
            response = requests.post(self.llm_url, headers=self._get_headers(), json=payload, timeout=5)
            response.raise_for_status()
            rewritten_query = response.json()['result']['alternatives'][0]['message']['text'].strip()
            return rewritten_query.replace('"', '').replace("'", "")
        except Exception as e:
            print(f"[Rewriter Error] {e}")
            return user_question
        
    def generate_answer(self, user_question: str, history: list) -> str:
        if not re.search(r'[а-яА-ЯёЁ]', user_question) and re.search(r'[a-zA-Z]', user_question):
            allowed_eng_words = ["SPA", "VIP", "OK", "HI"]
            if user_question.strip().upper() not in allowed_eng_words:
                return "Кажется, вы забыли переключить раскладку клавиатуры. Напишите, пожалуйста, по-русски."

        digits = re.sub(r'\D', '', user_question)
        if len(digits) >= 5:
            if not re.fullmatch(r'[78]\d{10}', digits):
                return "Для оформления заявки нужен корректный номер: 11 цифр, начинается с 8 или +7."

        standalone_query = self._rewrite_query(user_question, history) #Трансформация запроса
        print(f"[DEBUG] Оригинальный запрос: {user_question}")
        print(f"[DEBUG] Переписанный запрос: {standalone_query}")

        try: #векторизация и поиск
            query_vector = self.embeddings_client.get_embedding(standalone_query)
        except requests.exceptions.ConnectionError:
            return "Прошу прощения, у меня пропала связь с сетью. Пожалуйста, отправьте сообщение еще раз."
        except Exception as e:
            print(f"[EMBEDDING ERROR] {e}")
            return "Произошла внутренняя ошибка. Попробуйте немного позже."

        results = self.vector_store.search(query_vector, top_k=2)
        current_context = "\n\n".join(results) if results else ""

        payload = self._build_prompt(current_context, standalone_query, history) #генерация ответа
        
        try:
            response = requests.post(self.llm_url, headers=self._get_headers(), json=payload, timeout=15)
            response.raise_for_status()
            raw_llm_answer = response.json()['result']['alternatives'][0]['message']['text']
        except requests.exceptions.ConnectionError:
            return "Связь с нейросетью прервалась. Пожалуйста, повторите запрос."
        except Exception as e:
            print(f"[YANDEXGPT ERROR] {e}")
            return "К сожалению, сервис генерации ответов сейчас недоступен."

        return self._process_lead_tag(raw_llm_answer)

    def _build_prompt(self, context: str, question: str, history: list) -> dict:
        system_prompt = (
            "Ты — справочный бот по туризму 'Путеводя'. Выдавай информацию сухо, как справочник.\n\n"
            "БАЗОВЫЕ ПРАВИЛА:\n"
            "1. Завершай свои ответы только утвердительными предложениями с точкой. Вопросительные знаки использовать нельзя.\n"
            "2. Бери информацию только из блока 'Контекст'. Если информации нет, пиши фразу: 'В базе нет подходящих вариантов.'\n"
            "3. На приветствия отвечай: 'Готов помочь с выбором тура.'\n\n"
            "БРОНИРОВАНИЕ:\n"
            "Шаг 1. Если клиент пишет 'как забронировать' или 'хочу забронировать', отвечай: 'Для оформления заявки напишите ваше Имя и номер телефона.'\n"
            "Шаг 2. Если в сообщении есть имя и телефон, вставь в начало скрытый тег: [LEAD: Имя | Телефон | Название тура] и напиши фразу: 'Заявка успешно принята. Наш менеджер свяжется с вами.' Больше ничего не пиши."
        )

        messages = [{"role": "system", "text": system_prompt}]
        
        for msg in history:
            messages.append({"role": msg["role"], "text": msg["text"]})
        
        user_content = (
            f"Контекст:\n{context}\n\n"
            f"Вопрос: {question}"
        )
        messages.append({"role": "user", "text": user_content})

        return {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite/latest",
            "completionOptions": {
                "stream": False, 
                "temperature": 0.1,
                "maxTokens": "1000"
            },
            "messages": messages
        }
    
    def _process_lead_tag(self, llm_text: str) -> str:
        match = re.search(r'\[LEAD:\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\]', llm_text)
        if match:
            client_name = match.group(1).strip()
            phone = match.group(2).strip()
            tour_name = match.group(3).strip()
            print("="*40)
            print(f">>> [MOCK DB SAVE] НОВАЯ ЗАЯВКА ИЗ ЧАТА!")
            print(f">>> Имя: {client_name}")
            print(f">>> Телефон: {phone}")
            print(f">>> Тур: {tour_name}")
            print("="*40)
            clean_text = re.sub(r'\[LEAD:.*?\]', '', llm_text).strip()
            return clean_text
        return llm_text
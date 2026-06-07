import re
import requests
from django.conf import settings
from .chroma_db import VectorStore
from .embeddings import EmbeddingsClient
from assistant.models import Client, LeadRequest, Excursion

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

        #историю в один текстовый блок
        history_text = ""
        for msg in history[-4:]:
            role_name = "Клиент" if msg["role"] == "user" else "Ассистент"
            history_text += f"{role_name}: {msg['text']}\n"

        system_prompt = (
            "Ты — строгий лингвистический скрипт. Твоя единственная задача — переписать запрос клиента, "
            "чтобы он был понятен без контекста.\n\n"
            "ПРАВИЛА:\n"
            "1. Если клиент использует местоимения ('туда', 'этот тур', 'он') или неполные предложения, "
            "замени их на конкретные названия туров из Истории.\n"
            "2. Если клиент пишет бессмысленный набор букв, свое имя, телефон, или запрос уже понятен сам по себе "
            "— верни текст клиента БЕЗ ИЗМЕНЕНИЙ.\n"
            "3. ЗАПРЕЩЕНО отвечать на вопрос клиента или генерировать факты.\n"
            "4. В ответе напиши ТОЛЬКО переписанный запрос. Никаких вводных слов."
        )
        
        #всё в одном сообщении
        user_content = (
            f"История диалога:\n{history_text}\n"
            f"Текущий запрос клиента: {user_question}\n\n"
            f"Твой ответ (только переписанный запрос):"
        )

        messages = [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": user_content}
        ]

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
        
    def generate_answer(self, user_question: str, history: list) -> dict:
        if not re.search(r'[а-яА-ЯёЁ]', user_question) and re.search(r'[a-zA-Z]', user_question):
            allowed_eng_words = ["SPA", "VIP", "OK", "HI"]
            if user_question.strip().upper() not in allowed_eng_words:
                return {"text": "Кажется, вы забыли переключить раскладку клавиатуры. Напишите, пожалуйста, по-русски.", "chips": []}

        digits_only = re.sub(r'\D', '', user_question)
        phone_candidate = re.sub(r'[^\d+]', '', user_question)
        
        is_booking_context = history and history[-1]["role"] == "assistant" and "номер телефона" in history[-1]["text"].lower()
        has_long_number = len(digits_only) >= 10
        
        if (is_booking_context and digits_only) or has_long_number:
            if not re.search(r'(?:\+7|8)\d{10}(?!\d)', phone_candidate):
                return {
                    "text": "Пожалуйста, введите правильный номер телефона: начиная с +7 или 8", 
                    "chips": []
                }

        #ТРАНСФОРМАЦИЯ ЗАПРОСА
        standalone_query = self._rewrite_query(user_question, history)
        print(f"[DEBUG] Оригинальный запрос: {user_question}")
        print(f"[DEBUG] Переписанный запрос: {standalone_query}")

        #ВЕКТОРИЗАЦИЯ И ПОИСК
        try:
            query_vector = self.embeddings_client.get_embedding(standalone_query)
        except requests.exceptions.ConnectionError as e:
            print(f"[EMBEDDING ERROR] {e}")
            return {"text": "Прошу прощения, у меня пропала связь с сетью. Пожалуйста, отправьте сообщение еще раз.", "chips": []}
        except Exception as e:
            print(f"[EMBEDDING ERROR] {e}")
            return {"text": "Произошла внутренняя ошибка. Попробуйте немного позже.", "chips": []}

        results = self.vector_store.search(query_vector, top_k=2)
        current_context = "\n\n".join(results) if results else ""

        #ГЕНЕРАЦИЯ ОТВЕТА
        payload = self._build_prompt(current_context, standalone_query, history) 
        
        try:
            response = requests.post(self.llm_url, headers=self._get_headers(), json=payload, timeout=15)
            response.raise_for_status()
            raw_llm_answer = response.json()['result']['alternatives'][0]['message']['text']
        except requests.exceptions.ConnectionError:
            return {"text": "Связь с нейросетью прервалась. Пожалуйста, повторите запрос.", "chips": []}
        except Exception as e:
            print(f"[YANDEXGPT ERROR] {e}")
            return {"text": "К сожалению, сервис генерации ответов сейчас недоступен.", "chips": []}

        #Лиды и Подсказки
        processed_answer = self._process_lead_tag(raw_llm_answer)
        
        chips = []
        chips_match = re.search(r'\[CHIPS:(.*?)\]', processed_answer)
        
        if chips_match:
            raw_chips = chips_match.group(1).split('|')
            chips = [chip.strip() for chip in raw_chips if chip.strip()]
            processed_answer = processed_answer.replace(chips_match.group(0), '').strip()

        return {
            "text": processed_answer,
            "chips": chips
        }
    
    def _build_prompt(self, context: str, question: str, history: list) -> dict:
        system_prompt = (
            "Ты — интеллектуальный туристический агент 'Путеводя'. Твоя задача — отвечать на вопросы, используя ТОЛЬКО факты из блока 'Контекст'.\n\n"
            "ЖЕСТКИЕ ПРАВИЛА АНАЛИЗА:\n"
            "1. Отвечай ИМЕННО на вопрос пользователя. Если он спрашивает про цены — пиши только про цены. Если про даты — только про даты. Не вываливай описание всех туров подряд.\n"
            "2. Внимательно сравнивай суть вопроса и Контекст. Если клиент ищет экскурсии, а в Контексте описан SPA-отдых — отвечай строго: 'К сожалению, таких вариантов сейчас нет.'\n"
            "3. Никогда не начинай ответ с шаблонной фразы 'В базе есть два варианта туров'. Отвечай естественно и связно.\n"
            "4. Завершай ответ точкой. Никаких встречных вопросов.\n\n"
            "БРОНИРОВАНИЕ (ВНИМАТЕЛЬНО ИЗУЧИ):\n"
            "Шаг 1. Если клиент хочет забронировать тур, отвечай: 'Для оформления заявки напишите ваше Имя и номер телефона.'\n"
            "Шаг 2. Если клиент уже указал имя и контакт, СНАЧАЛА ПРОВЕРЬ НОМЕР. Если в номере меньше 10 цифр или присутствуют посторонние буквы (например, '6789шщ'), напиши: 'Пожалуйста, введите корректный номер телефона (от 10 цифр), чтобы менеджер смог с вами связаться.' НЕ ГЕНЕРИРУЙ ТЕГ LEAD.\n"
            "Шаг 3. Только если номер телефона похож на настоящий, напиши: 'Заявка успешно принята. Наш менеджер свяжется с вами.' и вставь тег [LEAD: Имя | Телефон | Название тура].\n\n"
            "ПОДСКАЗКИ ДЛЯ ПОЛЬЗОВАТЕЛЯ:\n"
            "В конце ответа всегда предлагай 2-3 короткие фразы (до 4 слов) для уточнения поиска.\n"
            "Обязательно оберни их в тег: [CHIPS: фраза 1 | фраза 2 | фраза 3]."
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
            raw_phone = match.group(2).strip()
            tour_name = match.group(3).strip()
            
            clean_phone = re.sub(r'[^\d+]', '', raw_phone)
            
            try:
                client, created = Client.objects.get_or_create(
                    phone=clean_phone,
                    defaults={'first_name': client_name, 'last_name': 'Чат'}
                )
                
                search_title = tour_name[:15]
                excursion = Excursion.objects.filter(title__icontains=search_title).first()
                
                if excursion:
                    LeadRequest.objects.create(
                        client=client,
                        excursion=excursion,
                        status='new'
                    )
                    print(f"[DB SUCCESS] Создана заявка от {client_name} на тур: {excursion.title}")
                else:
                    print(f"[DB WARNING] Тур '{tour_name}' не найден в БД. Заявка не сохранена.")
                    
            except Exception as e:
                print(f"[DB ERROR] Ошибка при сохранении лида: {e}")
                
            clean_text = re.sub(r'\[LEAD:.*?\]', '', llm_text).strip()
            return clean_text
            
        return llm_text
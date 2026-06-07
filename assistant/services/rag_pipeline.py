import re
import requests
from django.conf import settings
from .chroma_db import VectorStore
from .embeddings import EmbeddingsClient
from assistant.models import Client, LeadRequest, Excursion

class RAGPipeline:
    def init(self):
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
        if re.search(r'\d{10}', user_question):
            return user_question
            
        if not history:
            return user_question

        history_text = ""
        for msg in history[-4:]:
            role_name = "Клиент" if msg["role"] == "user" else "Ассистент"
            history_text += f"{role_name}: {msg['text']}\n"

        system_prompt = (
            "Ты — лингвистический скрипт. Твоя задача — сделать запрос клиента понятным без контекста.\n"
            "ПРАВИЛА:\n"
            "1. Если клиент использует местоимения ('туда', 'этот', 'его'), замени их на конкретные названия туров из Истории.\n"
            "2. Если клиент пишет имя и телефон — НЕ ПЕРЕПИСЫВАЙ, верни текст КАК ЕСТЬ.\n"
            "3. Если запрос уже содержит название тура — верни его как есть.\n"
            "4. В ответе только переписанный запрос. Никаких вводных слов."
        )
        
        user_content = (
            f"История диалога:\n{history_text}\n"
            f"Текущий запрос: {user_question}\n\n"
            f"Твой ответ:"
        )

        messages = [
            {"role": "system", "text": system_prompt},
            {"role": "user", "text": user_content}
        ]

        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite/latest",
            "completionOptions": {"stream": False, "temperature": 0.1, "maxTokens": "60"},
            "messages": messages
        }
        
        try:
            response = requests.post(self.llm_url, headers=self._get_headers(), json=payload, timeout=5)
            response.raise_for_status()
            rewritten_query = response.json()['result']['alternatives'][0]['message']['text'].strip()
            
            if "брони" in user_question.lower() and "«" not in rewritten_query:
                for msg in reversed(history):
                    match_tour = re.search(r'«(.*?)»', msg["text"])
                    if match_tour:
                        rewritten_query = f"{rewritten_query} {match_tour.group(0)}"
                        break
                        
            return rewritten_query.replace('"', '').replace("'", "")
        except Exception as e:
            print(f"[Rewriter Error] {e}")
            return user_question
        
    def generate_answer(self, user_question: str, history: list) -> dict:
        if not re.search(r'[а-яА-ЯёЁ]', user_question) and re.search(r'[a-zA-Z]', user_question):
            allowed_eng_words = ["SPA", "VIP", "OK", "HI"]
            if user_question.strip().upper() not in allowed_eng_words:
                return {"text": "Кажется, вы забыли переключить раскладку клавиатуры. Напишите, пожалуйста, по-русски.", "chips": []}
            #телефон
        digits_only = re.sub(r'\D', '', user_question)
        phone_candidate = re.sub(r'[^\d+]', '', user_question)
        is_booking_context = history and history[-1]["role"] == "assistant" and "номер телефона" in history[-1]["text"].lower()
        has_long_number = len(digits_only) >= 10
        
        if (is_booking_context and digits_only) or has_long_number:
            if not re.search(r'(?:\+7|8)\d{10}(?!\d)', phone_candidate):
                return {
                    "text": "Пожалуйста, введите правильный номер телефона: начиная с 8.", 
                    "chips": []
                }

        #трансформация запроса
        standalone_query = self._rewrite_query(user_question, history)
        print(f"[DEBUG] Оригинальный запрос: {user_question}")
        print(f"[DEBUG] Переписанный запрос: {standalone_query}")

        #поиск по вектору
        try:
            query_vector = self.embeddings_client.get_embedding(standalone_query)
        except Exception as e:
            print(f"[EMBEDDING ERROR] {e}")
            return {"text": "Произошла внутренняя ошибка. Попробуйте немного позже.", "chips": []}

        results = self.vector_store.search(query_vector, top_k=2)
        current_context = "\n\n".join(results) if results else ""

        payload = self._build_prompt(current_context, standalone_query, history) 
        
        #инъекция для принудительной генерации LEAD тега, если есть признаки бронирования
        if re.search(r'\d{10}', user_question) and any(word in user_question.lower() for word in ["брони", "заяв", "хочу"]):
            payload["messages"].append({
                "role": "user", 
                "text": "ВНИМАНИЕ: Если контакты есть в запросе, ОБЯЗАТЕЛЬНО добавь в ответ тег [LEAD: Имя | Телефон | Название тура]."
            })
        
        try:
            response = requests.post(self.llm_url, headers=self._get_headers(), json=payload, timeout=15)
            response.raise_for_status()
            raw_llm_answer = response.json()['result']['alternatives'][0]['message']['text']
        except Exception as e:
            print(f"[YANDEXGPT ERROR] {e}")
            return {"text": "К сожалению, сервис генерации ответов сейчас недоступен.", "chips": []}

        #LEAD тег и Chips
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
        last_tour = "не указан"
        for msg in reversed(history):
            match = re.search(r'«(.*?)»', msg["text"])
            if match:
                last_tour = match.group(1)
                break
        
        system_prompt = (
            f"Твой текущий обсуждаемый тур: «{last_tour}».\n"
            "ПРАВИЛО БРОНИРОВАНИЯ: Если пользователь хочет бронировать, ты ДОЛЖЕН использовать название текущего тура: «{last_tour}».\n"
            "Ты — интеллектуальный туристический агент 'Путеводя'. Твоя задача — отвечать на вопросы, используя ТОЛЬКО факты из блока 'Контекст'.\n\n"
            "ЖЕСТКИЕ ПРАВИЛА АНАЛИЗА:\n"
            "1. Отвечай ИМЕННО на вопрос пользователя. Если он спрашивает про цены — пиши только про цены. Если про даты — только про даты. Не вываливай описание всех туров подряд.\n"
            "2. Внимательно сравнивай суть вопроса и Контекст. Если клиент ищет экскурсии, а в Контексте описан SPA-отдых — отвечай строго: 'К сожалению, таких вариантов сейчас нет.'\n"
            "3. Никогда не начинай ответ с шаблонной фразы 'В базе есть два варианта туров'. Отвечай естественно и связно.\n"
            "4. Завершай ответ точкой. Никаких встречных вопросов.\n\n"
            "БРОНИРОВАНИЕ (ВНИМАТЕЛЬНО ИЗУЧИ):\n"
            "Шаг 1. ПЕРЕД ТЕМ КАК ЗАПРАШИВАТЬ ИМЯ И ТЕЛЕФОН, проверь, нет ли их в текущем запросе пользователя. "
            "Если в текущем сообщении есть Имя и Телефон (10 цифр), генерируй тег: [LEAD: Имя | Телефон | Название тура].\n"
            "Шаг 2. Если данных нет, отвечай: 'Для оформления заявки напишите ваше Имя и номер телефона.'\n"
            "Шаг 3. Если номер указан неверно, напиши: 'Пожалуйста, введите корректный номер телефона.'\n"
            "Шаг 4. Если номер верный, напиши ИМЕННО ТАК: 'Заявка успешно принята, менеджер свяжется с Вами.'\n"
            "После этой фразы ОБЯЗАТЕЛЬНО добавь технический тег для системы (он скрыт от клиента): [LEAD: Имя | Телефон | Название тура].\n"
            "ПРИМЕР ОТВЕТА: Заявка успешно принята, менеджер свяжется с Вами. [LEAD: Алёна | 89067890987 | Зимняя сказка]\n\n"
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
            print(f"[DEBUG] Анализирую ответ LLM: {llm_text}")
            from assistant.models import ChatState, Client, LeadRequest, Excursion
            
            match = re.search(r'\[LEAD:\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\]', llm_text)
            if match:
                client_name = match.group(1).strip()
                raw_phone = match.group(2).strip()
                tour_name = match.group(3).strip()
                
                clean_phone = re.sub(r'[^\d+]', '', raw_phone)
                
                clean_tour_name = tour_name.split('/')[0].strip().replace('«', '').replace('»', '').replace('"', '').replace("'", "")
                
                try:
                    client, created = Client.objects.get_or_create(
                        phone=clean_phone,
                        defaults={'first_name': client_name, 'last_name': 'Чат'}
                    )
                    
                    chat_state, _ = ChatState.objects.get_or_create(client=client)
                    
                    search_title = clean_tour_name[:20]
                    excursion = Excursion.objects.filter(title__icontains=search_title).first()
                    
                    if excursion:
                        LeadRequest.objects.create(
                            chat_state=chat_state,
                            excursion=excursion,
                            status='new'
                        )
                        print(f"[DB SUCCESS] Создана заявка от {client_name} на тур: {excursion.title}")
                    else:
                        print(f"[DB WARNING] Тур '{clean_tour_name}' не найден в БД.")
                        
                except Exception as e:
                    print(f"[DB ERROR] Ошибка при сохранении лида: {e}")
                    
                clean_text = re.sub(r'\[LEAD:.*?\]', '', llm_text).strip()
                return clean_text
                
            return llm_text
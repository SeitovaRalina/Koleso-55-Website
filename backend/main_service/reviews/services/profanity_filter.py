import threading

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class ToxicityFilter:
    _instance = None
    _model = None
    _tokenizer = None
    _load_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is not None and self._tokenizer is not None:
            return

        with self._load_lock:
            if self._model is not None and self._tokenizer is not None:
                return

            self._load_model_files()

    def _load_model_files(self):
        model_name = "cointegrated/rubert-tiny-toxicity"
        print(f"[{model_name}] Загрузка модели токсичности для русского языка...")

        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_name)

        self._model.eval()
        print("Модель RuBERT-tiny-toxicity успешно загружена и готова к работе.")

    def is_toxic(self, text: str, threshold: float = 0.75) -> dict:
        """
        Возвращает результат анализа токсичности текста на русском языке.
        Returns:
            {
                "is_toxic": bool,
                "score": float      # вероятность токсичности (0.0 - 1.0)
            }
        """
        if not text or len(text.strip()) < 3:
            return {"is_toxic": False, "score": 0.0}

        self._load_model()

        with torch.no_grad():
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            outputs = self._model(**inputs)
            proba = torch.sigmoid(outputs.logits).cpu().numpy()[0]

            score = 1 - (proba[0] * (1 - proba[-1]))

        is_toxic = score >= threshold

        return {
            "is_toxic": is_toxic,
            "score": round(score, 4)
        }


toxicity_filter = ToxicityFilter()

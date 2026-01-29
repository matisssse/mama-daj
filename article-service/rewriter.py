"""
Модуль для рерайта статей с использованием AI (локальная LLM через Ollama)
"""

import os
import logging
import requests
import time
import json

logger = logging.getLogger(__name__)


class ArticleRewriter:
    """Класс для рерайта статей с использованием локальной LLM через Ollama"""
    
    def __init__(self):
        # Настройки Ollama
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://ollama:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.max_retries = 3
        
        # Проверяем доступность Ollama
        self._check_ollama_availability()
    
    def _check_ollama_availability(self):
        """Проверяет доступность Ollama API"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                logger.info(f"Ollama доступен. Доступные модели: {model_names}")
                
                # Проверяем наличие нужной модели
                if not any(self.model in name for name in model_names):
                    logger.warning(f"Модель {self.model} не найдена. Доступные модели: {model_names}")
                    logger.warning(f"Выполните: docker compose exec ollama ollama pull {self.model}")
            else:
                logger.warning(f"Ollama недоступен (статус {response.status_code})")
        except Exception as e:
            logger.warning(f"Не удалось подключиться к Ollama: {e}")
            logger.warning("Убедитесь, что сервис Ollama запущен")
    
    def _call_ollama(self, prompt, system_prompt, max_tokens=2000, temperature=0.8):
        """
        Вызывает Ollama API для генерации текста
        
        Args:
            prompt: Текст запроса
            system_prompt: Системный промпт
            max_tokens: Максимальное количество токенов в ответе
            temperature: Температура генерации (0.0-1.0)
            
        Returns:
            str: Сгенерированный текст
        """
        url = f"{self.ollama_url}/api/generate"
        
        # Формируем полный промпт с системным сообщением
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=120  # Увеличенный таймаут для локальной генерации
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '').strip()
                else:
                    logger.error(f"Ошибка Ollama API (статус {response.status_code}): {response.text}")
                    
            except requests.exceptions.Timeout:
                logger.error(f"Таймаут при обращении к Ollama (попытка {attempt + 1})")
            except Exception as e:
                logger.error(f"Ошибка при обращении к Ollama (попытка {attempt + 1}): {e}")
            
            if attempt < self.max_retries - 1:
                wait_time = 2 ** attempt
                logger.info(f"Ожидание {wait_time} секунд перед повтором...")
                time.sleep(wait_time)
        
        return None
    
    def rewrite(self, article):
        """
        Делает рерайт статьи для SEO оптимизации
        
        Args:
            article: Словарь с данными статьи (title, content, url, image_url)
            
        Returns:
            Словарь с переписанной статьей
        """
        try:
            # Рерайт заголовка
            new_title = self._rewrite_title(article['title'])
            
            # Рерайт контента
            new_content = self._rewrite_content(article['content'], new_title)
            
            return {
                'title': new_title,
                'content': new_content,
                'image_url': article.get('image_url'),
                'original_url': article.get('url'),
            }
        
        except Exception as e:
            logger.error(f"Ошибка рерайта статьи: {e}", exc_info=True)
            return article
    
    def _rewrite_title(self, title):
        """Переписывает заголовок статьи"""
        system_prompt = "Ты профессиональный копирайтер и SEO-специалист."
        
        prompt = f"""Перепиши этот заголовок статьи, сохраняя смысл, но используя другие слова и структуру.
Заголовок должен быть привлекательным, SEO-оптимизированным и уникальным.
Верни только новый заголовок без дополнительных объяснений.

Оригинальный заголовок: {title}

Новый заголовок:"""
        
        new_title = self._call_ollama(prompt, system_prompt, max_tokens=100, temperature=0.8)
        
        if new_title:
            # Удаляем возможные лишние символы
            new_title = new_title.strip().strip('"\'')
            logger.info(f"Заголовок переписан: {title} -> {new_title}")
            return new_title
        else:
            logger.warning("Используется оригинальный заголовок")
            return title
    
    def _rewrite_content(self, content, title):
        """Переписывает контент статьи"""
        # Разбиваем контент на части, если он слишком длинный
        max_chunk_length = 3000  # Символов для одного запроса
        
        if len(content) <= max_chunk_length:
            return self._rewrite_chunk(content, title, is_first=True, is_last=True)
        
        # Разбиваем на параграфы
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            if current_length + para_length > max_chunk_length and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [para]
                current_length = para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        # Переписываем каждую часть
        rewritten_chunks = []
        for i, chunk in enumerate(chunks):
            is_first = (i == 0)
            is_last = (i == len(chunks) - 1)
            rewritten = self._rewrite_chunk(chunk, title, is_first, is_last)
            rewritten_chunks.append(rewritten)
            
            # Задержка между запросами
            if not is_last:
                time.sleep(1)
        
        return '\n\n'.join(rewritten_chunks)
    
    def _rewrite_chunk(self, text, title, is_first=True, is_last=True):
        """Переписывает часть текста"""
        context = ""
        if is_first:
            context += f"Это начало статьи с заголовком '{title}'. "
        if is_last:
            context += "Это последняя часть статьи. "
        
        system_prompt = "Ты профессиональный копирайтер, специализирующийся на создании уникального SEO-оптимизированного контента."
        
        prompt = f"""{context}
Перепиши следующий текст статьи, полностью изменяя формулировки, но сохраняя все важные факты и смысл.

Требования:
1. Используй совершенно другие слова и структуру предложений
2. Сохрани все важные факты и информацию
3. Текст должен быть уникальным и естественным
4. Оптимизируй для SEO (используй ключевые слова естественно)
5. Пиши простым и понятным языком
6. Не добавляй никаких вводных фраз или заключений
7. Верни только переписанный текст

Оригинальный текст:
{text}

Переписанный текст:"""
        
        rewritten_text = self._call_ollama(prompt, system_prompt, max_tokens=2000, temperature=0.8)
        
        if rewritten_text:
            logger.info(f"Часть контента переписана ({len(text)} -> {len(rewritten_text)} символов)")
            return rewritten_text
        else:
            logger.warning("Используется оригинальный текст")
            return text

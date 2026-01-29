"""
Модуль для рерайта статей с использованием AI
"""

import os
import logging
import openai
import time

logger = logging.getLogger(__name__)


class ArticleRewriter:
    """Класс для рерайта статей с использованием OpenAI API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OPENAI_API_KEY не установлен. Рерайт будет недоступен.")
        else:
            openai.api_key = self.api_key
        
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_retries = 3
    
    def rewrite(self, article):
        """
        Делает рерайт статьи для SEO оптимизации
        
        Args:
            article: Словарь с данными статьи (title, content, url, image_url)
            
        Returns:
            Словарь с переписанной статьей
        """
        if not self.api_key:
            logger.error("Невозможно выполнить рерайт: API ключ не установлен")
            return article
        
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
        prompt = f"""Перепиши этот заголовок статьи, сохраняя смысл, но используя другие слова и структуру.
Заголовок должен быть привлекательным, SEO-оптимизированным и уникальным.
Верни только новый заголовок без дополнительных объяснений.

Оригинальный заголовок: {title}
"""
        
        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Ты профессиональный копирайтер и SEO-специалист."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.8,
                )
                
                new_title = response.choices[0].message.content.strip()
                logger.info(f"Заголовок переписан: {title} -> {new_title}")
                return new_title
            
            except Exception as e:
                logger.error(f"Ошибка рерайта заголовка (попытка {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Экспоненциальная задержка
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
"""
        
        for attempt in range(self.max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Ты профессиональный копирайтер, специализирующийся на создании уникального SEO-оптимизированного контента."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=2000,
                    temperature=0.8,
                )
                
                rewritten_text = response.choices[0].message.content.strip()
                logger.info(f"Часть контента переписана ({len(text)} -> {len(rewritten_text)} символов)")
                return rewritten_text
            
            except Exception as e:
                logger.error(f"Ошибка рерайта контента (попытка {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.warning("Используется оригинальный текст")
                    return text

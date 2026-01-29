"""
Модуль для публикации статей на WordPress
"""

import os
import logging
import requests
from urllib.parse import urljoin
import base64

logger = logging.getLogger(__name__)


class WordPressPublisher:
    """Класс для публикации статей на WordPress через REST API"""
    
    def __init__(self):
        self.wp_url = os.getenv('WORDPRESS_URL')
        self.wp_user = os.getenv('WORDPRESS_USER')
        self.wp_password = os.getenv('WORDPRESS_PASSWORD')
        
        if not all([self.wp_url, self.wp_user, self.wp_password]):
            logger.error("Не все переменные WordPress настроены (WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)")
        
        self.api_url = urljoin(self.wp_url, '/wp-json/wp/v2/')
        self.auth = self._get_auth_header()
        
        # Настройки публикации
        self.post_status = os.getenv('WORDPRESS_POST_STATUS', 'draft')  # draft или publish
        self.default_category = os.getenv('WORDPRESS_DEFAULT_CATEGORY', '1')
    
    def _get_auth_header(self):
        """Создает заголовок авторизации"""
        if not self.wp_user or not self.wp_password:
            return None
        
        credentials = f"{self.wp_user}:{self.wp_password}"
        token = base64.b64encode(credentials.encode()).decode()
        return f"Basic {token}"
    
    def publish(self, article):
        """
        Публикует статью на WordPress
        
        Args:
            article: Словарь с данными статьи (title, content, image_url)
            
        Returns:
            bool: True если публикация успешна, False иначе
        """
        if not self.auth:
            logger.error("Невозможно опубликовать: отсутствуют данные авторизации WordPress")
            return False
        
        try:
            # Загружаем изображение, если есть
            featured_media_id = None
            if article.get('image_url'):
                featured_media_id = self._upload_image(article['image_url'], article['title'])
            
            # Создаем пост
            post_data = {
                'title': article['title'],
                'content': self._format_content(article['content']),
                'status': self.post_status,
                'categories': [int(self.default_category)],
            }
            
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            
            # Добавляем мета-информацию в конец поста (опционально)
            if article.get('original_url') and os.getenv('ADD_SOURCE_LINK', 'false').lower() == 'true':
                post_data['content'] += f"\n\n<!-- Source: {article['original_url']} -->"
            
            # Отправляем запрос
            headers = {
                'Authorization': self.auth,
                'Content-Type': 'application/json',
            }
            
            response = requests.post(
                urljoin(self.api_url, 'posts'),
                json=post_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                post_id = response.json().get('id')
                post_url = response.json().get('link')
                logger.info(f"Статья успешно опубликована (ID: {post_id}): {post_url}")
                return True
            else:
                logger.error(f"Ошибка публикации статьи: {response.status_code} - {response.text}")
                return False
        
        except Exception as e:
            logger.error(f"Ошибка публикации статьи на WordPress: {e}", exc_info=True)
            return False
    
    def _format_content(self, content):
        """Форматирует контент для WordPress (добавляет HTML теги)"""
        # Разбиваем на параграфы и оборачиваем в <p>
        paragraphs = content.split('\n\n')
        formatted = []
        
        for para in paragraphs:
            if para.strip():
                formatted.append(f"<p>{para.strip()}</p>")
        
        return '\n'.join(formatted)
    
    def _upload_image(self, image_url, title):
        """
        Загружает изображение в медиабиблиотеку WordPress
        
        Args:
            image_url: URL изображения
            title: Название изображения
            
        Returns:
            int: ID загруженного изображения или None
        """
        try:
            # Скачиваем изображение
            img_response = requests.get(image_url, timeout=30)
            img_response.raise_for_status()
            
            # Определяем имя файла
            filename = image_url.split('/')[-1].split('?')[0]
            if not filename:
                filename = 'image.jpg'
            
            # Определяем тип контента
            content_type = img_response.headers.get('Content-Type', 'image/jpeg')
            
            # Загружаем в WordPress
            headers = {
                'Authorization': self.auth,
                'Content-Type': content_type,
                'Content-Disposition': f'attachment; filename="{filename}"',
            }
            
            response = requests.post(
                urljoin(self.api_url, 'media'),
                data=img_response.content,
                headers=headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                media_id = response.json().get('id')
                logger.info(f"Изображение загружено (ID: {media_id}): {filename}")
                return media_id
            else:
                logger.error(f"Ошибка загрузки изображения: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            logger.error(f"Ошибка загрузки изображения {image_url}: {e}")
            return None
    
    def test_connection(self):
        """Проверяет подключение к WordPress API"""
        try:
            headers = {'Authorization': self.auth}
            response = requests.get(
                urljoin(self.api_url, 'posts'),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Подключение к WordPress API успешно")
                return True
            else:
                logger.error(f"Ошибка подключения к WordPress API: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"Ошибка подключения к WordPress API: {e}")
            return False

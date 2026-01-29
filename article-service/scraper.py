"""
Модуль для парсинга статей с веб-сайтов
"""

import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random

logger = logging.getLogger(__name__)


class ArticleScraper:
    """Класс для парсинга статей с различных сайтов"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_site(self, site_url, max_articles=5):
        """
        Парсит статьи с указанного сайта
        
        Args:
            site_url: URL сайта для парсинга
            max_articles: Максимальное количество статей для парсинга
            
        Returns:
            Список словарей с данными статей
        """
        articles = []
        
        try:
            # Получаем главную страницу или страницу блога
            response = self.session.get(site_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Ищем ссылки на статьи
            article_links = self._find_article_links(soup, site_url)
            
            # Ограничиваем количество статей
            article_links = article_links[:max_articles]
            
            logger.info(f"Найдено {len(article_links)} ссылок на статьи")
            
            # Парсим каждую статью
            for link in article_links:
                try:
                    article = self._scrape_article(link)
                    if article:
                        articles.append(article)
                        # Задержка между запросами
                        time.sleep(random.uniform(1, 3))
                except Exception as e:
                    logger.error(f"Ошибка парсинга статьи {link}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Ошибка парсинга сайта {site_url}: {e}")
        
        return articles
    
    def _find_article_links(self, soup, base_url):
        """Находит ссылки на статьи на странице"""
        links = []
        
        # Ищем статьи по различным селекторам
        # Обычные паттерны для блогов и новостных сайтов
        selectors = [
            'article a[href]',
            '.post a[href]',
            '.article a[href]',
            '.entry a[href]',
            'a.post-link',
            'a.article-link',
            '.blog-post a[href]',
            'h2 a[href]',
            'h3 a[href]',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    # Проверяем, что это внутренняя ссылка
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        if full_url not in links:
                            links.append(full_url)
        
        # Если не нашли по селекторам, ищем все ссылки на том же домене
        if not links:
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    # Фильтруем нежелательные ссылки
                    if not any(x in full_url.lower() for x in ['contact', 'about', 'category', 'tag', '#']):
                        if full_url not in links:
                            links.append(full_url)
        
        return links
    
    def _scrape_article(self, url):
        """Парсит одну статью"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Извлекаем заголовок
            title = self._extract_title(soup)
            
            # Извлекаем контент
            content = self._extract_content(soup)
            
            # Извлекаем изображение
            image_url = self._extract_image(soup, url)
            
            if title and content:
                return {
                    'url': url,
                    'title': title,
                    'content': content,
                    'image_url': image_url,
                }
            else:
                logger.warning(f"Не удалось извлечь заголовок или контент из {url}")
                return None
        
        except Exception as e:
            logger.error(f"Ошибка парсинга статьи {url}: {e}")
            return None
    
    def _extract_title(self, soup):
        """Извлекает заголовок статьи"""
        # Пробуем различные варианты
        title = None
        
        # Сначала ищем в meta тегах
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content']
        
        # Затем в title
        if soup.title:
            title = soup.title.string
        
        # Затем в заголовках
        for tag in ['h1', 'h2']:
            heading = soup.find(tag)
            if heading:
                return heading.get_text(strip=True)
        
        return title
    
    def _extract_content(self, soup):
        """Извлекает основной контент статьи"""
        # Удаляем ненужные элементы
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Ищем контент по различным селекторам
        content_selectors = [
            'article',
            '.post-content',
            '.article-content',
            '.entry-content',
            '.content',
            'main',
            '.post-body',
        ]
        
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                # Извлекаем текст из параграфов
                paragraphs = content_element.find_all('p')
                if paragraphs:
                    text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    if len(text) > 200:  # Минимальная длина статьи
                        return text
        
        # Если не нашли, берем все параграфы на странице
        paragraphs = soup.find_all('p')
        if paragraphs:
            text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            if len(text) > 200:
                return text
        
        return None
    
    def _extract_image(self, soup, base_url):
        """Извлекает основное изображение статьи"""
        # Сначала ищем в Open Graph
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return urljoin(base_url, og_image['content'])
        
        # Затем ищем в article
        article = soup.find('article')
        if article:
            img = article.find('img')
            if img and img.get('src'):
                return urljoin(base_url, img['src'])
        
        # Ищем первое изображение с достаточным размером
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and not any(x in src.lower() for x in ['logo', 'icon', 'avatar', 'button']):
                return urljoin(base_url, src)
        
        return None

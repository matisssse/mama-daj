#!/usr/bin/env python3
"""
Article Scraper and Rewriter Service
Парсит статьи с сайтов, делает рерайт и публикует на WordPress
"""

import os
import time
import json
import logging
import schedule
from datetime import datetime
from scraper import ArticleScraper
from rewriter import ArticleRewriter
from publisher import WordPressPublisher

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/article-service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ArticleService:
    """Основной класс сервиса для работы с статьями"""
    
    def __init__(self):
        self.scraper = ArticleScraper()
        self.rewriter = ArticleRewriter()
        self.publisher = WordPressPublisher()
        self.sites_file = os.getenv('SITES_CONFIG_FILE', '/app/config/sites.json')
        self.processed_articles_file = '/app/data/processed_articles.json'
        self.processed_articles = self._load_processed_articles()
        
    def _load_processed_articles(self):
        """Загружает список уже обработанных статей"""
        try:
            if os.path.exists(self.processed_articles_file):
                with open(self.processed_articles_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка загрузки списка обработанных статей: {e}")
        return []
    
    def _save_processed_articles(self):
        """Сохраняет список обработанных статей"""
        try:
            os.makedirs(os.path.dirname(self.processed_articles_file), exist_ok=True)
            with open(self.processed_articles_file, 'r', encoding='utf-8') as f:
                json.dump(self.processed_articles, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения списка обработанных статей: {e}")
    
    def load_sites(self):
        """Загружает список сайтов для парсинга"""
        try:
            with open(self.sites_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('sites', [])
        except FileNotFoundError:
            logger.error(f"Файл конфигурации не найден: {self.sites_file}")
            return []
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации сайтов: {e}")
            return []
    
    def process_articles(self):
        """Основной метод обработки статей"""
        logger.info("Начало обработки статей...")
        
        sites = self.load_sites()
        if not sites:
            logger.warning("Список сайтов пуст или не загружен")
            return
        
        for site in sites:
            try:
                site_url = site.get('url')
                site_name = site.get('name', site_url)
                max_articles = site.get('max_articles', 5)
                
                logger.info(f"Обработка сайта: {site_name} ({site_url})")
                
                # Парсинг статей
                articles = self.scraper.scrape_site(site_url, max_articles)
                logger.info(f"Найдено {len(articles)} статей на {site_name}")
                
                for article in articles:
                    try:
                        # Проверяем, не обрабатывали ли мы уже эту статью
                        article_url = article.get('url')
                        if article_url in self.processed_articles:
                            logger.info(f"Статья уже обработана: {article_url}")
                            continue
                        
                        # Рерайт статьи
                        logger.info(f"Рерайт статьи: {article.get('title', 'без названия')}")
                        rewritten_article = self.rewriter.rewrite(article)
                        
                        # Публикация на WordPress
                        logger.info(f"Публикация статьи: {rewritten_article.get('title')}")
                        published = self.publisher.publish(rewritten_article)
                        
                        if published:
                            self.processed_articles.append(article_url)
                            self._save_processed_articles()
                            logger.info(f"Статья успешно опубликована: {rewritten_article.get('title')}")
                            
                            # Задержка между публикациями для естественности
                            delay = int(os.getenv('PUBLISH_DELAY_SECONDS', '300'))
                            logger.info(f"Ожидание {delay} секунд перед следующей публикацией...")
                            time.sleep(delay)
                        else:
                            logger.error(f"Не удалось опубликовать статью: {rewritten_article.get('title')}")
                    
                    except Exception as e:
                        logger.error(f"Ошибка обработки статьи: {e}", exc_info=True)
                        continue
            
            except Exception as e:
                logger.error(f"Ошибка обработки сайта {site_name}: {e}", exc_info=True)
                continue
        
        logger.info("Обработка статей завершена")
    
    def run(self):
        """Запуск сервиса с расписанием"""
        # Получаем расписание из переменных окружения
        schedule_time = os.getenv('SCHEDULE_TIME', '03:00')  # По умолчанию в 3 часа ночи
        
        logger.info(f"Сервис запущен. Расписание: каждый день в {schedule_time}")
        
        # Настраиваем расписание
        schedule.every().day.at(schedule_time).do(self.process_articles)
        
        # Опциональный запуск при старте
        if os.getenv('RUN_ON_STARTUP', 'false').lower() == 'true':
            logger.info("Запуск обработки статей при старте...")
            self.process_articles()
        
        # Основной цикл
        while True:
            schedule.run_pending()
            time.sleep(60)  # Проверяем расписание каждую минуту


if __name__ == '__main__':
    try:
        service = ArticleService()
        service.run()
    except KeyboardInterrupt:
        logger.info("Сервис остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise

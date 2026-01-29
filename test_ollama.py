#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности Ollama
"""

import requests
import json
import sys

def test_ollama_connection(url="http://localhost:11434"):
    """Проверяет подключение к Ollama"""
    print(f"🔍 Проверка подключения к Ollama ({url})...")
    
    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama доступен!")
            print(f"📦 Установленные модели: {len(models)}")
            for model in models:
                print(f"   - {model.get('name')} (размер: {model.get('size', 0) / 1e9:.1f} GB)")
            return True
        else:
            print(f"❌ Ollama вернул статус {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Не удалось подключиться к Ollama: {e}")
        return False


def test_ollama_generation(url="http://localhost:11434", model="llama3.2"):
    """Тестирует генерацию текста с помощью Ollama"""
    print(f"\n🧪 Тестирование генерации текста (модель: {model})...")
    
    prompt = "Перепиши этот заголовок: 'Искусственный интеллект изменяет мир технологий'"
    system_prompt = "Ты профессиональный копирайтер."
    
    payload = {
        "model": model,
        "prompt": f"{system_prompt}\n\n{prompt}",
        "stream": False,
        "options": {
            "temperature": 0.8,
            "num_predict": 100,
        }
    }
    
    try:
        print("⏳ Генерация текста (это может занять некоторое время)...")
        response = requests.post(
            f"{url}/api/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '').strip()
            
            print(f"✅ Генерация успешна!")
            print(f"📝 Оригинал: {prompt}")
            print(f"✨ Результат: {generated_text}")
            
            # Статистика
            eval_count = result.get('eval_count', 0)
            eval_duration = result.get('eval_duration', 0) / 1e9  # наносекунды в секунды
            
            if eval_count > 0 and eval_duration > 0:
                tokens_per_sec = eval_count / eval_duration
                print(f"⚡ Скорость: {tokens_per_sec:.1f} токенов/сек")
                print(f"⏱️  Время: {eval_duration:.2f} секунд")
            
            return True
        else:
            print(f"❌ Ошибка генерации (статус {response.status_code}): {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут при генерации текста")
        return False
    except Exception as e:
        print(f"❌ Ошибка при генерации: {e}")
        return False


def main():
    print("=" * 60)
    print("🚀 Тест Ollama для Article Service")
    print("=" * 60)
    
    # Проверка подключения
    if not test_ollama_connection():
        print("\n⚠️  Убедитесь, что Ollama запущен:")
        print("   docker compose up -d ollama")
        sys.exit(1)
    
    # Тест генерации
    if not test_ollama_generation():
        print("\n⚠️  Убедитесь, что модель загружена:")
        print("   docker compose exec ollama ollama pull llama3.2")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Все тесты пройдены успешно!")
    print("🎉 Ollama готов к использованию для рерайта статей")
    print("=" * 60)


if __name__ == "__main__":
    main()

[![CI workflow](https://github.com/leomag/fastapi-demo/actions/workflows/main.yml/badge.svg)](https://github.com/leomag/fastapi-demo/actions/workflows/main.yml)


## 📌 FastAPI Demo — демонстрационное backend-приложение

**FastAPI Demo** — это пример backend-сервиса, реализованного на базе фреймворка FastAPI. Проект демонстрирует базовую архитектуру REST API, работу с базой данных и применение асинхронного подхода в Python.

![Screenshot](.github/fastapi-demo.png)

---

## 🚀 Основные возможности

- Реализация REST API с CRUD-операциями  
- Асинхронное взаимодействие с [Exchange API](https://github.com/fawazahmed0/exchange-api/)
- ML модель, определяющая на каком языке написано сообщение
- Работа с SQLite
- Валидация данных с использованием Pydantic  
- Автоматическая генерация документации (Swagger/Redoc)   
- ML-модели хранятся в DVC

---

## 🏗️ Архитектура

Проект построен по классической слоистой архитектуре:

- **API слой** — обработка HTTP-запросов  
- **Сервисный слой** — бизнес-логика  
- **Слой данных** — модели и работа с БД  

Такой подход упрощает масштабирование и поддержку кода.

---

## 🧰 Используемый стек

- Python 3.x  
- FastAPI
- Uvicorn  
- SQLAlchemy
- Scikit-learn
- PostgreSQL  
- Pydantic  
- Isort
- Black
- Flake8
- Docker

---

## ⚙️ Развертывание

Проект можно запускать:

- локально (через uvicorn)  
- в Docker-контейнере  

---

## 🎯 Цель проекта

- Показать базовый шаблон FastAPI-приложения  
- Продемонстрировать лучшие практики организации backend-кода  
- Показать практики CI (линтинг, тесты, сборка приложения и упаковка в docker-образ c сохранением в GHCR)
- Показать практики CD (деплой сервиса в [Render](https://render.com))
- Служить отправной точкой для разработки production-ready сервисов  

---

## DVC
- Для нормальной работы с DVC нужно использовать платное S3
- Плагин [dvc-yadisk](https://pypi.org/project/dvc-yadisk/) является сторонним и не поддерживается официально командой DVC, в отличие от настройки через S3 (Yandex Cloud), которая работает стабильнее
- Поэтому прикладываю ссылку на [модель](https://drive.google.com/drive/folders/1dk7PHTnqFChWLFuQDY90mKPbB97bAWT4?usp=share_link), которую нужно скачать и положить в директорию 'models/' внутри проекта

## ⚙️ Запуск проекта

### 🔹 Локальный запуск через Docker

1. Клонируйте репозиторий:
```bash
git clone https://github.com/leomag/fastapi-demo.git
cd fastapi-demo
pip install -r requirements.txt
```
Опционально (если у вас есть свой яндекс диск, где уже хранится модель через DVC)
```bash
dvc-yadisk-enable
dvc remote modify --local remote_name token YANDEX_OAUTH_TOKEN
dvc pull
```
2. Соберите docker-образ, запустите его в контейнере:
```bash
docker build -t fastapi-demo .
docker run -d -p 8000:8000 fastapi-demo
```

Приложение будет доступно по адресу:
http://localhost:8000

Swagger-документация:
http://localhost:8000/docs

Redoс-документация:
http://localhost:8000/redoc
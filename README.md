# HTTP API пользователей после аудита (Flask + SQLite)

## О проекте

**Что делает.** Демонстрационный **HTTP API на Flask**: пользователи в **SQLite**, пароли как **bcrypt** в БД, демо фоновой задачи с синхронизацией потоков. Код получен **аудитом и рефакторингом** исходных учебных фрагментов (`utils.py`, проблемный Flask-слой) по конвенциям [Guide](https://github.com/SpiritWalker84/Guide) (`docs/conventions/`): модульность, ООП, параметризованный SQL, явные HTTP-контракты.

**Как запускать.** Из корня: `cp .env.example .env` (при необходимости задайте `FLASK_SECRET_KEY`), затем `docker compose up -d --build`. Проверка: `curl -s http://127.0.0.1:5000/health`. Остановка: `docker compose down`.

Исходящие вызовы к своему API при типичном развёртывании идут по **HTTP**. **TLS** на стороне приложения не поднимается — при необходимости его задаёт **обратный прокси** или ingress.

**Ограничения:** одна БД **SQLite** на томе; в Compose используется **один** процесс Gunicorn, что согласовано с файлом БД. Для высокой нагрузки нужны отдельная СУБД и горизонтальное масштабирование за прокси.

## Стек технологий

- Python **3.12**, **Flask** 3.x, **Gunicorn**, **bcrypt**
- **SQLite** (файл на томе `/data` в контейнере)
- **Docker** / **Docker Compose**, **pytest** (см. `requirements-dev.txt`)

## Структура репозитория

| Путь | Назначение |
|------|------------|
| `src/vpf11/` | Пакет приложения: конфиг, БД, репозитории, сервисы, HTTP blueprint |
| `src/vpf11/app_factory.py` | Фабрика `create_app()` |
| `wsgi.py` | Точка входа Gunicorn (`app`) |
| `docker-compose.yml`, `Dockerfile` | Сборка и запуск веб-сервиса |
| `requirements.txt` | Зависимости продакшена |
| `requirements-dev.txt` | Зависимости для тестов |
| `openapi.yaml` | Контракт API **OpenAPI 3.1**; выдаётся также как `GET /openapi.yaml` |
| `tests/` | Смоук-тесты API |

## Запуск

### Docker Compose (основной способ)

Из корня репозитория:

```bash
cp .env.example .env
# При необходимости: FLASK_SECRET_KEY (см. .env.example)

docker compose up -d --build
```

Проверка: `curl -s http://127.0.0.1:5000/health`

Остановка: `docker compose down`

### Локально (без Docker)

Нужен Python **3.12**.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

export PYTHONPATH=src
export DATABASE_PATH=./data/app.db
mkdir -p data
python -c "from vpf11.app_factory import create_app; create_app().run(host='0.0.0.0', port=5000)"
```

Для продакшен-подобного запуска на хосте из корня с `PYTHONPATH=src`:  
`gunicorn -w 1 -b 0.0.0.0:5000 wsgi:app`

## Конфигурация

См. **`.env.example`**:

| Переменная | Обязательность | Описание |
|------------|----------------|----------|
| `DATABASE_PATH` | нет | Путь к файлу SQLite; в Docker по умолчанию задаётся в `docker-compose.yml` (`/data/app.db`) |
| `FLASK_SECRET_KEY` | нет | Секрет Flask; в Compose можно задать через `.env` или окружение хоста |

## API (кратко)

- `GET /health` — проверка живости
- `POST /api/users` — создать пользователя, JSON `{ "name", "tags"? }` → **201** и `id`
- `GET /api/users/<id>` — получить пользователя → **200** / **404**
- `GET /api/users/by-name?name=...` — поиск по имени
- `POST /api/users/<id>/credentials` — задать пароль `{ "password" }` (хеш в БД)
- `POST /api/background-task` или `POST /bg` — демо фонового потока; тело опционально `{ "id" }` → **202**
- `GET /openapi.yaml` — актуальная спецификация OpenAPI

Алиасы учебного примера: **`POST /adducer`**, **`GET /user/<id>`** (в пути только целое `id`). В спецификации нет путей вроде `/adduser`, `/activate/{id}`, `/slow`, `/wrong` — они от другого примера.

## Разработка и тесты

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```

## Запуск проекта через Docker Compose

### Что запускается

`docker-compose.yaml` поднимает все части проекта одной командой:

- **backend**: Django API (порт **8000**)
- **db**: PostgreSQL (порт **5432**)
- **redis**: Redis (порт **6379**)
- **celery**: Celery worker
- **celery_beat**: Celery Beat (планировщик задач)

Все сервисы берут переменные окружения из файла `.env`.

---

### Подготовка переменных окружения

1) Создайте файл `.env` в корне проекта на основе шаблона:

```bash
cp .env.example .env
```

Для Windows (PowerShell):

```powershell
Copy-Item .env.example .env
```

2) При необходимости поменяйте значения (пароли, ключи и т.д.) в `.env`.

---

### Запуск

Запуск всех сервисов одной командой:

```bash
docker compose up --build
```

Остановить сервисы:

```bash
docker compose down
```

Если нужно удалить данные БД (том Postgres):

```bash
docker compose down -v
```

---

### Как проверить работоспособность сервисов

#### Backend (Django)

- Откройте Swagger UI: `http://localhost:8000/api/docs/`
- Или проверьте схему: `http://localhost:8000/api/schema/`

Создать суперпользователя (опционально):

```bash
docker compose exec backend python manage.py createsuperuser
```

#### PostgreSQL

Проверить, что Postgres принимает подключения:

```bash
docker compose exec db pg_isready -U postgres
```

Зайти в psql (опционально):

```bash
docker compose exec db psql -U postgres -d hwdjango2
```

#### Redis

Проверить Redis:

```bash
docker compose exec redis redis-cli ping
```

Ожидаемый ответ: `PONG`

#### Celery worker

Проверить логи воркера:

```bash
docker compose logs -f celery
```

#### Celery Beat

Проверить логи планировщика:

```bash
docker compose logs -f celery_beat
```


# Custom Authentication & Authorization System (Test Task)

Backend-приложение на **Django + DRF**, реализующее собственную систему **аутентификации и авторизации** без использования встроенного Django `auth`.  
Проект демонстрирует работу с JWT-токенами, обработку ролей, правил доступа (RBAC) и выдачу ресурсов на основе разрешений.

## Стек технологий

- Python 3  
- Django  
- Django REST Framework  
- bcrypt — хеширование паролей  
- PyJWT — токены авторизации  
- PostgreSQL

## Основной функционал

### Пользователи

- **Регистрация:** `POST /api/auth/register/`
- **Логин (JWT):** `POST /api/auth/login/`
- **Логаут:** `POST /api/auth/logout/`  
- **Текущий пользователь:**  
  - `GET /api/me/` — информация о себе  
  - `PATCH /api/me/` — обновление профиля  
  - `DELETE /api/me/` — мягкое удаление (`is_active = False`)

Аутентификация в остальных ручках — через заголовок:

```http
Authorization: Bearer <access_token>
```
### Система разграничения прав (RBAC)

Используются таблицы:

#### Role — Роли пользователей: `admin`, `user`, …

#### BusinessElement — бизнес-объект (в примере: `task`)

#### AccessRule — права роли на элемент:

| Поле | Описание |
|------|----------|
| can_read | читать свои |
| can_read_all | читать все |
| can_create | создавать |
| can_update | обновлять свои |
| can_update_all | обновлять любые |
| can_delete | удалять свои |
| can_delete_all | удалять любые |

Поведение:

- Нет токена → **401 Unauthorized**  
- Есть токен, но нет разрешения → **403 Forbidden**  
- Есть нужные права → **200 OK**

### Mock-ресурсы

Приложение mockapp содержит модель:

#### Task: `title, description, owner, created_at, updated_at`

Эндпоинты: 

- `GET /api/tasks/ — список задач`

обычный пользователь видит только свои задачи; роль с `can_read_all` — видит все задачи.

- `POST /api/tasks/ — создать задачу (owner проставляется из токена)`

- `GET /api/tasks/{id}/`
- `PATCH /api/tasks/{id}/`

разрешения зависят от комбинации `can_*` и `can_*_all`

Права проверяются через кастомный класс DRF-разрешений `AccessRulePermission`.

## Admin API: управление правилами доступа

Доступно только для роли admin:

- `GET /api/access-rules/ — список всех правил`
- `POST /api/access-rules/ — создать правило`
- `GET /api/access-rules/{id}/ — получить правило`
- `PATCH /api/access-rules/{id}/ — изменить`
- `DELETE /api/access-rules/{id}/ — удалить`

Так администратор может динамически менять, кто и к каким ресурсам имеет доступ`
## Структура проекта
```markdown
em-auth-system/
├─ config/              # Django-проект
│  ├─ settings.py       # настройки проекта: БД, приложения, DRF, middleware
│  ├─ urls.py           # глобальная маршрутизация всего API (подключает users и mockapp)
│  └─ middleware.py     # JWTAuthenticationMiddleware (достаёт пользователя из токена)
│
├─ users/               # всё про пользователей и роли
│  ├─ models.py         # User, Role, BusinessElement, AccessRule
│  ├─ serializers.py    # регистрация, логин, профиль
│  ├─ views.py          
│  ├─ urls.py
│  ├─ services.py       # bcrypt + JWT (create/verify токенов)
│  └─ permissions.py    # AccessRulePermission, IsAdminRole
│
├─ mockapp/             # demo-приложение с задачами
│  ├─ models.py         # Task
│  ├─ serializers.py
│  ├─ views.py          # список/создание/детали задач
│  └─ urls.py
│
├─ requirements.txt
├─ README.md
└─ manage.py
```
## Схема БД
```
User
├─ id
├─ full_name
├─ email (unique)
├─ password_hash
├─ role_id → Role.id
├─ is_active (soft delete)
└─ timestamps

Role
├─ id
└─ name

BusinessElement
├─ id
├─ code
└─ name

AccessRule
├─ id
├─ role_id → Role
├─ element_id → BusinessElement
├─ can_read
├─ can_read_all
├─ can_create
├─ can_update
├─ can_update_all
├─ can_delete
└─ can_delete_all
```

## Запуск проекта

```bash
git clone <repo-url>
cd em-auth-system

# создать и активировать виртуальное окружение (по желанию)

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

```
Далее можно работать с API через Postman / HTTP-клиент,
создать роли и правила доступа и проверить, как меняется поведение `GET/POST /api/tasks/`
для разных пользователей и наборов прав.

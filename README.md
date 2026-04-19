# 🏚 Tavern Keeper

> *Смотритель откладывает перо. Взгляд медленно останавливается на вошедшем.*

Модульный Discord-бот для управления сервером в жанре таверны. Встречает гостей, управляет ролями, выносит предупреждения — всё от имени Смотрителя, в духе атмосферы.

---

## Возможности

| Модуль | Что делает |
|---|---|
| **Приветствие** | При входе нового участника — выдаёт роль и постит одну из 5 атмосферных фраз (без повторов подряд) |
| **Роли** | Выдача и снятие ролей через команды |
| **Модерация** | Предупреждения с атмосферными фразами, настраиваемый порог, кик |
| **Простынка** | Публикация текста правил от имени бота |
| **Статус** | Ротация статусов бота каждый час |
| **Голос** | Атмосферные фразы на голосовые события (вход, выход, AFK) |

---

## Стек

- **Python 3.10+** · discord.py 2.x · aiosqlite · python-dotenv
- **База данных:** SQLite (локально, `data/tavern.db`)
- **Типизация:** mypy strict

---

## Быстрый старт

```bash
git clone git@github.com:Cybiomez/tavern-keeper.git
cd tavern-keeper

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Заполни .env (токен, application_id, invite_url)

python main.py
```

---

## Конфигурация (.env)

```env
DISCORD_TOKEN=        # токен бота из Discord Developer Portal
APPLICATION_ID=       # ID приложения
INVITE_URL=           # ссылка-приглашение на сервер

# Только для разработки — мгновенная синхронизация команд
# DEV_GUILD_ID=
```

---

## Настройка сервера

После добавления бота на сервер — настрой через slash-команды:

```
/set default_role      Роль, выдаваемая новым участникам
/set warn_role         Роль при достижении порога предупреждений
/set warn_threshold    Количество предупреждений до выдачи роли (по умолчанию: 2)

/set greeting_channel  Канал с правилами (куда /post rules кладёт простынку)
/set guests_channel    Канал для фраз о новых гостях
/set public_channel    Канал для предупреждений, кика, голосовых событий
/set mod_channel       Канал для команд модерации
/set log_channel       Канал журнала действий бота

/config                Показать текущие настройки
```

---

## Команды

### Модерация
| Команда | Описание | Права |
|---|---|---|
| `/warn @участник причина` | Вынести предупреждение | manage_roles |
| `/unwarn @участник [заметка]` | Снять последнее предупреждение | manage_roles |
| `/warnings @участник` | История предупреждений | manage_roles |
| `/kick @участник причина` | Выгнать участника | kick_members |

### Роли
| Команда | Описание | Права |
|---|---|---|
| `/role give @участник @роль` | Выдать роль | manage_roles |
| `/role take @участник @роль` | Забрать роль | manage_roles |

### Администрирование
| Команда | Описание | Права |
|---|---|---|
| `/set ...` | Настройка каналов и ролей | manage_guild |
| `/post rules [#канал]` | Опубликовать правила | manage_guild |
| `/config` | Текущие настройки | manage_guild |

---

## Структура проекта

```
tavern-keeper/
├── main.py                   Точка входа
├── bot/
│   ├── core.py               Класс бота, загрузка модулей, send_log()
│   ├── config.py             Конфигурация из .env
│   ├── cogs/                 Независимые модули
│   │   ├── greetings.py      Приветствие новых участников
│   │   ├── roles.py          /role give / take
│   │   ├── moderation.py     /warn /unwarn /warnings /kick
│   │   ├── admin.py          /set /post /config
│   │   ├── presence.py       Статус бота (ротация)
│   │   └── voice.py          Голосовые события
│   ├── db/
│   │   ├── database.py       Инициализация SQLite + миграции
│   │   └── queries.py        Все запросы к БД
│   └── content/
│       ├── phrases.py        Фразы приветствия
│       └── texts.py          Текст правил (простынка)
└── data/                     База данных (gitignored)
```

---

## Добавить статусы

Открой [bot/cogs/presence.py](bot/cogs/presence.py) и добавь строку в список `STATUSES`:

```python
_StatusEntry("Новый текст", discord.ActivityType.watching),
```

Типы активности: `watching`, `listening`, `playing`, `streaming`.

---

## Запуск как фоновый процесс

```bash
screen -dmS tavern bash -c "PYTHONUNBUFFERED=1 .venv/bin/python main.py > /tmp/tavern.log 2>&1"

# Посмотреть логи
cat /tmp/tavern.log

# Подключиться к сессии
screen -r tavern

# Отключиться (бот продолжает работать)
Ctrl+A, затем D
```

---

## Права бота на сервере

При добавлении через OAuth2 боту нужны:
- Manage Roles
- Kick Members
- Send Messages
- View Channels
- Read Message History

Роль `Tavern Keeper` (создаётся автоматически) должна стоять **выше** всех ролей, которыми бот управляет.

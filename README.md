# Tavern Keeper

Discord-бот для управления сервером в жанре таверны. Приветствует гостей, управляет ролями, выносит предупреждения — всё от имени Смотрителя.

## Стек

- Python 3.11+, discord.py 2.x, aiosqlite, python-dotenv
- Типизация: mypy strict

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Заполни .env своими значениями
python main.py
```

## Структура

```
bot/
├── core.py          — класс бота, загрузка когов, синхронизация команд
├── config.py        — конфиг из .env
├── cogs/            — модули (каждый независим)
│   ├── greetings.py — on_member_join, атмосферные фразы, выдача роли
│   ├── roles.py     — /role give / take
│   ├── moderation.py— /warn /unwarn /warnings /kick
│   ├── admin.py     — /set /post /config
│   ├── presence.py  — статус бота (ротация каждый час)
│   └── voice.py     — атмосферные фразы на голосовые события
├── db/
│   ├── database.py  — инициализация SQLite
│   └── queries.py   — все запросы к БД
└── content/
    ├── phrases.py   — фразы приветствия (5 штук, без повторов подряд)
    └── texts.py     — простынка с плейсхолдером {invite_url}
```

## Настройка сервера

После добавления бота на сервер настрой его через слэш-команды:

```
/set default_role   — роль новичка (выдаётся автоматически при входе)
/set warn_role      — роль нарушителя (выдаётся при достижении порога)
/set warn_threshold — кол-во предупреждений до выдачи роли (по умолчанию 2)
/set public_channel — канал для атмосферных сообщений бота
/set greeting_channel — канал с правилами
/set mod_channel    — канал для команд модерации
/set log_channel    — канал для журнала действий

/post rules         — опубликовать простынку в текущем или указанном канале
/config             — показать текущие настройки
```

## Разработка

Для мгновенной синхронизации команд (без ожидания часа) добавь в `.env`:

```
DEV_GUILD_ID=твой_guild_id
```

Команды будут синхронизированы только с этим сервером. Убери перед деплоем на прод.

## Добавить статусы

Открой `bot/cogs/presence.py`, добавь строки в список `STATUSES`:

```python
_StatusEntry("Новый текст", discord.ActivityType.watching),
```

Типы: `watching`, `listening`, `playing`, `streaming`.

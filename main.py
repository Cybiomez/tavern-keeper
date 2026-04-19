import asyncio

from bot.config import load_config
from bot.core import TavernKeeper
from bot.db.database import init_db


async def main() -> None:
    config = load_config()
    await init_db()
    async with TavernKeeper(config) as bot:
        await bot.start(config.token)


if __name__ == "__main__":
    asyncio.run(main())

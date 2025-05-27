import asyncio
import asyncpg
import os
import sys

async def wait_for_db():
    # Получаем параметры из переменных окружения
    host = os.getenv("DB_HOST", "db")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASS", "postgres")
    database = os.getenv("DB_NAME", "cinetome")

    max_attempts = 30
    attempt = 1

    while attempt <= max_attempts:
        try:
            conn = await asyncpg.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database
            )
            await conn.close()
            print("Database is ready!")
            return
        except Exception as e:
            print(f"Attempt {attempt}/{max_attempts}: Waiting for database... ({str(e)})")
            await asyncio.sleep(1)
            attempt += 1

    print("Could not connect to the database after several attempts. Exiting.")
    sys.exit(1)

if __name__ == "__main__":
    asyncio.run(wait_for_db())
import asyncpg
from app.core.logger import log_info


class Database:
    def __init__(self, USER, PASSWORD, HOST, DB, PORT="5432"):
        self.user = USER
        self.password = PASSWORD
        self.host = HOST
        self.port = PORT
        self.database = DB
        self._cursor = None

        self._connection_pool = None

    async def connect(self):
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=20,
                    command_timeout=60,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    ssl="require",
                )
                log_info("Database pool connectionn opened")

            except Exception as e:
                log_info(e)

    async def fetch_rows(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()
            try:
                result = await con.fetch(query, *args)
                return result
            except Exception as e:
                log_info(e)
            finally:
                await self._connection_pool.release(con)

    async def close(self):
        if not self._connection_pool:
            try:
                await self._connection_pool.close()
                log_info("Database pool connection closed")
            except Exception as e:
                log_info(e)

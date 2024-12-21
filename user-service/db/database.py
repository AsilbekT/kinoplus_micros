class Database:
    def __init__(self, database_url):
        self.database_url = database_url
        self.pool = None

    async def connect(self):
        import asyncpg
        self.pool = await asyncpg.create_pool(self.database_url)

    async def close(self):
        await self.pool.close()

    async def create_user(self, username, email, phone_number, google_id, apple_id):
        query = """
        INSERT INTO users (username, email, phone_number, google_id, apple_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id;
        """
        return await self.pool.fetchval(query, username, email, phone_number, google_id, apple_id)

    async def get_user(self, user_id):
        query = """
        SELECT id, username, email, phone_number, google_id, apple_id
        FROM users
        WHERE id = $1;
        """
        return await self.pool.fetchrow(query, int(user_id))

    async def create_or_update_user(self, username, email, phone_number, google_id, apple_id):
        query = """
        INSERT INTO users (username, email, phone_number, google_id, apple_id)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (email) -- Replace with your unique column
        DO UPDATE SET
            username = EXCLUDED.username,
            phone_number = EXCLUDED.phone_number,
            google_id = EXCLUDED.google_id,
            apple_id = EXCLUDED.apple_id
        RETURNING id;
        """
        return await self.pool.fetchval(query, username, email, phone_number, google_id, apple_id)

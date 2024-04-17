from src.infrastructure.database.schemas import Professional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select
from aiohttp import ClientSession
import re


class ProfessionalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def has_professional(self, username: str) -> str:
        print("has_professional", username)
        get_one_stmt = (
            select(Professional).where(Professional.username == username).limit(1)
        )
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            return str(result[0])
        async with ClientSession() as client:
            async with client.get(f"https://calendly.com/{username}/30min") as resp:
                match = re.search(r'(?:"uuid":")([a-z\d-]*)"', await resp.text())
                if match:
                    aux_id: str = match.groups()[0]
                    insert_stmt = (
                        Professional.__table__.insert()
                        .returning(Professional.id, Professional.username)
                        .values({"username": username, "aux_id": aux_id})
                    )
                    result = (await self.session.execute(insert_stmt)).fetchone()
                    await self.session.commit()
                    if result:
                        return str(result[0])
        return False

    async def get_all(self):
        print("get_all")
        stmt = select(Professional).limit(10)
        stream = await self.session.stream_scalars(stmt.order_by(Professional.id))
        return [str(professional) async for professional in stream]

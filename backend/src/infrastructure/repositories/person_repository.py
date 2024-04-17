from typing import Dict, Any
from src.infrastructure.database.schemas import Person
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select, delete
from json import loads
from aiohttp import ClientSession
import re


class PersonRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_one(self, wpp_number: str):
        print("get_one: ", wpp_number)
        get_one_stmt = select(Person).where(Person.wpp_number == wpp_number).limit(1)
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            return str(result[0])

    async def update_email(self, wpp_number:str, email: str) -> str:
        print("Updating email:", wpp_number, email)
        get_one_stmt = select(Person).where(Person.wpp_number == wpp_number).limit(1)
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            update_stmt = Person.__table__.update().returning(
                Person.id, Person.email)\
                .where(Person.wpp_number == wpp_number)\
                .values({"email": email})
            await self.session.execute(update_stmt)
            await self.session.commit()

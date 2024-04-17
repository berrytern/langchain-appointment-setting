from src.infrastructure.database.schemas import Person, Message
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import update, select, delete

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_messages(self, wpp_number):
        get_one_stmt = select(Person).where(Person.wpp_number == wpp_number).limit(1)
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            get_one_stmt = select(Message).where(Message.person_id == result[0].id).limit(100)
            result = (await self.session.execute(get_one_stmt)).fetchall()
            return [message[0] for  message in  result]
        else:
            insert_stmt = Person.__table__.insert().returning(
                Person.id)\
                .values({"wpp_number": wpp_number})
            result = (await self.session.execute(insert_stmt)).fetchone()
            await self.session.commit()
            return []
    
    async def add_message(self, wpp_number, origin, content):
        get_one_stmt = select(Person).where(Person.wpp_number == wpp_number).limit(1)
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            insert_stmt = Message.__table__.insert()\
                .returning(
                    Message.id)\
                    .values({"person_id": result[0].id, "origin": origin, "content": content})
            result = (await self.session.execute(insert_stmt)).fetchone()
            await self.session.commit()
        
from typing import Dict, Any
from src.infrastructure.database.schemas import Professional
from src.application.domain.models import ProfessionalModel, ProfessionalList
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select, delete
from json import loads


class ProfessionalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: Dict[str, Any], commit = True):
        insert_stmt = Professional.__table__.insert().returning(
            Professional.id, Professional.name, Professional.email, Professional.created_at, Professional.updated_at)\
            .values(**data)
        result = (await self.session.execute(insert_stmt)).fetchone()
        if result:
            result = loads(ProfessionalModel(id=result[0], name=result[1], email=result[2], created_at=result[3], updated_at=result[4])
                           .model_dump_json())
            commit and await self.session.commit()
        return result

    async def get_one(self, id):
        get_one_stmt = select(Professional).where(Professional.id == id).limit(1)
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            result = result[0]
            result = loads(ProfessionalModel(id=result.id, name=result.name, email=result.email, created_at=result.created_at, updated_at=result.updated_at)
                           .model_dump_json())
        return result

    async def get_all(self, filters={}):
        stmt = select(Professional).filter_by(**filters["query"]).limit(filters["limit"])
        stream = await self.session.stream_scalars(stmt.order_by(Professional.id))
        return loads(ProfessionalList(root=[aluno async for aluno in stream]).model_dump_json())

    async def update_one(self, id, data):
        update_stmt = Professional.__table__.update().returning(
            Professional.id, Professional.name, Professional.email, Professional.created_at, Professional.updated_at)\
            .where(Professional.id == id)\
            .values(**data)
        result = (await self.session.execute(update_stmt)).fetchone()
        if result:
            result = loads(ProfessionalModel(id=result[0], name=result[1], email=result[2], created_at=result[3], updated_at=result[4])
                           .model_dump_json())
            await self.session.commit()
        return result

    async def delete_one(self, id):
        await self.session.execute(delete(Professional).where(Professional.id == id))
        await self.session.commit()

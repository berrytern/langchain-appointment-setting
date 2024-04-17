from typing import List, Dict, Union
from src.infrastructure.database.schemas import Appointment, Professional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select
from aiohttp import ClientSession
from datetime import datetime


class AppointmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_available(self, professional_id: str, start_time: str):
        get_one_stmt = (
            select(Appointment)
            .where(
                Appointment.start_time == start_time,
                Appointment.professional_id == professional_id,
            )
            .limit(1)
        )
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            return result[0].available
        else:
            insert_stmt = (
                Appointment.__table__.insert()
                .returning(Appointment.available)
                .values(
                    {
                        "professional_id": professional_id,
                        "start_time": datetime.strptime(
                            start_time, "%y-%m-%d %H:%M:%S"
                        ),
                    }
                )
            )
            result = (await self.session.execute(insert_stmt)).fetchone()
            print("save result:", result)
            await self.session.commit()
            return True

    async def feed_day(
        self, schedules: List[Dict[str, Union[str, int]]], professional_id: str
    ):
        for schedule in schedules:
            get_one_stmt = (
                select(Appointment)
                .where(
                    Appointment.start_time == schedule["start_time"],
                    Appointment.professional_id == professional_id,
                )
                .limit(1)
            )
            result = (await self.session.execute(get_one_stmt)).fetchone()
            if not result:
                insert_stmt = (
                    Appointment.__table__.insert()
                    .returning(Appointment.available)
                    .values(
                        {
                            "professional_id": professional_id,
                            "start_time": datetime.strptime(
                                schedule["start_time"], "%y-%m-%d %H:%M:%S"
                            ),
                        }
                    )
                )
                result = (await self.session.execute(insert_stmt)).fetchone()
            elif result[0].available != (schedule["status"] == "available"):
                update_stmt = (
                    Appointment.__table__.update()
                    .where(Appointment.id == result[0].id)
                    .values({"available": schedule["status"] == "available"})
                )
                await self.session.execute(update_stmt)

        await self.session.commit()

    async def get_available_appointments(self, professional_id: str, date: str):
        print("get_available_appointments", professional_id, date)

        get_one_stmt = (
            select(Professional).where(Professional.id == professional_id).limit(1)
        )
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            aux_id = result[0].aux_id
            async with ClientSession() as client:
                async with client.get(
                    f"https://calendly.com/api/booking/event_types/{aux_id}/"
                    + f"calendar/range?timezone=America/Sao_Paulo&diagnostics=false&range_start={date}&range_end={date}"
                ) as resp:
                    days = await resp.json()["days"]
                    self.feed_days(days)
        return []

        """"""

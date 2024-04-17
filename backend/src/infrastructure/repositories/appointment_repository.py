from src.infrastructure.database.schemas import Person, Appointment, Professional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from sqlalchemy import select
from datetime import datetime

class AppointmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_available(self, professional_id: str, start_time: str):
        get_one_stmt = select(Appointment).where(Appointment.start_time == start_time, Appointment.professional_id == professional_id).limit(1)
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            return result[0].available
        else:
            insert_stmt = Appointment.__table__.insert().returning(
                Appointment.available)\
                .values({"professional_id": professional_id, "start_time": datetime.strptime(start_time, '%y-%m-%d %H:%M:%S')})
            result = (await self.session.execute(insert_stmt)).fetchone()
            print("save result:", result)
            await self.session.commit()
            return True
    
    async def get_available_appointments(self, professional_id: str, date: str):
        print("get_available_appointments", professional_id, date)
        '''get_one_stmt = select(Appointment).where(Appointment.start_time == start_time, Appointment.professional_id == professional_id).limit(1)
        result = (await self.session.execute(get_one_stmt)).fetchone()
        if result:
            return result[0].available
        else:
            insert_stmt = Appointment.__table__.insert().returning(
                Appointment.available)\
                .values({"professional_id": professional_id, "start_time": datetime.strptime(start_time, '%y-%m-%d %H:%M:%S')})
            result = (await self.session.execute(insert_stmt)).fetchone()
            print("save result:", result)
            await self.session.commit()
            return True'''
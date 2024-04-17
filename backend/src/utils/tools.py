from langchain.tools import BaseTool
from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories import PersonRepository, ProfessionalRepository, AppointmentRepository
import re
from asyncio import get_running_loop, Future


class EmailValidator(BaseTool):
    name = "Email_validator"
    description = "Use this tool when you need to check if email is valid"

    def _run(self, email: str) -> bool:
        return bool(re.search(r"[a-zA-Z\d.]{2,20}@(gmail|hotmail|yahoo|outlook|mail).(com|net)", email))

    async def _arun(self, email: str):
        ft = Future(loop=get_running_loop())
        ft.set_result(bool(re.search(r"[a-zA-Z\d.]{2,20}@(gmail|hotmail|yahoo|outlook|mail).(com|net)", email)))
        return await ft


class GetOnePerson(BaseTool):
    name = "get_one_person"
    description = "Use this tool when you need to get person to retrieve person_id"

    def _run(self, wpp_number: str) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, wpp_number: str):
        async with get_db() as session:
            return await PersonRepository(session).get_one(wpp_number)

class UpdatePersonEmail(BaseTool):
    name = "update_person_email"
    description = "Use this tool when you need to update email of user/person"

    def _run(self, wpp_number: str, email: str) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, wpp_number: str, email: str):
        async with get_db() as session:
            return await PersonRepository(session).update_email(wpp_number, email)


class HasProfessional(BaseTool):
    name = "has_professional"
    description = "Use this tool when you need verify if some professional exists or retrieve professional_id"

    def _run(self, username: str) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, username: str):
        async with get_db() as session:
            return await ProfessionalRepository(session).has_professional(username)


class GetAllProfessional(BaseTool):
    name = "get_all_professionals"
    description = "Use this tool when you need to list all professionals"

    def _run(self) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self):
        async with get_db() as session:
            return await ProfessionalRepository(session).get_all()

class GetAvailableAppointments(BaseTool):
    name = "get_available_appointments"
    description = "Use this tool when you need to get all available appointments of professional_id on the given date"

    def _run(self, professional_id: str, date: str) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, professional_id: str, date: str):
        async with get_db() as session:
            return await AppointmentRepository(session).get_available_appointments(professional_id, date)
    
class IsAvailableAppointment(BaseTool):
    name = "is_appointment_available"
    description = "Use this tool when you need to verify if appointment is available for professional_id on the given datetime"

    def _run(self, professional_id: str, start_time: str) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, professional_id: str, start_time: str):
        async with get_db() as session:
            return await AppointmentRepository(session).is_available(professional_id, start_time)

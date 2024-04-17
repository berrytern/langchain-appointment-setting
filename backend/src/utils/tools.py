from typing import Type
from langchain.tools import BaseTool, StructuredTool
from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories import (
    PersonRepository,
    ProfessionalRepository,
    AppointmentRepository,
)
from asyncio import get_running_loop, Future
from pydantic.v1 import BaseModel, Field, StrictStr
import re


class EmailValidator(BaseTool):
    name = "Email_validator"
    description = "Use this tool when you need to check if email is valid"

    def _run(self, email: str) -> bool:
        return bool(
            re.search(
                r"[a-zA-Z\d.]{2,20}@(gmail|hotmail|yahoo|outlook|mail)" + r".(com|net)",
                email,
            )
        )

    async def _arun(self, email: str):
        ft = Future(loop=get_running_loop())
        ft.set_result(
            bool(
                re.search(
                    r"[a-zA-Z\d.]{2,20}@(gmail|hotmail|yahoo|outlook|mail)"
                    + r".(com|net)",
                    email,
                )
            )
        )
        return await ft


class GetOnePerson(BaseTool):
    name = "get_one_person"
    description = "Use this tool only when you need to retrieve person_id"

    def _run(self, wpp_number: str) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, wpp_number: str):
        """receives wpp_number as argument and return json of person"""
        async with get_db() as session:
            return await PersonRepository(session).get_one(wpp_number)


class UpdatePersonEmail(BaseTool):
    name = "update_person_email"
    description = "Use this tool when you need to update email of user/person"

    def _run(self, wpp_number: str, email: str) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, wpp_number: str, email: str):
        """receives wpp_number: str and email: str as arguments and return None"""
        async with get_db() as session:
            return await PersonRepository(session).update_email(wpp_number, email)


class HasProfessionalModel(BaseModel):
    username: StrictStr = Field(description="username of professional")


class HasProfessional(BaseTool):
    name = "has_professional"
    description = "Use this tool when you need verify if some professional exists or retrieve professional_id"

    def _run(self, username: str) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, username: str):
        """receives username as argument and return json of person or None"""
        async with get_db() as session:
            return await ProfessionalRepository(session).has_professional(username)


class GetAllProfessional(BaseTool):
    name = "get_all_professionals"
    description = "Use this tool when you need to list all professionals"

    def _run(self) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self):
        """receives no arguments and returns list[str]"""
        async with get_db() as session:
            return await ProfessionalRepository(session).get_all()


class GetAvailableAppointmentModel(BaseModel):
    professional_id: StrictStr = Field(description="id of professional")
    date: StrictStr = Field(description="appointment date on format '%Y-%m-%d'")


class GetAvailableAppointments(BaseTool):
    name = "get_available_appointments"
    description = "Use this tool when you need to get all available appointments of professional_id on the given date"
    args_schema: Type[BaseModel] = GetAvailableAppointmentModel

    def _run(self, professional_id: str, date: str) -> bool:
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, professional_id: str, date: str):
        """receives (professional_id: str and date: str) as arguments and returns list[str]"""
        async with get_db() as session:
            return await AppointmentRepository(session).get_available_appointments(
                professional_id, date
            )


class IsAvailable(BaseModel):
    professional_id: StrictStr = Field(description="id of professional")
    appointment_datetime: StrictStr = Field(
        description="appointment datetime on format '%Y-%m-%d %h:%M:%S'"
    )


async def is_appointment_available(professional_id: str, appointment_datetime: str):
    """Use professional_id: str and appointment_datetime: str as args and returns bool"""
    async with get_db() as session:
        return await AppointmentRepository(session).is_available(
            professional_id, appointment_datetime
        )


is_appointment_available_tool = StructuredTool.from_function(
    name="is_appointment_available",
    description="verify if time is available for appointment of professional_id",
    args_schema=IsAvailable,
    return_direct=True,
    coroutine=is_appointment_available,
)


class IsAvailableAppointment(BaseTool):
    name = "is_appointment_available"
    description = (
        "Use this tool when you need to verify if appointment is available "
        + "for professional_id on the given datetime"
    )
    args_schema: Type[BaseModel] = IsAvailable

    def _run(self, professional_id: str, appointment_date: str) -> bool:
        """Use the tool."""
        raise NotImplementedError("Not implemented sync function")

    async def _arun(self, professional_id: str, appointment_date: str):
        """Use the tool asynchronously."""
        async with get_db() as session:
            return await AppointmentRepository(session).is_available(
                professional_id, appointment_date
            )

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
class Base(AsyncAttrs, DeclarativeBase):
    pass
from .message import Message
from .person import Person
from .professional import Professional
from .appointment import Appointment

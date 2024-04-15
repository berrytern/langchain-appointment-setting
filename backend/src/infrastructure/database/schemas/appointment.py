import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from . import Base


class Appointment(Base):
    __tablename__ = "appointment"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    professional_id = Column(UUID(as_uuid=True), ForeignKey("professional.id"))
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.id"))
    start_time = Column(DateTime(timezone=True))
    available = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return '{"id":"' + str(self.id) + '", "professional_id": "'+str(self.professional_id)+'", '\
            + '", "start_time": "'+str(self.start_time)+'", '+'", "available": "'+self.available+'}'

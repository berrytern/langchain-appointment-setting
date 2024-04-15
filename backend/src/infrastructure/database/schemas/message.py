import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from . import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    person_id = Column(UUID(as_uuid=True), ForeignKey("person.id"))
    content = Column(String)
    origin = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return '{"id":"'+ str(self.id) + '", "person_id": "'+str(self.person_id)+'", '\
            +'", "content": "'+self.content+'", '+'", "origin": "'+self.origin+'}'

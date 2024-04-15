import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from . import Base


class Professional(Base):
    __tablename__ = "professional"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    username = Column(String(60))

    def __repr__(self) -> str:
        return '{"id": "' + str(self.id) + '", "username": "' + self.username+'"}'

import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from . import Base


class Person(Base):
    __tablename__ = "person"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    wpp_number = Column(String(30), unique=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return '{"id": "' + str(self.id) + '", "wpp_number": "' + str(self.wpp_number) \
            +'", "email": "' + str(self.email) + '", "created_at": "' \
            + str(self.created_at) +'", "updated_at": "' + str(self.updated_at)+ '"}'


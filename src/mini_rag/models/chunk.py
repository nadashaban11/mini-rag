import uuid

from sqlalchemy import ForeignKey, Text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
from datetime import datetime

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    resource_uuid: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"), index=True
    )
    chunk_order: Mapped[int] = mapped_column()
    chunk_text: Mapped[str] = mapped_column(Text())
    chunk_metadata: Mapped[dict] = mapped_column(JSONB())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    
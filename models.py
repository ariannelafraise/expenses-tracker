from datetime import date
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    Enum as SAEnum,
    Numeric,
    String,
    Table,
    Column,
    ForeignKey,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class TransactionDirection(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


transaction_tags = Table(
    "transaction_tags",
    Base.metadata,
    Column(
        "transaction_id",
        ForeignKey(
            "transactions.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey(
            "tags.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    card_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    account_name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    direction: Mapped[TransactionDirection] = mapped_column(
        SAEnum(TransactionDirection),
        nullable=False,
    )
    cashback_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4),
        nullable=True,
    )
    cashback_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary=transaction_tags,
        back_populates="transactions",
        passive_deletes=True,
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    transactions: Mapped[list[Transaction]] = relationship(
        secondary=transaction_tags,
        back_populates="tags",
    )


class BlacklistKeyword(Base):
    __tablename__ = "blacklist_keywords"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    keyword: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
    )
    strict: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

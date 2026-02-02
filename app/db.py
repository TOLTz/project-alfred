import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, String, Float, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

load_dotenv()

DB_URL = os.getenv("DB_URL", "sqlite:///./alfred.db")

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)  # pending | delivered
    job_id: Mapped[str] = mapped_column(String, nullable=False)
    order_json: Mapped[str] = mapped_column(Text, nullable=False)


class MenuItem(Base):
    __tablename__ = "menu_items"

    item_id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    aliases_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list[str]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

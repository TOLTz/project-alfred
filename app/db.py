from sqlalchemy import create_engine, String, Float, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DB_URL = "sqlite:///./alfred.db"

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},  # necessário no SQLite com threads
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


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

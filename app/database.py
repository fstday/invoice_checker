from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Session
from datetime import datetime


# Создаем движок - подключение к SQLite файлу
engine = create_engine("sqlite:///invoices.db")


class Base(DeclarativeBase):
    pass


class InvoiceCheck(Base):
    __tablename__ = "invoice_checks"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    file_name       = Column(String)
    expected_number = Column(String)
    expected_date   = Column(String)
    found_number    = Column(String, nullable=True)
    found_date      = Column(String, nullable=True)
    number_match    = Column(Boolean)
    date_match      = Column(Boolean)
    status          = Column(String)
    created_at      = Column(DateTime, default=datetime.utcnow)


# Создаем таблицу, если ее нет
Base.metadata.create_all(engine)


def save_result(result: dict):
    """Сохраняет результат проверки в БД"""
    with Session(engine) as session:
        record = InvoiceCheck(**{k: v for k, v in result.items() if k != "error"})
        session.add(record)
        session.commit()

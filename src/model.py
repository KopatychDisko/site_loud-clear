from typing import List, Optional
from uuid import UUID

from sqlalchemy import BigInteger, String, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from config import POSTGRESQL_DBNAME, POSTGRESQL_HOST, POSTGRESQL_PASSWORD, POSTGRESQL_PORT, POSTGRESQL_USER

from pydantic import BaseModel, ConfigDict
from datetime import datetime

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRESQL_USER}:{POSTGRESQL_PASSWORD}"
    f"@{POSTGRESQL_HOST}:{POSTGRESQL_PORT}/{POSTGRESQL_DBNAME}"
)

engine = create_async_engine(url=DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    telegram_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(30))
    role: Mapped[str] = mapped_column(default='customer', nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    birth_day: Mapped[DateTime] = mapped_column(DateTime)
    
    orders_created: Mapped[List['Orders']] = relationship(
        back_populates="customer",
        foreign_keys="[Orders.customer_id]"
    )

    orders_accepted: Mapped[List['Orders']] = relationship(
        back_populates="accepted_executor",
        foreign_keys="[Orders.accepted_executor_id]"
    )
    
    offers_sent: Mapped[List['Offers']] = relationship(back_populates='executor', cascade="all, delete-orphan")
    
    executor_profile: Mapped['Executors'] = relationship('Executors', back_populates='user', uselist=False)
    
    
class Orders(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    urgency: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(default='pending', nullable=False)
    group_message_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False, unique=True)
    accepted_price: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    
    accepted_executor_id: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=True)
    customer_id: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    
    customer: Mapped['Users'] = relationship(
        back_populates="orders_created",
        foreign_keys=[customer_id]
    )
    
    accepted_executor: Mapped['Users'] = relationship(
        back_populates="orders_accepted",
        foreign_keys=[accepted_executor_id]
    )
    
    offers: Mapped[List['Offers']] = relationship(back_populates='order', cascade="all, delete-orphan")
    
class Offers(Base):
    __tablename__ = 'offers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    price: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    status: Mapped[str] = mapped_column(String, default='sent')
    customer_message_id: Mapped[BigInteger] = mapped_column(BigInteger, nullable=False)
    
    executor_id: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey('users.telegram_id', ondelete='CASCADE'), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    
    executor: Mapped['Users'] = relationship(back_populates='offers_sent')
    order: Mapped['Orders'] = relationship(back_populates='offers')
    
class Executors(Base):
    __tablename__ = 'executors'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=func.gen_random_uuid())
    
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(nullable=False, default=0)
    description: Mapped[str] = mapped_column(String(2000), nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    price: Mapped[int] = mapped_column(nullable=True)
    experience: Mapped[int] = mapped_column(nullable=True)
    completed_orders: Mapped[int] = mapped_column(nullable=True, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    works: Mapped[String] = mapped_column(String(100))
    
    user: Mapped['Users'] = relationship('Users',back_populates='executor_profile')
    reviews: Mapped[list['Feedback']] = relationship('Feedback', back_populates='executor', cascade="all, delete-orphan")
    
    
class Feedback(Base):
    __tablename__ = 'feedback'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    star: Mapped[int] = mapped_column()
    text: Mapped[str] = mapped_column(String(300))
    
    executor_id: Mapped[UUID] = mapped_column(ForeignKey('executors.id'), nullable=False)
    customer_id: Mapped[BigInteger] = mapped_column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'))
    
    executor: Mapped['Executors'] = relationship('Executors', back_populates='reviews')
    
    
class ExecutorOut(BaseModel):
    id: UUID
    name: str
    age: int
    rating: float
    description: Optional[str]
    image_url: Optional[str]
    price: Optional[int]
    experience: Optional[int]
    completed_orders: Optional[int]
    created_at: Optional[datetime]
    works: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class ExecutorsListOut(BaseModel):
    executors: List[ExecutorOut]

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def shutdown_db():
    await engine.dispose()
    
async def get_session():
    async with async_session() as session:
        yield session
"""
Модель пользователя для таблицы public.users
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from api.database import Base

class User(Base):
    __tablename__ = "users"
    
    id_user = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # 👈 Твоё название поля
    nickname = Column(String(100), unique=True, index=True)  # 👈 nickname вместо username
    phone = Column(String(20), nullable=True)
    id_role = Column(Integer, ForeignKey("roles.id_role"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь с таблицей ролей
    role = relationship("Role", back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id_user}, email='{self.email}')>"


class Role(Base):
    __tablename__ = "roles"
    
    id_role = Column(Integer, primary_key=True, index=True)
    name_role = Column(String(50), nullable=False)
    
    # Связь с пользователями
    users = relationship("User", back_populates="role")
    
    def __repr__(self):
        return f"<Role(id={self.id_role}, name='{self.name_role}')>"
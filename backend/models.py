"""
SQLAlchemy ORM models — User, Device, Relay
"""
from sqlalchemy import Column, String, Boolean, Integer, BigInteger, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)        # UUID
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    device_id = Column(String, ForeignKey("devices.device_id"), nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(BigInteger, default=0)

    device = relationship("Device", back_populates="users", foreign_keys=[device_id])


class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True)   # e.g. SH-001
    owner_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    num_switches = Column(Integer, default=4)
    online = Column(Boolean, default=False)
    last_seen = Column(BigInteger, default=0)
    ip_address = Column(String, default="")
    created_at = Column(BigInteger, default=0)

    users = relationship("User", back_populates="device", foreign_keys=[User.device_id])
    relays = relationship("Relay", back_populates="device", cascade="all, delete-orphan")


class Relay(Base):
    __tablename__ = "relays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.device_id"), nullable=False)
    relay_key = Column(String, nullable=False)    # e.g. relay1
    name = Column(String, default="Switch")       # e.g. Living Room
    state = Column(Boolean, default=False)

    device = relationship("Device", back_populates="relays")

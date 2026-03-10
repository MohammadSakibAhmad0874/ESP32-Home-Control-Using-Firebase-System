"""
SQLAlchemy ORM models — User, Device, Relay, Schedule, PowerLog, PreRegisteredDevice
"""
from sqlalchemy import Column, String, Boolean, Integer, BigInteger, Float, ForeignKey, Text
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


class PreRegisteredDevice(Base):
    """
    Admin-seeded device IDs. Users claim these from the web dashboard.
    Once claimed, a full Device + User record is created.
    """
    __tablename__ = "pre_registered_devices"

    device_id    = Column(String, primary_key=True)   # e.g. SAKIB7860
    label        = Column(String, default="")          # Optional friendly name
    num_switches = Column(Integer, default=4)           # Number of relay switches
    is_claimed   = Column(Boolean, default=False)       # True once a user registers
    created_at   = Column(BigInteger, default=0)


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
    schedules = relationship("Schedule", back_populates="device", cascade="all, delete-orphan")
    power_logs = relationship("PowerLog", back_populates="device", cascade="all, delete-orphan")


class Relay(Base):
    __tablename__ = "relays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.device_id"), nullable=False)
    relay_key = Column(String, nullable=False)    # e.g. relay1
    name = Column(String, default="Switch")       # e.g. Living Room
    state = Column(Boolean, default=False)
    wattage = Column(Float, default=60.0)         # Watts — used for power estimation

    device = relationship("Device", back_populates="relays")


class Schedule(Base):
    """
    A timed automation rule: fire relay ON or OFF at a specific time on selected days.
    days is a comma-separated string of day abbreviations: "Mon,Tue,Wed,Thu,Fri,Sat,Sun"
    """
    __tablename__ = "schedules"

    id = Column(String, primary_key=True)         # UUID
    device_id = Column(String, ForeignKey("devices.device_id"), nullable=False)
    relay_key = Column(String, nullable=False)    # e.g. relay1
    action = Column(String, nullable=False)       # "on" or "off"
    time = Column(String, nullable=False)         # "HH:MM" in 24h format (local time of server)
    days = Column(String, nullable=False)         # "Mon,Wed,Fri" or "all"
    enabled = Column(Boolean, default=True)
    label = Column(String, default="")           # Optional user label
    created_at = Column(BigInteger, default=0)

    device = relationship("Device", back_populates="schedules")


class PowerLog(Base):
    """
    Records every relay state change with a timestamp.
    Used to calculate how long each relay was ON and estimate energy usage.
    """
    __tablename__ = "power_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.device_id"), nullable=False)
    relay_key = Column(String, nullable=False)   # e.g. relay1
    state = Column(Boolean, nullable=False)      # True = turned ON, False = turned OFF
    timestamp = Column(BigInteger, nullable=False)  # Unix seconds

    device = relationship("Device", back_populates="power_logs")

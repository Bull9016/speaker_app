from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "speaker_app.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String)  # speaker, event_manager, admin
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    speakers = relationship("Speaker", back_populates="user")

class Speaker(Base):
    __tablename__ = "speakers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, nullable=False)
    mobile = Column(String)
    # Additional speaker fields requested during registration
    speaker2_name = Column(String, nullable=True)
    speaker2_email = Column(String, nullable=True)
    speaker2_tshirt = Column(String, nullable=True)
    user = relationship("User", back_populates="speakers")
    track = Column(String)
    session_category = Column(String)
    tshirt_size = Column(String)
    food_choice = Column(String)
    blood_group = Column(String)
    emergency_contact_name = Column(String)
    emergency_contact_number = Column(String)
    linkedin_url = Column(String)
    sap_community_url = Column(String)
    is_verified = Column(Boolean, default=False)
    availability = Column(JSON)  # Store availability as JSON
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    sessions = relationship("Session", back_populates="speaker")
    documents = relationship("Document", back_populates="speaker")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    speaker_id = Column(Integer, ForeignKey('speakers.id'))
    title = Column(String, nullable=False)
    abstract = Column(Text)
    category = Column(String)
    track = Column(String)
    co_speaker_email = Column(String)
    co_speaker_tshirt = Column(String)
    status = Column(String, default="pending")  # pending, approved, rejected, hold
    timeslot = Column(String)
    location = Column(String)
    presentation_url = Column(String)
    feedback_score = Column(Integer)
    feedback_comments = Column(Text)
    speaker_confirmed = Column(Boolean, default=False)
    co_speaker_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_modified = Column(DateTime, onupdate=datetime.datetime.utcnow)
    change_requests = relationship("ChangeRequest", back_populates="session")
    speaker = relationship("Speaker", back_populates="sessions")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    speaker_id = Column(Integer, ForeignKey('speakers.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=True)
    doc_type = Column(String)  # presentation, template, promotional
    file_url = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="pending")  # pending, approved, rejected
    speaker = relationship("Speaker", back_populates="documents")

class ChangeRequest(Base):
    __tablename__ = "change_requests"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    request_type = Column(String)  # title, abstract, speaker
    old_value = Column(Text)
    new_value = Column(Text)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    session = relationship("Session", back_populates="change_requests")

class QRCode(Base):
    __tablename__ = "qrcodes"
    id = Column(Integer, primary_key=True, index=True)
    speaker_id = Column(Integer, ForeignKey('speakers.id'))
    code = Column(String, unique=True)
    purpose = Column(String)  # checkin, tshirt, certificate
    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AgendaItem(Base):
    __tablename__ = "agenda_items"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=True)
    title = Column(String)
    start_time = Column(String)
    duration = Column(String)
    location = Column(String)
    item_type = Column(String)  # keynote, break, session, snack
    order = Column(Integer, default=0)

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    rating = Column(Integer)
    comments = Column(Text)
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String)
    action = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    message = Column(String)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
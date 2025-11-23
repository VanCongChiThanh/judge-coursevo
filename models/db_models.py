from sqlalchemy import Column, String, Text, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from controllers.database import Base


class User(Base):
    __tablename__ = "users"
    # Chỉ cần định nghĩa khóa chính để SQLAlchemy biết bảng này tồn tại
    id = Column(UUID(as_uuid=True), primary_key=True)


class CodeExercise(Base):
    __tablename__ = "code_exercises"
    # Chỉ cần định nghĩa khóa chính để SQLAlchemy biết bảng này tồn tại
    code_exercise_id = Column(UUID(as_uuid=True), primary_key=True)

class OAuthAccessToken(Base):
    __tablename__ = "oauth_access_tokens"
    # Chỉ cần định nghĩa các cột cần thiết để truy vấn
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)



class CodeSubmission(Base):
    __tablename__ = "code_submissions"

    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    exercise_id = Column(
        UUID(as_uuid=True),
        ForeignKey("code_exercises.code_exercise_id"),
        nullable=False,
    )
    source_code = Column(Text, nullable=False)
    language_id = Column(Integer, nullable=False)
    status = Column(String(255), nullable=False)
    execution_time = Column(Float, nullable=True)
    memory_usage = Column(Integer, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    gemini_feedback = Column(JSON, nullable=True)
    points_achieved = Column(Integer, default=0)
    submitted_at = Column(DateTime, nullable=False, server_default=func.now())

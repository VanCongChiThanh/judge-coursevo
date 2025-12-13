from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import json

from utils.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def upsert_course_vector(course_id: str, embedding: list[float]):
    db = SessionLocal()
    sql = text("""
        INSERT INTO course_vector (course_id, embedding, updated_at)
        VALUES (:course_id, CAST(:embedding AS jsonb), NOW())
        ON CONFLICT (course_id)
        DO UPDATE SET embedding = CAST(:embedding AS jsonb), updated_at = NOW();
    """)
    db.execute(sql, {
        "course_id": course_id,
        "embedding": json.dumps(embedding)
    })
    db.commit()
    db.close()
    
def get_all_course_vectors():
    db = SessionLocal()
    sql = text("""
        SELECT course_id, embedding FROM course_vector;
    """)
    result = db.execute(sql).fetchall()
    db.close()
    if result:
        return [{"course_id": row[0], "embedding": row[1]} for row in result]
    return []
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# 1. Coge la URL de la base de datos de Render (del "Environment")
DATABASE_URL = os.environ.get("DATABASE_URL")

# 2. Si no la encuentra (ej. en tu PC), usa un archivo local (opcional)
# PERO para Render, SIEMPRE usará la URL de arriba.
if DATABASE_URL is None:
    DATABASE_URL = "sqlite:///./timetracker.db" # Tu base de datos antigua

# 3. Le decimos que use PostgreSQL (si la URL existe) o SQLite si no.
if DATABASE_URL.startswith("postgres://"):
    # Arreglo para Heroku/Render que usa 'postgres://' pero SQLAlchemy prefiere 'postgresql://'
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- TUS MODELOS (Los he movido de models.py aquí por simplicidad) ---
# (Si tus modelos están en models.py, asegúrate de que importas Base)
# *ACTUALIZACIÓN*: Tu main.py los importa de database.py, así que TIENEN que estar aquí.

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Relación (para que 'f.user.username' funcione)
    fichajes = relationship("Fichaje", back_populates="user")

class Fichaje(Base):
    __tablename__ = "fichajes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hora_entrada = Column(DateTime)
    hora_salida = Column(DateTime, nullable=True)

    # Relación (para que 'f.user.username' funcione)
    user = relationship("User", back_populates="fichajes")


# --- FUNCIÓN PARA DAR LA BASE DE DATOS ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


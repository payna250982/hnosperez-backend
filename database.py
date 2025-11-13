import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# 1. Coge la URL de la base de datos de Render (del "Environment")
DATABASE_URL = os.environ.get("DATABASE_URL")

connect_args = {} # Empezamos sin argumentos extra

# 2. Comprobamos si estamos usando SQLite (ej. en local)
if DATABASE_URL.startswith("sqlite"):
    # Si es SQLite, AÑADIMOS el argumento que daba el error
    connect_args = {"check_same_thread": False}

# 3. Comprobamos si hay que arreglar la URL de postgres (un truco de Render)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 4. Creamos el "motor" y le pasamos los argumentos (que estarán vacíos si es Postgres)
engine = create_engine(DATABASE_URL, connect_args=connect_args)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- TUS MODELOS (Los has importado desde aquí en main.py) ---

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

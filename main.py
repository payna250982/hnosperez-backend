from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, User, Fichaje  # Asumo que estos se importan desde database.py
from passlib.context import CryptContext
from datetime import datetime

# --- 1. LOS MOLDES (SCHEMAS) ---
# Esto le dice a FastAPI qué "paquetes" (Body) esperar
class UserCreate(BaseModel):
    username: str
    password: str

class FichajeData(BaseModel):
    username: str

# --- FIN DE LOS MOLDES ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API HnosPerez funcionando correctamente"}

# --- REGISTRO CORREGIDO ---
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)): # <-- 1. CAMBIO AQUÍ
    if db.query(User).filter(User.username == user.username).first(): # <-- 2. CAMBIO AQUÍ
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    hashed_password = pwd_context.hash(user.password) # <-- 3. CAMBIO AQUÍ
    
    db_user = User(username=user.username, hashed_password=hashed_password) # <-- 4. CAMBIO AQUÍ
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": f"Usuario {db_user.username} creado correctamente"} # <-- 5. CAMBIO AQUÍ

# --- FICHAR ENTRADA CORREGIDO ---
@app.post("/fichar_entrada")
def fichar_entrada(data: FichajeData, db: Session = Depends(get_db)): # <-- 1. CAMBIO AQUÍ
    user = db.query(User).filter(User.username == data.username).first() # <-- 2. CAMBIO AQUÍ
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    fichaje = Fichaje(user_id=user.id, hora_entrada=datetime.utcnow())
    db.add(fichaje)
    db.commit()
    db.refresh(fichaje)
    return {"message": f"Entrada registrada para {user.username} a las {fichaje.hora_entrada}"}

# --- FICHAR SALIDA CORREGIDO ---
@app.post("/fichar_salida")
def fichar_salida(data: FichajeData, db: Session = Depends(get_db)): # <-- 1. CAMBIO AQUÍ
    user = db.query(User).filter(User.username == data.username).first() # <-- 2. CAMBIO AQUÍ
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    fichaje = (
        db.query(Fichaje)
        .filter(Fichaje.user_id == user.id, Fichaje.hora_salida == None)
        .order_by(Fichaje.id.desc())
        .first()
    )
    if not fichaje:
        raise HTTPException(status_code=400, detail="No hay fichajes pendientes")
    fichaje.hora_salida = datetime.utcnow()
    db.commit()
    db.refresh(fichaje)
    return {"message": f"Salida registrada para {user.username} a las {fichaje.hora_salida}"}

@app.get("/fichajes")
def get_fichajes(db: Session = Depends(get_db)):
    # Asumo que tu models.py tiene una 'relationship' en Fichaje llamada 'user'
    fichajes = db.query(Fichaje).all()
    
    # Formateamos los datos para que coincidan con tu App.jsx
    respuesta = []
    for f in fichajes:
        respuesta.append({
            "usuario": f.user.username, # Esto necesita la relationship 'user'
            "entrada": f.hora_entrada.isoformat(), # Usamos isoformat para que JS lo entienda
            "salida": f.hora_salida.isoformat() if f.hora_salida else None # Igual aquí
        })
    return respuesta

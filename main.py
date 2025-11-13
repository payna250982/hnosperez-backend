from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
# IMPORTANTE: Asegúrate de importar Base y engine
from database import SessionLocal, User, Fichaje, get_db, Base, engine 
from passlib.context import CryptContext
from datetime import datetime

# --- 1. LA LÍNEA QUE FALTABA ---
# Esto crea tus tablas (User, Fichaje) en la nueva base de datos de Render
try:
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas (si no existían).")
except Exception as e:
    print(f"Error al crear tablas: {e}")

# --- 2. LOS MOLDES (SCHEMAS) ---
# Esto arregla el error 422
class UserCreate(BaseModel):
    username: str
    password: str

class FichajeData(BaseModel):
    username: str

# --- FIN DE LOS MOLDES ---

app = FastAPI()

# --- 3. CORS ---
# Esto permite que Vercel hable con Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# (La función 'get_db' ya se importa desde database.py)

@app.get("/")
def root():
    return {"message": "API HnosPerez funcionando correctamente"}

# --- REGISTRO CORREGIDO ---
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    
    hashed_password = pwd_context.hash(user.password)
    
    db_user = User(username=user.username, hashed_password=hashed_password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": f"Usuario {db_user.username} creado correctamente"}

# --- FICHAR ENTRADA CORREGIDO ---
@app.post("/fichar_entrada")
def fichar_entrada(data: FichajeData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    fichaje = Fichaje(user_id=user.id, hora_entrada=datetime.utcnow())
    db.add(fichaje)
    db.commit()
    db.refresh(fichaje)
    return {"message": f"Entrada registrada para {user.username} a las {fichaje.hora_entrada}"}

# --- FICHAR SALIDA CORREGIDO ---
@app.post("/fichar_salida")
def fichar_salida(data: FichajeData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
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

# --- GET FICHAJES (LA FUNCIÓN ARREGLADA) ---
@app.get("/fichajes")
def get_fichajes(db: Session = Depends(get_db)):
    
    try:
        fichajes_db = db.query(Fichaje).all()
        
        respuesta = []
        for f in fichajes_db:
            user = db.query(User).filter(User.id == f.user_id).first()
            username = user.username if user else "Usuario Desconocido"

            respuesta.append({
                "usuario": username,
                "entrada": f.hora_entrada.isoformat(),
                "salida": f.hora_salida.isoformat() if f.hora_salida else None
            })
        return respuesta
    except Exception as e:
        print(f"Error en /fichajes: {e}")
        return []



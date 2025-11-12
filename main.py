from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, User, Fichaje
from passlib.context import CryptContext
from datetime import datetime

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

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    hashed_password = pwd_context.hash(password)
    user = User(username=username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": f"Usuario {username} creado correctamente"}

@app.post("/fichar_entrada")
def fichar_entrada(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    fichaje = Fichaje(user_id=user.id, hora_entrada=datetime.utcnow())
    db.add(fichaje)
    db.commit()
    db.refresh(fichaje)
    return {"message": f"Entrada registrada para {username} a las {fichaje.hora_entrada}"}

@app.post("/fichar_salida")
def fichar_salida(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
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
    return {"message": f"Salida registrada para {username} a las {fichaje.hora_salida}"}

@app.get("/fichajes")
def get_fichajes(db: Session = Depends(get_db)):
    fichajes = db.query(Fichaje).all()
    return [
        {
            "usuario": f.user.username,
            "entrada": f.hora_entrada,
            "salida": f.hora_salida
        }
        for f in fichajes
    ]

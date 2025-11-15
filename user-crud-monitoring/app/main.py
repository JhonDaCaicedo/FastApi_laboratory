from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Base
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response
from pydantic import BaseModel

# Inicializar FastAPI
app = FastAPI()

# Métrica Prometheus
USER_CREATED = Counter("user_created_total", "Número total de usuarios creados")

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Dependencia para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo Pydantic para validación de entrada
class UserCreate(BaseModel):
    name: str
    age: int

# Endpoint para obtener todos los usuarios
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Endpoint para crear un nuevo usuario
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(name=user.name, age=user.age)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    USER_CREATED.inc()
    return new_user

# Endpoint para métricas Prometheus
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
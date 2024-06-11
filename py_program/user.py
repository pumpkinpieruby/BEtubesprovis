from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import sqlite3

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

router = APIRouter()

class User(BaseModel):
    user_nama: str
    user_email: str
    user_no_telp: str
    user_password: str
    user_nik: str
    user_tanggal_lahir: str
    user_bpjs: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str

class TokenData(BaseModel):
    email: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(email: str):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_email, user_nama, user_no_telp, user_password, user_nik, user_tanggal_lahir, user_bpjs FROM user WHERE user_email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return UserInDB(
            user_email=user[0],
            user_nama=user[1],
            user_no_telp=user[2],
            user_password=user[3],
            user_nik=user[4],
            user_tanggal_lahir=user[5],
            user_bpjs=user[6],
            hashed_password=user[3]  # Sesuaikan jika ada hashing password
        )
    return None

@router.post("/register", response_model=Token)
def register_user(user: User):
    hashed_password = get_password_hash(user.user_password)
    user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO user (user_email, user_nama, user_no_telp, user_password, user_nik, user_tanggal_lahir, user_bpjs) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user.user_email, user.user_nama, user.user_no_telp, user_in_db.hashed_password, user.user_nik, user.user_tanggal_lahir, user.user_bpjs)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.user_email}

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_email
    }

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user

@router.get("/getAllUsers", response_model=List[User])
def get_all_users(current_user: User = Depends(get_current_user)):
    conn = sqlite3.connect("carewave.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_email, user_nama, user_no_telp, user_password, user_nik, user_tanggal_lahir, user_bpjs FROM user")
    users = cursor.fetchall()
    conn.close()
    return [User(
        user_email=user[0],
        user_nama=user[1],
        user_no_telp=user[2],
        user_password=user[3],
        user_nik=user[4],
        user_tanggal_lahir=user[5],
        user_bpjs=user[6]
    ) for user in users]

@router.get("/getUserInfo", response_model=User)
def get_user_info(current_user: User = Depends(get_current_user)):
    return current_user

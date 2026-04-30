from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
import os
import jwt
import secrets
from pathlib import Path

# =========================
# CONFIGURATION GLOBALE
# =========================

APP_ENV = os.getenv("APP_ENV", "production")

if APP_ENV != "production":
    raise RuntimeError("Application must run in production mode")

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET or JWT_SECRET in ["changeme", "secret123", "CHANGE_ME"]:
    raise RuntimeError("JWT_SECRET insecure or not set")

JWT_ALGO = "HS256"

UPLOAD_DIR = Path("/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Permissions strictes (750)
os.chmod(UPLOAD_DIR, 0o750)

# =========================
# APPLICATION FASTAPI
# =========================

app = FastAPI(
    debug=False,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# =========================
# CORS RESTREINT
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

# =========================
# AUTHENTIFICATION JWT
# =========================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {"message": "Welcome to SharePy"}

@app.post("/login")
def login(username: str):
    if not username or len(username) < 3:
        raise HTTPException(status_code=400, detail="Invalid username")

    token = jwt.encode(
        {
            "user": username,
            "nonce": secrets.token_hex(8)
        },
        JWT_SECRET,
        algorithm=JWT_ALGO
    )
    return {"token": token}

@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    user=Depends(verify_token)
):
    filename = os.path.basename(file.filename)

    if not filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {"status": "uploaded", "file": filename}

@app.get("/files/{filename}")
def download(filename: str, user=Depends(verify_token)):
    safe_name = os.path.basename(filename)
    file_path = UPLOAD_DIR / safe_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)

# =========================
# ROUTES BLOQUÉES EN PROD
# =========================

@app.get("/debug/info")
def debug_info():
    raise HTTPException(status_code=404, detail="Not found")

@app.get("/admin")
def admin_panel():
    raise HTTPException(status_code=403, detail="Forbidden")

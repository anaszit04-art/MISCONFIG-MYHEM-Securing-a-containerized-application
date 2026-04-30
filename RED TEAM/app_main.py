import os, time, jwt
from fastapi import FastAPI, UploadFile, File, HTTPException, Response, Depends
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

DEBUG = True  # M2
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # M1
JWT_SECRET = os.getenv("JWT_SECRET", "changeme")  # M15

security = HTTPBearer()

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(debug=DEBUG)

# M7: CORS wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="/app/static"), name="static")


@app.get("/", response_class=PlainTextResponse)
def home():
    return "SharePy (vulnerable) is running"


@app.post("/login")
def login(username: str, password: str):
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        token = jwt.encode({"sub": username, "iat": int(time.time())}, JWT_SECRET, algorithm="HS256")
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # M13: pas de contrôle filename, overwrite possible
    dest_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(dest_path, "wb") as f:
        f.write(await file.read())
    return {"uploaded": file.filename, "public_url": f"/uploads/{file.filename}"}


@app.get("/download/{filename}")
def download(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path)


@app.get("/debug/info")  # M14
def debug_info():
    return {"env": dict(os.environ), "cwd": os.getcwd(), "debug": DEBUG}


@app.get("/version")  # M10
def version():
    return {"app": "SharePy", "framework": "FastAPI/Uvicorn", "mode": "debug"}


@app.get("/test-cookie")  # M9
def test_cookie(response: Response):
    # Cookie volontairement non sécurisé
    response.set_cookie(
        key="session_id",
        value="abc123-vulnerable-session"
        # pas Secure / HttpOnly / SameSite strict (volontaire)
    )
    return {"message": "Cookie défini sans Secure/HttpOnly/SameSite"}


@app.get("/crash")  # M2
def crash():
    return 1 / 0


@app.get("/admin")  # M15: escalation via JWT forgé
def admin(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            creds.credentials,
            JWT_SECRET,
            algorithms=["HS256"]
        )
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Forbidden")

        return {
            "status": "admin access granted",
            "user": payload.get("sub"),
            "jwt_payload": payload
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
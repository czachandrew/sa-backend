from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from database import metadata, database, engine
from fastapi.middleware.cors import CORSMiddleware
from api import api_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "https://serene-parfait-5f4de1.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(request: Request, exc: ResponseValidationError):
    print(exc.errors())
    print(exc.body)
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


@app.on_event("startup")
async def startup_event():
    metadata.create_all(engine)
    await database.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect()

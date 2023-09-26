from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging

app = FastAPI()
logging.basicConfig(filename="log.txt", level=logging.ERROR,
                    format="%(asctime)s %(message)s")


@app.exception_handler(Exception)
async def handle_exceptions(request: Request, exc: Exception):
    error_message = f"URL: {request.url}: ERROR: {str(exc)}"
    logging.error(error_message)
    return JSONResponse(content={"error": str(exc)}, status_code=500)


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=["Origin, X-Requested-With, Content-Type, Accept"],
)

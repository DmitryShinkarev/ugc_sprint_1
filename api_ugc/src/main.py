import logging

import uvicorn
from api.v1 import ugc_loader
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.logger import LOGGING
from core.settings import get_settings
from db.events_storage import get_event_storage, KafkaEventStorage

app = FastAPI(
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    title="Post-only API UGC для онлайн-кинотеатра",
    description="Сбор различной аналитики",
    version="1.0.0",
)

@app.get("/healthCheck")
async def healthCheck():
    return {"message": "Hello!"}


@app.on_event("startup")
async def startup_event():
    await get_event_storage()


@app.on_event("shutdown")
async def shutdown_event():
    event_storage: KafkaEventStorage = await get_event_storage()
    await event_storage.producer.stop()


if get_settings().app.should_check_jwt:
    from core.middleware import apply_middleware

    apply_middleware(app=app)


app.include_router(ugc_loader.router, prefix="/api/v1", tags=["UGC Loader"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=get_settings().app.host,
        port=get_settings().app.port,
        log_config=LOGGING,
        log_level=logging.DEBUG,
        reload=get_settings().app.should_reload,
    )

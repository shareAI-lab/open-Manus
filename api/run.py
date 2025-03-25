import uvicorn
from app.core.setting import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        app="main:app",
        host=settings.server.HOST,
        port=settings.server.PORT,
        reload=settings.server.RELOAD,
        log_config=None,
    )

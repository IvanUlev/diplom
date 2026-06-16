import uvicorn

from core.config import settings
import handlers #noqa

from dotenv import load_dotenv
load_dotenv()


def main():
    """Запуск приложения"""
    uvicorn.run(
        "api.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=settings.WEBAPP_PORT,
        reload=False
    )


if __name__ == "__main__":
    main()
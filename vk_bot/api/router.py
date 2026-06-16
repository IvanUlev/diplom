from fastapi import APIRouter

router_telegram = APIRouter(tags=["webhook"])

# --- Регистрация эндпоинтов (side-effect импорты) ---
import api.telegram.endpoints  # noqa: F401

router = APIRouter()

router.include_router(router_telegram, include_in_schema=False)
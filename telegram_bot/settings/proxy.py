import os
import httpx
from settings.proxy_manager import ProxyManager


def generate_proxy_url(protocol: str, login: str, password: str, host: str, port: str) -> str:
    return f"{protocol}://{login}:{password}@{host}:{port}"


# ── Основной прокси из переменных окружения ───────────────────────────────────
_env_proxy: str | None = None

if os.getenv("USE_PROXY") == "True":
    _env_proxy = generate_proxy_url(
        os.getenv("PROXY_PROTOCOL", ""),
        os.getenv("PROXY_LOGIN", ""),
        os.getenv("PROXY_PASS", ""),
        os.getenv("PROXY_HOST", ""),
        os.getenv("PROXY_PORT", ""),
    )

# ── Дополнительные прокси ─────────────────────────────────────────────────────
# Добавляй новые прокси сюда в формате "protocol://login:password@host:port".
# Основной прокси из env всегда идёт первым; эти — резервные.
EXTRA_PROXIES: list[str] = [
    "http://vichirkos21:wbT7n4K68W@5.133.163.5:50100",
    "http://vichirkos21:wbT7n4K68W@5.133.163.246:50100",
    # "http://user3:pass3@55.66.77.88:50100",
]

# ── Пул прокси и менеджер ─────────────────────────────────────────────────────
_all_proxies: list[str] = [p for p in [_env_proxy, *EXTRA_PROXIES] if p]

proxy_manager: ProxyManager | None = ProxyManager(_all_proxies) if _all_proxies else None
PROXY_URL: str | None = _env_proxy

# ── HTTP-клиент для внешних запросов (OpenAI и др.) ───────────────────────────
_limits = httpx.Limits(keepalive_expiry=20, max_keepalive_connections=10)

http_client = (
    httpx.AsyncClient(proxy=PROXY_URL, timeout=30.0, limits=_limits)
    if PROXY_URL
    else httpx.AsyncClient(timeout=30.0, limits=_limits)
)


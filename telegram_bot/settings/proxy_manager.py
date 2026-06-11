import asyncio
import time
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Awaitable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED    = "closed"     # работает нормально
    OPEN      = "open"       # отключён после серии ошибок
    HALF_OPEN = "half_open"  # тестовый запрос после восстановления


@dataclass
class ProxyEntry:
    url: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_at: Optional[float] = field(default=None)

    def is_available(self, recovery_timeout: float) -> bool:
        if self.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
            return True
        # OPEN — проверяем, истёк ли таймаут восстановления
        if self.last_failure_at is None:
            return True
        if (time.monotonic() - self.last_failure_at) >= recovery_timeout:
            self.state = CircuitState.HALF_OPEN
            return True
        return False


class ProxyManager:
    """
    Round-robin балансировщик прокси с паттерном Circuit Breaker.

    Состояния каждого прокси:
      CLOSED    — работает, принимает запросы.
      OPEN      — отключён после FAILURE_THRESHOLD ошибок подряд;
                  пропускается до истечения RECOVERY_TIMEOUT.
      HALF_OPEN — после RECOVERY_TIMEOUT отправляется один тестовый запрос;
                  успех → CLOSED, ошибка → снова OPEN.

    Добавление нового прокси:
        В settings/proxy.py добавь строку в список EXTRA_PROXIES.
    """

    FAILURE_THRESHOLD: int   = 3      # ошибок до открытия circuit
    RECOVERY_TIMEOUT:  float = 60.0   # секунд в OPEN до HALF_OPEN
    SUCCESS_THRESHOLD: int   = 2      # успехов в HALF_OPEN до CLOSED

    def __init__(self, proxy_urls: list[str]) -> None:
        urls = [u for u in proxy_urls if u]
        if not urls:
            raise ValueError("ProxyManager: список прокси не может быть пустым")
        self.proxies: list[ProxyEntry] = [ProxyEntry(url=u) for u in urls]
        self._index: int = 0

    # ------------------------------------------------------------------ #
    #  Выбор прокси                                                        #
    # ------------------------------------------------------------------ #

    def get_next(self) -> str:
        """
        Round-robin по доступным прокси.
        Если все в состоянии OPEN — возвращает ближайший к восстановлению.
        """
        available: set[str] = {
            p.url for p in self.proxies if p.is_available(self.RECOVERY_TIMEOUT)
        }

        if not available:
            # аварийный режим: все circuit open
            best = min(self.proxies, key=lambda p: p.last_failure_at or 0.0)
            logger.error(
                "Все прокси в состоянии OPEN. Принудительно используем: %s", best.url
            )
            return best.url

        n = len(self.proxies)
        for _ in range(n):
            candidate = self.proxies[self._index % n]
            self._index = (self._index + 1) % n
            if candidate.url in available:
                return candidate.url

        return next(iter(available))  # fallback (не должен достигаться)

    def get_primary(self) -> str:
        """Возвращает первый (основной из env) прокси."""
        return self.proxies[0].url

    # ------------------------------------------------------------------ #
    #  Обратная связь                                                      #
    # ------------------------------------------------------------------ #

    def report_success(self, url: str) -> None:
        """Уведомить менеджер об успешном запросе через прокси."""
        for entry in self.proxies:
            if entry.url != url:
                continue
            entry.success_count += 1
            if entry.state == CircuitState.HALF_OPEN:
                if entry.success_count >= self.SUCCESS_THRESHOLD:
                    entry.state = CircuitState.CLOSED
                    entry.failure_count = 0
                    logger.info("Прокси восстановлен (→ CLOSED): %s", url)
            elif entry.state == CircuitState.CLOSED:
                # медленное сокращение счётчика ошибок при успехах
                entry.failure_count = max(0, entry.failure_count - 1)
            break

    def report_failure(self, url: str) -> None:
        """Уведомить менеджер об ошибке запроса через прокси."""
        for entry in self.proxies:
            if entry.url != url:
                continue
            entry.failure_count += 1
            entry.last_failure_at = time.monotonic()
            entry.success_count = 0

            if entry.state == CircuitState.HALF_OPEN:
                entry.state = CircuitState.OPEN
                logger.warning(
                    "Прокси вернулся в OPEN после неудачной проверки: %s", url
                )
            elif (
                entry.state == CircuitState.CLOSED
                and entry.failure_count >= self.FAILURE_THRESHOLD
            ):
                entry.state = CircuitState.OPEN
                logger.warning(
                    "Прокси отключён (→ OPEN, %d ошибок): %s",
                    entry.failure_count,
                    url,
                )
            break

    # ------------------------------------------------------------------ #
    #  Retry-обёртка                                                       #
    # ------------------------------------------------------------------ #

    async def execute_with_retry(
        self,
        coro_factory: Callable[[str], Awaitable[T]],
        max_attempts: Optional[int] = None,
    ) -> T:
        """
        Выполняет ``coro_factory(proxy_url)`` с автоматической сменой прокси.

        Каждый прокси из пула пробуется не более одного раза за вызов.
        При успехе вызывает ``report_success``, при ошибке — ``report_failure``.

        :param coro_factory:  callable(proxy_url: str) -> Awaitable
        :param max_attempts:  потолок попыток; по умолчанию = кол-во прокси
        :raises:              последнее пойманное исключение или RuntimeError
        """
        from aiogram.exceptions import TelegramRetryAfter

        max_proxy_attempts = max_attempts if max_attempts is not None else len(self.proxies)
        tried: set[str] = set()
        last_error: Optional[Exception] = None
        proxy_attempts = 0

        while proxy_attempts < max_proxy_attempts:
            proxy_url = self.get_next()

            if proxy_url in tried:
                if len(tried) >= len(self.proxies):
                    break
                continue

            tried.add(proxy_url)
            proxy_attempts += 1

            try:
                result: T = await coro_factory(proxy_url)
                self.report_success(proxy_url)
                return result
            except TelegramRetryAfter as exc:
                # Rate limit от Telegram — не вина прокси, ждём и повторяем без смены прокси
                retry_after = exc.retry_after if hasattr(exc, "retry_after") else 5
                logger.warning(
                    "Telegram rate limit (retry after %ds). Ждём и повторяем через прокси %s...",
                    retry_after,
                    proxy_url,
                )
                await asyncio.sleep(retry_after + 1)
                tried.discard(proxy_url)
                proxy_attempts -= 1  # не считаем rate-limit как попытку смены прокси
                last_error = exc
            except Exception as exc:
                self.report_failure(proxy_url)
                last_error = exc
                logger.warning(
                    "Прокси %s → ошибка: %s. Переключаемся...", proxy_url, exc
                )

        raise last_error or RuntimeError("Все прокси недоступны")

    # ------------------------------------------------------------------ #
    #  Статус / мониторинг                                                 #
    # ------------------------------------------------------------------ #

    def status(self) -> list[dict]:
        """Текущее состояние всех прокси (для логов и мониторинга)."""
        return [
            {
                "url": p.url,
                "state": p.state.value,
                "failures": p.failure_count,
                "successes": p.success_count,
            }
            for p in self.proxies
        ]

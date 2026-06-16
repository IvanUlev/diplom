import logging
import sys

class NoWebhookFilter(logging.Filter):
    def filter(self, record):
        return 'webhook' not in record.getMessage().lower()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


# uvicorn_access = logging.getLogger("uvicorn.access")
# uvicorn_access.addFilter(NoWebhookFilter())
# logging.getLogger("uvicorn").setLevel(logging.WARNING)

# logging.getLogger("aiogram.event").setLevel(logging.WARNING)
# logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)
# logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
# logging.getLogger("httpcore.connection").setLevel(logging.INFO)
# logging.getLogger("httpcore.http11").setLevel(logging.WARNING)
# logging.getLogger("chromadb.telemetry.product.posthog").setLevel(logging.WARNING)
# logging.getLogger("chromadb.config").setLevel(logging.WARNING)
# logging.getLogger("python_multipart.multipart").setLevel(logging.WARNING)
# logging.getLogger("openai._base_client").setLevel(logging.INFO)
# logging.getLogger("fastapi").setLevel(logging.INFO)
# logging.getLogger("pdfinterp").setLevel(logging.INFO)
# logging.getLogger("pdfminer.pdfparser").setLevel(logging.INFO)
# logging.getLogger("pdfminer.pdfpage").setLevel(logging.INFO)
# logging.getLogger("pdfminer.cmapdb").setLevel(logging.INFO)
# logging.getLogger("pdfminer.psparser").setLevel(logging.INFO)
# logging.getLogger("pydub.converter").setLevel(logging.WARNING)
# logging.getLogger("pdfminer.pdfdocument").setLevel(logging.WARNING)
# logging.getLogger("pdfminer.pdfinterp").setLevel(logging.WARNING)
# logging.getLogger("asyncio").setLevel(logging.WARNING)
# logging.getLogger("tzlocal").setLevel(logging.WARNING)
# logging.getLogger("urllib3").setLevel(logging.WARNING)

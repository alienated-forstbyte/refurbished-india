import logging
from app.services.change_detector import ChangeEvent, ChangeType

logger = logging.getLogger(__name__)


class Notifier:
    async def send_notification(self, event: ChangeEvent, channels: list[str] | None = None):
        if channels is None:
            channels = ["log"]

        message = self._format_event(event)

        for channel in channels:
            if channel == "log":
                logger.info(f"[notifier] {message}")
            elif channel == "email":
                await self._send_email(message)
            elif channel == "telegram":
                await self._send_telegram(message)
            elif channel == "discord":
                await self._send_discord(message)

    def _format_event(self, event: ChangeEvent) -> str:
        product = event.product
        name = product.product_name or "Unknown Product"
        match event.type:
            case ChangeType.NEW_PRODUCT:
                return f"🆕 New: {name} — ₹{product.price}"
            case ChangeType.PRICE_CHANGED:
                return f"💰 Price drop: {name} — ₹{event.old_price} → ₹{event.new_price}"
            case ChangeType.BACK_IN_STOCK:
                return f"✅ In stock: {name} — ₹{product.price}"
            case ChangeType.OUT_OF_STOCK:
                return f"❌ Out of stock: {name}"
            case ChangeType.REMOVED:
                return f"🗑️ Removed: {name}"
        return f"Event: {name}"

    async def _send_email(self, message: str):
        logger.info(f"[notifier] Email would send: {message}")

    async def _send_telegram(self, message: str):
        logger.info(f"[notifier] Telegram would send: {message}")

    async def _send_discord(self, message: str):
        logger.info(f"[notifier] Discord would send: {message}")

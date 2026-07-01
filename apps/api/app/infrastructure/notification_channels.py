"""Notification channels (console only until real integrations needed)."""

from abc import ABC, abstractmethod


class INotificationChannel(ABC):
    """Extension point: one implementation per delivery channel (push/sms/email/console)."""

    name: str

    @abstractmethod
    async def send(self, recipient: str, message: str) -> bool:
        pass


class ConsoleChannel(INotificationChannel):
    """Fallback/dev channel: logs to stdout."""

    name = "console"

    async def send(self, recipient: str, message: str) -> bool:
        print(f"[console-notification] to={recipient} message={message}")
        return True

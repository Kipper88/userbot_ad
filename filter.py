from aiogram.types import Message
from aiogram import BaseMiddleware

from typing import Callable, Dict, Any, Awaitable

from cfg import admin_id


class isAdmin(BaseMiddleware):
    def __init__(self) -> None:
        self.counter = 0

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if event.from_user.id in admin_id:   
            return await handler(event, data)
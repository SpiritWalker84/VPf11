"""Учёт «активных» идентификаторов с защитой от гонок."""

from __future__ import annotations

import threading
import time
from typing import Any


class ActiveUsersTracker:
    """
    Хранит ограниченный список активных id с блокировкой.

    Используется демонстрационным фоновым эндпоинтом; логика обрезки
    намеренно простая (FIFO при переполнении).
    """

    def __init__(self, max_size: int = 5, sleep_s: float = 0.1) -> None:
        self._max = max_size
        self._sleep_s = sleep_s
        self._lock = threading.Lock()
        self._active: list[int] = []

    def register(self, user_id: int) -> None:
        """Добавляет id и при переполнении удаляет самый старый элемент."""
        with self._lock:
            self._active.append(user_id)
            time.sleep(self._sleep_s)
            if len(self._active) > self._max:
                self._active.pop(0)

    def snapshot(self) -> dict[str, Any]:
        """Возвращает неизменяемый снимок состояния для JSON-ответа."""
        with self._lock:
            return {"len": len(self._active), "active": list(self._active)}

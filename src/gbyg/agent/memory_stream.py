from __future__ import annotations

import numpy as np

class MemoryStream(list):
    _last_index = 0

    def __init__(self, iterable=None):
        if iterable is None:
            super().__init__()
        else:
            super().__init__(iterable)

    def _get_index(self) -> int:
        self._last_index += 1
        return self._last_index

    def get_last_created(self, n, minimum_created_time=0) -> list[dict[str, str]]:
        return self._get_last(n, "created", minimum_created_time)

    def get_last_acessed(self, n, minimum_created_time=0) -> list[dict[str, str]]:
        return self._get_last(n, "acessed", minimum_created_time)

    def _get_last(self, n, key, minimum_created_time=0) -> list[dict[str, str]]:
        n = min(len(self), n)

        times = [memory[key] for memory in self]

        indexes = np.argpartition(times, -n)[-n:]

        result = [self[i] for i in indexes if self[i]["created"] > minimum_created_time]

        return result
    
    def _ensure_index(self, item):
        if "index" not in item:
            item["index"] = self._get_index()
        else:
            self._last_index = max(int(item["index"]), self._last_index)

        if "last_acessed" not in item:
            item["last_acessed"] = item["created"]

        return item

    def __setitem__(self, index, item):
        item = self._ensure_index(item)
        super().__setitem__(index, item)

    def insert(self, index, item):
        item = self._ensure_index(item)
        super().insert(index, item)

    def append(self, item):
        item = self._ensure_index(item)
        super().append(item)
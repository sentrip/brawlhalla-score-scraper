import time
from abc import ABC
from multiprocessing.connection import Client, Listener
from threading import Thread
from typing import Any, Optional

__all__ = [
    'Delegate',
    'Emitter',
    'check_event', 'on_event'
]


class Delegate(ABC):

    def check_event(self, event: str, data: Any = None) -> int:
        pass

    def on_event(self, event: str, data: Any = None):
        pass


class Emitter:
    def __init__(self):
        self.delegate = None

    def connect(self, delegate: Delegate):
        self.delegate = delegate

    def check_event(self, event: str, data: Any = None) -> int:
        return check_event(self.delegate, event, data)

    def on_event(self, event: str, data: Any = None):
        on_event(self.delegate, event, data)


def check_event(delegate: Optional[Delegate], event: str, data: Any = None) -> int:
    if delegate is not None:
        return delegate.check_event(event, data)
    return False


def on_event(delegate: Optional[Delegate], event: str, data: Any = None):
    if delegate is not None:
        delegate.on_event(event, data)


class SocketDelegate(Delegate):
    def __init__(self):
        self._client = None
        self._queue = []
        self._poll_interval = 0.001
        self._update_interval = 0.001
        self._time_since_last_update = 0

    def connect(self, port: int):
        self._client = Client(('localhost', port))
        Thread(target=self._run, daemon=True).start()

    def on_custom_event(self, code: str, event: str, data: Any) -> Any:
        pass

    def _run(self):
        while True:
            time.sleep(self._poll_interval)
            self._time_since_last_update += self._poll_interval
            self._read_events()
            if self._time_since_last_update >= self._update_interval:
                self._time_since_last_update = 0
                self._update()

    def _read_events(self):
        while self._client.poll():
            self._queue.append(self._client.recv())

    def _update(self):
        for t, event, data in self._queue:
            if t == 'c':
                self._client.send(self.check_event(event, data))
            elif t == 'e':
                self.on_event(event, data)
            else:
                result = self.on_custom_event(t, event, data)
                if result is not None:
                    self._client.send(result)

        self._queue.clear()


class SocketEmitter(Emitter):

    def __init__(self):
        super().__init__()
        self._conn = None
        self._server = None

    def connect(self, port: int):
        self._server = Listener(('localhost', port))
        Thread(target=self._connect, daemon=True).start()

    def wait_for_client(self):
        while self._conn is None:
            time.sleep(0.001)

    def check_event(self, event: str, data: Any = None) -> int:
        self._conn.send(('c', event, data))
        return self._conn.recv()

    def on_event(self, event: str, data: Any = None):
        self._conn.send(('e', event, data))

    def _connect(self):
        self._conn = self._server.accept()

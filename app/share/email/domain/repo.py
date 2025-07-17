from abc import ABC, abstractmethod


class EmailRepository(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> None:
        pass

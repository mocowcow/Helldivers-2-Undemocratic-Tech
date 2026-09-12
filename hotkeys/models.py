from dataclasses import dataclass


@dataclass(frozen=True)
class Binding:
    key: str
    action: str
    value: str = ""

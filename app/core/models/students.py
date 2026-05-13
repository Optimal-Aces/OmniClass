from dataclasses import dataclass
from typing import Optional

@dataclass
class Student:
    id: str
    class_id: str
    last_name: str
    first_name: str
    lrn: Optional[str] = None
    middle_name: Optional[str] = None
    sex: Optional[str] = None
    birthdate: Optional[str] = None
    guardian_name: Optional[str] = None
    emergency_contact: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.last_name}, {self.first_name}"

    @property
    def initials(self) -> str:
        return f"{self.first_name[0]}{self.last_name[0]}".upper()
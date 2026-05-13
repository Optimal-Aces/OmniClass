from dataclasses import dataclass

@dataclass
class Subject:
    id: str
    class_id: str
    name: str
    code: str = ""
    ww_weight: float = 0.40
    pt_weight: float = 0.40
    qa_weight: float = 0.20
from dataclasses import dataclass

@dataclass
class ClassSection:
    id: str
    teacher_id: str
    name: str
    grade_level: int
    school_year: str
    term: str = "Full Year"
    is_archived: bool = False
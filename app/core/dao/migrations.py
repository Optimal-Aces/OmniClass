MIGRATIONS = {
    1: """
    CREATE TABLE IF NOT EXISTS teachers (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
        school TEXT, password TEXT NOT NULL, is_pro INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS classes (
        id TEXT PRIMARY KEY, teacher_id TEXT NOT NULL REFERENCES teachers(id),
        name TEXT NOT NULL, grade_level INTEGER NOT NULL,
        school_year TEXT NOT NULL, term TEXT NOT NULL DEFAULT 'Full Year',
        is_archived INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY, class_id TEXT NOT NULL REFERENCES classes(id),
        lrn TEXT, last_name TEXT NOT NULL, first_name TEXT NOT NULL,
        middle_name TEXT, sex TEXT, birthdate TEXT,
        guardian_name TEXT, emergency_contact TEXT,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS subjects (
        id TEXT PRIMARY KEY, class_id TEXT NOT NULL REFERENCES classes(id),
        name TEXT NOT NULL, code TEXT,
        ww_weight REAL DEFAULT 0.40, pt_weight REAL DEFAULT 0.40, qa_weight REAL DEFAULT 0.20,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS grade_columns (
        id TEXT PRIMARY KEY, subject_id TEXT NOT NULL REFERENCES subjects(id),
        term TEXT NOT NULL, category TEXT NOT NULL CHECK(category IN ('WW','PT','QA')),
        col_number INTEGER NOT NULL, max_score REAL NOT NULL DEFAULT 100, label TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS grade_entries (
        id TEXT PRIMARY KEY, column_id TEXT NOT NULL REFERENCES grade_columns(id),
        student_id TEXT NOT NULL REFERENCES students(id),
        score REAL, edited_by TEXT, edited_at TEXT,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending',
        UNIQUE(column_id, student_id)
    );
    CREATE TABLE IF NOT EXISTS attendance (
        id TEXT PRIMARY KEY, class_id TEXT NOT NULL REFERENCES classes(id),
        student_id TEXT NOT NULL REFERENCES students(id),
        date TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('present','absent','late','excused')),
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending',
        UNIQUE(student_id, date)
    );
    CREATE TABLE IF NOT EXISTS anecdotal_records (
        id TEXT PRIMARY KEY, student_id TEXT NOT NULL REFERENCES students(id),
        category TEXT NOT NULL, observation TEXT NOT NULL, logged_by TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS lesson_logs (
        id TEXT PRIMARY KEY, class_id TEXT NOT NULL REFERENCES classes(id),
        subject_id TEXT REFERENCES subjects(id),
        date TEXT NOT NULL, topic TEXT NOT NULL,
        competency TEXT, objectives TEXT, hours_taught REAL DEFAULT 1.0, content TEXT,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS assessments (
        id TEXT PRIMARY KEY, class_id TEXT NOT NULL REFERENCES classes(id),
        subject_id TEXT REFERENCES subjects(id), title TEXT NOT NULL,
        grade_level INTEGER, items INTEGER NOT NULL DEFAULT 0,
        hours REAL DEFAULT 1.0, tos_data TEXT, questions TEXT,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS recitation_sessions (
        id TEXT PRIMARY KEY, class_id TEXT NOT NULL REFERENCES classes(id),
        subject_id TEXT REFERENCES subjects(id), topic TEXT NOT NULL,
        questions TEXT, scores TEXT, synced_to_gradebook INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY, class_id TEXT NOT NULL REFERENCES classes(id),
        subject_id TEXT REFERENCES subjects(id), title TEXT NOT NULL,
        max_score REAL DEFAULT 100, brief TEXT, rubric TEXT,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS sf10_entries (
        id TEXT PRIMARY KEY, student_lrn TEXT NOT NULL, school_year TEXT NOT NULL,
        grade_level INTEGER NOT NULL, section TEXT, school_name TEXT, adviser_name TEXT,
        days_present INTEGER DEFAULT 0, days_absent INTEGER DEFAULT 0,
        general_average REAL, promotion_status TEXT, remarks TEXT,
        is_locked INTEGER DEFAULT 0, locked_by TEXT, locked_at TEXT,
        is_manual INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
        synced_at TEXT, sync_status TEXT DEFAULT 'pending',
        UNIQUE(student_lrn, school_year)
    );
    CREATE TABLE IF NOT EXISTS sf10_subject_grades (
        id TEXT PRIMARY KEY, entry_id TEXT NOT NULL REFERENCES sf10_entries(id),
        subject TEXT NOT NULL, q1 REAL, q2 REAL, q3 REAL, q4 REAL, final_grade REAL,
        synced_at TEXT, sync_status TEXT DEFAULT 'pending'
    );
    CREATE TABLE IF NOT EXISTS sync_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT NOT NULL,
        record_id TEXT NOT NULL,
        operation TEXT NOT NULL CHECK(operation IN ('insert','update','delete')),
        payload TEXT, created_at TEXT DEFAULT (datetime('now')), attempts INTEGER DEFAULT 0
    );
    """
}
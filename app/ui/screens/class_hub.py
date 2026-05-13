import customtkinter as ctk
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT
)

class ClassHubScreen(ctk.CTkFrame):
    def __init__(self, master, db, teacher: dict, class_data: dict, **kwargs):
        super().__init__(master, fg_color=SURFACE, **kwargs)
        self.db         = db
        self.teacher    = teacher
        self.class_data = class_data
        self.master     = master
        self._build()

    def _build(self):
        # Sidebar
        sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar, text="OmniClass",
            font=(FONT, 18, "bold"), text_color="#ffffff"
        ).pack(pady=(28, 4), padx=20, anchor="w")
        ctk.CTkLabel(
            sidebar, text=self.teacher.get("name", "Teacher"),
            font=(FONT, 12), text_color=MUTED
        ).pack(padx=20, anchor="w")
        ctk.CTkLabel(
            sidebar, text=self.class_data.get("name", ""),
            font=(FONT, 11), text_color="#475569"
        ).pack(padx=20, anchor="w", pady=(0, 24))

        nav_items = [
            ("← Dashboard",  self._back_to_dashboard),
            ("👥 Students",   self._open_students),
            ("📅 Attendance", self._open_attendance),
            ("📊 Gradebook",  self._open_gradebook),
            ("📈 Analytics",  self._open_analytics),
            ("📓 Lesson Logs",self._open_lesson_logs),
            ("📝 Assessments",self._open_assessments),
            ("🎯 Recitation", self._open_recitation),
            ("🧪 Project Lab",self._open_project_lab),
        ]

        for label, cmd in nav_items:
            is_back = label.startswith("←")
            btn = ctk.CTkButton(
                sidebar, text=f"  {label}",
                anchor="w",
                fg_color="#1e2d45" if is_back else "transparent",
                hover_color="#1e2d45", height=38,
                text_color=MUTED if is_back else "#cbd5e1",
                font=(FONT, 13), command=cmd
            )
            btn.pack(fill="x", padx=12, pady=2)

        # Main content
        self.content = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        self._show_hub()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_hub(self):
        self._clear_content()

        # Top bar
        topbar = ctk.CTkFrame(self.content, fg_color="#ffffff", height=56, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkLabel(
            topbar, text="Class Overview",
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)

        # Body
        body = ctk.CTkScrollableFrame(self.content, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=24, pady=24)

        # Header banner
        banner = ctk.CTkFrame(body, fg_color=SIDEBAR_BG, corner_radius=12, height=100)
        banner.pack(fill="x", pady=(0, 24))
        banner.pack_propagate(False)

        ctk.CTkLabel(
            banner,
            text=f"Grade {self.class_data['grade_level']}",
            font=(FONT, 11), text_color=MUTED
        ).pack(anchor="w", padx=24, pady=(18, 0))
        ctk.CTkLabel(
            banner,
            text=self.class_data["name"],
            font=(FONT, 20, "bold"), text_color="#ffffff"
        ).pack(anchor="w", padx=24)
        ctk.CTkLabel(
            banner,
            text=f"SY {self.class_data['school_year']}  ·  {self.class_data['term']}",
            font=(FONT, 12), text_color=MUTED
        ).pack(anchor="w", padx=24)

        # Stats row
        stats_frame = ctk.CTkFrame(body, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 24))

        student_count = self._count_students()
        for i, (label, value, color) in enumerate([
            ("Students Enrolled", str(student_count), PRIMARY),
            ("Subjects",          str(self._count_subjects()), "#8b5cf6"),
            ("Attendance Records",str(self._count_attendance()), "#10b981"),
        ]):
            card = ctk.CTkFrame(stats_frame, fg_color="#ffffff", corner_radius=10)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(
                card, text=value,
                font=(FONT, 28, "bold"), text_color=color
            ).pack(pady=(16, 2), padx=20, anchor="w")
            ctk.CTkLabel(
                card, text=label,
                font=(FONT, 12), text_color=TEXT_SECONDARY
            ).pack(pady=(0, 16), padx=20, anchor="w")

        # Module cards
        ctk.CTkLabel(
            body, text="Modules",
            font=(FONT, 14, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 10))

        modules_frame = ctk.CTkFrame(body, fg_color="transparent")
        modules_frame.pack(fill="x")

        modules = [
            ("👥", "Students",    "Manage roster, edit profiles, view LRNs.",         self._open_students,    PRIMARY),
            ("📅", "Attendance",  "Track daily attendance, lates, and absences.",      self._open_attendance,  "#8b5cf6"),
            ("📊", "Gradebook",   "Manage subjects, grading sheets, DepEd forms.",     self._open_gradebook,   "#10b981"),
            ("📈", "Analytics",   "Performance insights and class averages.",           self._open_analytics,   "#f59e0b"),
            ("📓", "Lesson Logs", "Draft daily lesson plans with AI assistance.",       self._open_lesson_logs, "#ef4444"),
            ("📝", "Assessments", "Generate exams, quizzes, and TOS with AI.",         self._open_assessments, "#06b6d4"),
            ("🎯", "Recitation",  "Gamified oral recitation with live leaderboard.",   self._open_recitation,  "#ec4899"),
            ("🧪", "Project Lab", "Design performance tasks and grading rubrics.",     self._open_project_lab, "#84cc16"),
        ]

        for i, (icon, title, desc, cmd, color) in enumerate(modules):
            card = ctk.CTkFrame(modules_frame, fg_color="#ffffff", corner_radius=12)
            card.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="nsew")
            modules_frame.grid_columnconfigure(i % 2, weight=1)

            # Color bar
            ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=0).pack(fill="x")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=14)

            ctk.CTkLabel(
                inner, text=f"{icon}  {title}",
                font=(FONT, 14, "bold"), text_color=TEXT_PRIMARY
            ).pack(anchor="w")
            ctk.CTkLabel(
                inner, text=desc,
                font=(FONT, 11), text_color=TEXT_SECONDARY,
                wraplength=280, justify="left"
            ).pack(anchor="w", pady=(4, 10))

            ctk.CTkButton(
                inner, text="Open →",
                fg_color=SURFACE, text_color=color,
                hover_color="#e2e8f0", height=30,
                font=(FONT, 12), anchor="w",
                command=cmd
            ).pack(anchor="w")

    def _count_students(self) -> int:
        r = self.db.connect().execute(
            "SELECT COUNT(*) as c FROM students WHERE class_id=?",
            (self.class_data["id"],)
        ).fetchone()
        return r["c"] if r else 0

    def _count_subjects(self) -> int:
        r = self.db.connect().execute(
            "SELECT COUNT(*) as c FROM subjects WHERE class_id=?",
            (self.class_data["id"],)
        ).fetchone()
        return r["c"] if r else 0

    def _count_attendance(self) -> int:
        r = self.db.connect().execute(
            "SELECT COUNT(*) as c FROM attendance WHERE class_id=?",
            (self.class_data["id"],)
        ).fetchone()
        return r["c"] if r else 0

    def _back_to_dashboard(self):
        from app.ui.screens.dashboard import DashboardScreen
        self.pack_forget()
        dash = DashboardScreen(self.master, self.db, teacher=self.teacher)
        dash.pack(fill="both", expand=True)

    def _open_students(self):
        from app.ui.screens.student_profile import StudentProfileScreen
        self.pack_forget()
        screen = StudentProfileScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        screen.pack(fill="both", expand=True)

    def _open_attendance(self):
        from app.ui.screens.attendance import AttendanceScreen
        self.pack_forget()
        screen = AttendanceScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        screen.pack(fill="both", expand=True)

    def _open_gradebook(self):
        from app.ui.screens.gradebook import GradebookScreen
        self.pack_forget()
        screen = GradebookScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        screen.pack(fill="both", expand=True)

    def _open_analytics(self):
        from app.ui.screens.analytics import AnalyticsScreen
        self.pack_forget()
        screen = AnalyticsScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        screen.pack(fill="both", expand=True)

    def _open_lesson_logs(self):
        from app.ui.screens.lesson_logs import LessonLogsScreen
        self.pack_forget()
        screen = LessonLogsScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        screen.pack(fill="both", expand=True)

    def _open_assessments(self):
        from app.ui.screens.assessments import AssessmentsScreen
        self.pack_forget()
        screen = AssessmentsScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        screen.pack(fill="both", expand=True)

    def _open_recitation(self):
        from app.ui.screens.recitation import RecitationScreen
        self.pack_forget()
        screen = RecitationScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        screen.pack(fill="both", expand=True)

    def _open_project_lab(self):
        from app.ui.screens.project_lab import ProjectLabScreen
        self.pack_forget()
        screen = ProjectLabScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        screen.pack(fill="both", expand=True)
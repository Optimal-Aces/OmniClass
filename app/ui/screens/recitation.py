import customtkinter as ctk
import uuid
import random
from datetime import datetime
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT, DANGER, SUCCESS, WARNING
)

class RecitationScreen(ctk.CTkFrame):
    def __init__(self, master, db, teacher: dict, class_data: dict, **kwargs):
        super().__init__(master, fg_color=SURFACE, **kwargs)
        self.db         = db
        self.teacher    = teacher
        self.class_data = class_data
        self.master     = master
        self.session    = None
        self.questions  = []
        self.q_index    = 0
        self.scores     = {}
        self._build()

    def _build(self):
        sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(
            sidebar, text="TeachCRM",
            font=(FONT, 18, "bold"), text_color="#ffffff"
        ).pack(pady=(28, 4), padx=20, anchor="w")
        ctk.CTkLabel(
            sidebar, text=self.teacher.get("name", ""),
            font=(FONT, 12), text_color=MUTED
        ).pack(padx=20, anchor="w")
        ctk.CTkLabel(
            sidebar, text=self.class_data.get("name", ""),
            font=(FONT, 11), text_color="#475569"
        ).pack(padx=20, anchor="w", pady=(0, 24))

        for label, cmd in [
            ("← Class Hub",   self._back),
            ("🎯 Recitation",  None),
        ]:
            ctk.CTkButton(
                sidebar, text=f"  {label}", anchor="w",
                fg_color=PRIMARY if "Recitation" in label else "#1e2d45",
                hover_color="#3d5ce0" if "Recitation" in label else "#1e2d45",
                height=38, font=(FONT, 13),
                text_color="#ffffff" if "Recitation" in label else MUTED,
                command=cmd or (lambda: None)
            ).pack(fill="x", padx=12, pady=2)

        self.content = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)
        self._render_hub()

    def _render_hub(self):
        for w in self.content.winfo_children():
            w.destroy()

        topbar = ctk.CTkFrame(self.content, fg_color="#ffffff", height=56, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkLabel(
            topbar, text="Gamified Recitation",
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            topbar, text="+ Start New Session",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            height=34, font=(FONT, 13),
            command=self._new_session_dialog
        ).pack(side="right", padx=24, pady=11)

        body = ctk.CTkScrollableFrame(self.content, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=24, pady=24)

        # Banner
        banner = ctk.CTkFrame(body, fg_color="#4c0519", corner_radius=12, height=80)
        banner.pack(fill="x", pady=(0, 20))
        banner.pack_propagate(False)
        ctk.CTkLabel(
            banner, text="Gamified Recitation",
            font=(FONT, 17, "bold"), text_color="#ffffff"
        ).pack(anchor="w", padx=24, pady=(16, 2))
        ctk.CTkLabel(
            banner,
            text="Interactive oral recitation with spinner wheel and live leaderboard.",
            font=(FONT, 12), text_color="#fda4af"
        ).pack(anchor="w", padx=24)

        # Session history
        ctk.CTkLabel(
            body, text="Session History",
            font=(FONT, 14, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))

        table = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
        table.pack(fill="both", expand=True)

        header = ctk.CTkFrame(table, fg_color="#f8fafc", height=36, corner_radius=0)
        header.pack(fill="x")
        for col, width, text in [
            (0, 260, "Topic"),
            (1, 120, "Subject"),
            (2, 140, "Date"),
            (3, 100, "Status"),
            (4, 80,  "Action"),
        ]:
            ctk.CTkLabel(
                header, text=text,
                font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY,
                width=width, anchor="w"
            ).grid(row=0, column=col, padx=(12 if col == 0 else 4, 4), pady=8, sticky="w")

        sessions = self._load_sessions()
        rows_frame = ctk.CTkFrame(table, fg_color="#ffffff", corner_radius=0)
        rows_frame.pack(fill="both", expand=True)

        if not sessions:
            ctk.CTkLabel(
                rows_frame,
                text="No sessions yet.\nStart a new session to begin.",
                font=(FONT, 13), text_color=TEXT_SECONDARY, justify="center"
            ).pack(pady=40)
            return

        for i, s in enumerate(sessions):
            bg  = "#ffffff" if i % 2 == 0 else "#f8fafc"
            row = ctk.CTkFrame(rows_frame, fg_color=bg, height=44, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            ctk.CTkLabel(
                row, text=s["topic"],
                font=(FONT, 12), text_color=TEXT_PRIMARY,
                width=260, anchor="w"
            ).grid(row=0, column=0, padx=12, pady=10, sticky="w")

            pill = ctk.CTkFrame(row, fg_color=PRIMARY, corner_radius=6, height=22, width=100)
            pill.grid(row=0, column=1, padx=4, pady=11, sticky="w")
            ctk.CTkLabel(
                pill, text=(s.get("subject_name") or "—")[:12],
                font=(FONT, 10, "bold"), text_color="#ffffff"
            ).pack(expand=True)

            ctk.CTkLabel(
                row, text=s["created_at"][:10],
                font=(FONT, 12), text_color=TEXT_SECONDARY,
                width=140, anchor="w"
            ).grid(row=0, column=2, padx=4, pady=10, sticky="w")

            synced = s["synced_to_gradebook"]
            status_pill = ctk.CTkFrame(
                row,
                fg_color=SUCCESS if synced else WARNING,
                corner_radius=6, height=22, width=80
            )
            status_pill.grid(row=0, column=3, padx=4, pady=11, sticky="w")
            ctk.CTkLabel(
                status_pill,
                text="Synced" if synced else "Pending",
                font=(FONT, 10, "bold"), text_color="#ffffff"
            ).pack(expand=True)

            ctk.CTkButton(
                row, text="▶ Resume", width=80, height=28,
                fg_color=SURFACE, text_color=PRIMARY,
                hover_color="#e2e8f0", font=(FONT, 11),
                command=lambda sess=s: self._start_session(sess)
            ).grid(row=0, column=4, padx=4, pady=8)

    def _new_session_dialog(self):
        students = self._load_students()
        if not students:
            from tkinter import messagebox
            messagebox.showinfo("No Students", "Add students first.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("New Recitation Session")
        dialog.geometry("460x340")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="New Recitation Session",
            font=(FONT, 16, "bold")
        ).pack(pady=(20, 16), padx=24, anchor="w")

        ctk.CTkLabel(dialog, text="Topic", font=(FONT, 12)).pack(anchor="w", padx=24)
        topic_e = ctk.CTkEntry(
            dialog, placeholder_text="e.g. Pagsusulat para sa Pagtatrabaho",
            width=410, height=38
        )
        topic_e.pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Subject", font=(FONT, 12)).pack(anchor="w", padx=24)
        subjects  = self._load_subjects()
        sub_names = [s["name"] for s in subjects]
        sub_var   = ctk.StringVar(value=sub_names[0] if sub_names else "")
        ctk.CTkOptionMenu(
            dialog,
            values=sub_names if sub_names else ["No subjects"],
            variable=sub_var, width=410
        ).pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Number of Questions", font=(FONT, 12)).pack(anchor="w", padx=24)
        q_e = ctk.CTkEntry(dialog, placeholder_text="e.g. 20", width=410, height=38)
        q_e.insert(0, "20")
        q_e.pack(padx=24, pady=(2, 10))

        err = ctk.CTkLabel(dialog, text="", text_color=DANGER, font=(FONT, 11))
        err.pack()

        def start():
            topic = topic_e.get().strip()
            if not topic:
                err.configure(text="Topic is required.")
                return
            try:
                q_count = int(q_e.get().strip() or "20")
            except ValueError:
                err.configure(text="Invalid question count.")
                return

            sub_id = None
            for s in subjects:
                if s["name"] == sub_var.get():
                    sub_id = s["id"]
                    break

            # Generate simple questions
            questions = self._generate_questions(topic, q_count)
            now = datetime.utcnow().isoformat()
            session_id = str(uuid.uuid4())

            self.db.connect().execute(
                """INSERT INTO recitation_sessions
                   (id, class_id, subject_id, topic, questions, created_at)
                   VALUES (?,?,?,?,?,?)""",
                (session_id, self.class_data["id"], sub_id,
                 topic, str(questions), now)
            )
            self.db.connect().commit()

            session = {
                "id": session_id,
                "topic": topic,
                "subject_id": sub_id,
                "subject_name": sub_var.get(),
                "questions": str(questions),
                "synced_to_gradebook": 0,
                "created_at": now,
            }
            dialog.destroy()
            self._start_session(session)

        ctk.CTkButton(
            dialog, text="Start Session",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            width=410, height=42, command=start
        ).pack(padx=24, pady=12)

    def _generate_questions(self, topic: str, count: int) -> list:
        base = [
            f"Ano ang kahulugan ng {topic}?",
            f"Magbigay ng halimbawa ng {topic}.",
            f"Bakit mahalaga ang {topic}?",
            f"Ipaliwanag ang {topic} sa inyong sariling salita.",
            f"Paano ginagamit ang {topic} sa pang-araw-araw na buhay?",
            f"Ano ang pagkakaiba ng {topic} sa iba?",
            f"Ilista ang mga katangian ng {topic}.",
            f"Sino ang gumagamit ng {topic}?",
            f"Kailan ginagamit ang {topic}?",
            f"Ano ang benepisyo ng pag-aaral ng {topic}?",
        ]
        questions = []
        for i in range(count):
            questions.append(base[i % len(base)])
        return questions

    def _start_session(self, session: dict):
        self.session   = session
        self.questions = eval(session.get("questions", "[]"))
        self.q_index   = 0
        self.scores    = {}
        students       = self._load_students()
        self.students  = students
        self._render_projector()

    def _render_projector(self):
        for w in self.content.winfo_children():
            w.destroy()

        if not self.questions or self.q_index >= len(self.questions):
            self._end_session()
            return

        q     = self.questions[self.q_index]
        total = len(self.questions)

        # Top info bar
        info = ctk.CTkFrame(self.content, fg_color="#ffffff", height=40, corner_radius=0)
        info.pack(fill="x")
        info.pack_propagate(False)

        ctk.CTkLabel(
            info, text=f"  Question {self.q_index + 1} of {total}  ·  {self.session['topic']}",
            font=(FONT, 12), text_color=TEXT_SECONDARY
        ).pack(side="left", padx=16, pady=10)

        ctk.CTkButton(
            info, text="End Session ✕", width=110, height=28,
            fg_color="#fee2e2", text_color=DANGER,
            hover_color="#fecaca", font=(FONT, 11),
            command=self._end_session
        ).pack(side="right", padx=16, pady=6)

        # Main layout
        main = ctk.CTkFrame(self.content, fg_color=SURFACE)
        main.pack(fill="both", expand=True, padx=16, pady=16)
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)

        # Left — question card
        left = ctk.CTkFrame(main, fg_color="#ffffff", corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)

        q_num = ctk.CTkLabel(
            left, text=f"{self.q_index + 1} of {total}",
            font=(FONT, 13), text_color=MUTED
        )
        q_num.pack(anchor="w", padx=24, pady=(20, 8))

        ctk.CTkLabel(
            left, text=q,
            font=(FONT, 20, "bold"), text_color=TEXT_PRIMARY,
            wraplength=520, justify="center"
        ).pack(padx=24, pady=(0, 20))

        # Spinner — pick random student
        student = random.choice(self.students) if self.students else None
        if student:
            spin_frame = ctk.CTkFrame(left, fg_color="#1e1b4b", corner_radius=12)
            spin_frame.pack(fill="x", padx=24, pady=(0, 20))
            ctk.CTkLabel(
                spin_frame, text="CURRENTLY CALLING",
                font=(FONT, 10, "bold"), text_color="#a5b4fc"
            ).pack(pady=(14, 4))
            self.called_label = ctk.CTkLabel(
                spin_frame,
                text=f"{student['last_name']}, {student['first_name']}",
                font=(FONT, 22, "bold"), text_color="#ffffff"
            )
            self.called_label.pack(pady=(0, 14))
            self.current_student = student

            ctk.CTkButton(
                spin_frame, text="🔀 Spin Again",
                fg_color="transparent", hover_color="#312e81",
                text_color="#a5b4fc", font=(FONT, 12), height=32,
                command=self._respin
            ).pack(pady=(0, 10))

        # Score buttons
        score_frame = ctk.CTkFrame(left, fg_color="transparent")
        score_frame.pack(fill="x", padx=24, pady=(0, 20))

        for text, pts, color, hover in [
            ("👎  0 PTS",   0,  "#f1f5f9", "#e2e8f0"),
            ("😐  Half PTS", 5, "#fffbeb", "#fef3c7"),
            ("🔥  10 PTS",  10, "#f0fdf4", "#dcfce7"),
        ]:
            ctk.CTkButton(
                score_frame, text=text,
                fg_color=color, text_color=TEXT_PRIMARY,
                hover_color=hover, height=44,
                font=(FONT, 13), border_width=1,
                border_color="#e2e8f0",
                command=lambda p=pts: self._award_score(p)
            ).pack(side="left", expand=True, fill="x", padx=4)

        # Skip button
        ctk.CTkButton(
            left, text="Skip Question →",
            fg_color=SURFACE, text_color=MUTED,
            hover_color="#e2e8f0", height=36,
            font=(FONT, 12),
            command=self._next_question
        ).pack(padx=24, pady=(0, 16))

        # Right — leaderboard
        right = ctk.CTkFrame(main, fg_color="#ffffff", corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            right, text="Live Leaderboard",
            font=(FONT, 13, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16, pady=(16, 4))

        ctk.CTkFrame(
            right, fg_color=SUCCESS, height=2, corner_radius=0
        ).pack(fill="x", padx=16, pady=(0, 8))

        # Show top scorers
        sorted_scores = sorted(
            self.scores.items(), key=lambda x: -x[1]
        )

        for rank, (sid, pts) in enumerate(sorted_scores[:8], 1):
            s = next((st for st in self.students if st["id"] == sid), None)
            if not s:
                continue
            bg = "#fffbeb" if rank == 1 else "#ffffff"
            row = ctk.CTkFrame(right, fg_color=bg, corner_radius=8, height=36)
            row.pack(fill="x", padx=10, pady=2)
            row.pack_propagate(False)
            medal = "👑" if rank == 1 else str(rank)
            ctk.CTkLabel(
                row, text=f"{medal}  {s['last_name']}, {s['first_name']}",
                font=(FONT, 11), text_color=TEXT_PRIMARY,
                anchor="w"
            ).pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(
                row, text=f"{pts} pts",
                font=(FONT, 11, "bold"),
                text_color=PRIMARY if rank == 1 else TEXT_SECONDARY
            ).pack(side="right", padx=8)

    def _respin(self):
        student = random.choice(self.students)
        self.current_student = student
        self.called_label.configure(
            text=f"{student['last_name']}, {student['first_name']}"
        )

    def _award_score(self, pts: int):
        if hasattr(self, "current_student") and self.current_student:
            sid = self.current_student["id"]
            self.scores[sid] = self.scores.get(sid, 0) + pts
        self._next_question()

    def _next_question(self):
        self.q_index += 1
        self._render_projector()

    def _end_session(self):
        if self.session and self.scores:
            conn = self.db.connect()
            conn.execute(
                "UPDATE recitation_sessions SET scores=? WHERE id=?",
                (str(self.scores), self.session["id"])
            )
            conn.commit()
        self.session = None
        self._render_hub()

    def _load_sessions(self):
        rows = self.db.connect().execute(
            """SELECT r.*, s.name as subject_name
               FROM recitation_sessions r
               LEFT JOIN subjects s ON r.subject_id = s.id
               WHERE r.class_id=? ORDER BY r.created_at DESC""",
            (self.class_data["id"],)
        ).fetchall()
        return [dict(r) for r in rows]

    def _load_students(self):
        rows = self.db.connect().execute(
            "SELECT * FROM students WHERE class_id=? ORDER BY last_name",
            (self.class_data["id"],)
        ).fetchall()
        return [dict(r) for r in rows]

    def _load_subjects(self):
        rows = self.db.connect().execute(
            "SELECT * FROM subjects WHERE class_id=? ORDER BY name",
            (self.class_data["id"],)
        ).fetchall()
        return [dict(r) for r in rows]

    def _back(self):
        from app.ui.screens.class_hub import ClassHubScreen
        self.pack_forget()
        hub = ClassHubScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        hub.pack(fill="both", expand=True)
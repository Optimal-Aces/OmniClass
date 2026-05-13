import customtkinter as ctk
import uuid
from datetime import datetime
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT, DANGER, SUCCESS
)

class LessonLogsScreen(ctk.CTkFrame):
    def __init__(self, master, db, teacher: dict, class_data: dict, **kwargs):
        super().__init__(master, fg_color=SURFACE, **kwargs)
        self.db         = db
        self.teacher    = teacher
        self.class_data = class_data
        self.master     = master
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
            ("📓 Lesson Logs", None),
        ]:
            ctk.CTkButton(
                sidebar, text=f"  {label}", anchor="w",
                fg_color=PRIMARY if "Lesson" in label else "#1e2d45",
                hover_color="#3d5ce0" if "Lesson" in label else "#1e2d45",
                height=38, font=(FONT, 13),
                text_color="#ffffff" if "Lesson" in label else MUTED,
                command=cmd or (lambda: None)
            ).pack(fill="x", padx=12, pady=2)

        self.content = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)
        self._render()

    def _render(self):
        for w in self.content.winfo_children():
            w.destroy()

        # Top bar
        topbar = ctk.CTkFrame(self.content, fg_color="#ffffff", height=56, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkLabel(
            topbar, text="Daily Lesson Logs",
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            topbar, text="+ New Lesson Log",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            height=34, font=(FONT, 13),
            command=self._new_log_dialog
        ).pack(side="right", padx=24, pady=11)

        body = ctk.CTkScrollableFrame(self.content, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=24, pady=24)

        # Banner
        banner = ctk.CTkFrame(body, fg_color=SIDEBAR_BG, corner_radius=12, height=80)
        banner.pack(fill="x", pady=(0, 20))
        banner.pack_propagate(False)
        ctk.CTkLabel(
            banner, text="Daily Lesson Logs",
            font=(FONT, 17, "bold"), text_color="#ffffff"
        ).pack(anchor="w", padx=24, pady=(16, 2))
        ctk.CTkLabel(
            banner,
            text="Track topics, competencies, and hours taught per session.",
            font=(FONT, 12), text_color=MUTED
        ).pack(anchor="w", padx=24)

        # Search + filter row
        filter_row = ctk.CTkFrame(body, fg_color="transparent")
        filter_row.pack(fill="x", pady=(0, 12))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_logs(body))
        ctk.CTkEntry(
            filter_row,
            placeholder_text="Search topics or competencies...",
            textvariable=self.search_var,
            width=320, height=36
        ).pack(side="left")

        self.sub_filter_var = ctk.StringVar(value="All Subjects")
        subjects = ["All Subjects"] + [s["name"] for s in self._load_subjects()]
        ctk.CTkOptionMenu(
            filter_row,
            values=subjects,
            variable=self.sub_filter_var,
            width=180,
            command=lambda *a: self._refresh_logs(body)
        ).pack(side="left", padx=8)

        # Log archive table
        self.log_table = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
        self.log_table.pack(fill="both", expand=True)

        # Table header
        header = ctk.CTkFrame(self.log_table, fg_color="#f8fafc", height=36, corner_radius=0)
        header.pack(fill="x")
        for col, width, text in [
            (0, 120, "Date"),
            (1, 100, "Subject"),
            (2, 320, "Topic / Competency"),
            (3, 60,  "Hrs"),
            (4, 100, "Actions"),
        ]:
            ctk.CTkLabel(
                header, text=text,
                font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY,
                width=width, anchor="w"
            ).grid(row=0, column=col, padx=(12 if col == 0 else 4, 4), pady=8, sticky="w")

        self.rows_frame = ctk.CTkScrollableFrame(
            self.log_table, fg_color="#ffffff", corner_radius=0
        )
        self.rows_frame.pack(fill="both", expand=True)

        self._refresh_logs(body)

    def _refresh_logs(self, body=None):
        for w in self.rows_frame.winfo_children():
            w.destroy()

        query   = self.search_var.get().strip().lower()
        sub_flt = self.sub_filter_var.get()

        logs = self._load_logs()

        if query:
            logs = [l for l in logs if
                    query in l["topic"].lower() or
                    (l["competency"] and query in l["competency"].lower())]
        if sub_flt != "All Subjects":
            logs = [l for l in logs if l.get("subject_name") == sub_flt]

        if not logs:
            ctk.CTkLabel(
                self.rows_frame,
                text="No lesson logs yet.\nClick '+ New Lesson Log' to create one.",
                font=(FONT, 13), text_color=TEXT_SECONDARY, justify="center"
            ).pack(pady=40)
            return

        for i, log in enumerate(logs):
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            row = ctk.CTkFrame(self.rows_frame, fg_color=bg, height=44, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            dt = log["date"][:10] if log["date"] else "—"
            ctk.CTkLabel(
                row, text=dt,
                font=(FONT, 12), text_color=TEXT_SECONDARY,
                width=120, anchor="w"
            ).grid(row=0, column=0, padx=12, pady=10, sticky="w")

            sub_name = log.get("subject_name") or "—"
            sub_label = ctk.CTkLabel(
                row, text=sub_name,
                font=(FONT, 11, "bold"), text_color="#ffffff",
                width=90, anchor="center"
            )
            sub_label.grid(row=0, column=1, padx=4, pady=8, sticky="w")
            # Color pill background
            pill = ctk.CTkFrame(row, fg_color=PRIMARY, corner_radius=6, height=24, width=90)
            pill.grid(row=0, column=1, padx=4, pady=10, sticky="w")
            ctk.CTkLabel(
                pill, text=sub_name[:10],
                font=(FONT, 10, "bold"), text_color="#ffffff"
            ).pack(expand=True)

            ctk.CTkLabel(
                row, text=log["topic"],
                font=(FONT, 12), text_color=TEXT_PRIMARY,
                width=320, anchor="w"
            ).grid(row=0, column=2, padx=4, pady=10, sticky="w")

            ctk.CTkLabel(
                row, text=f"{log['hours_taught']}h",
                font=(FONT, 12), text_color=TEXT_SECONDARY,
                width=60, anchor="w"
            ).grid(row=0, column=3, padx=4, pady=10, sticky="w")

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=4, padx=4, pady=6)
            ctk.CTkButton(
                actions, text="View", width=48, height=26,
                fg_color=SURFACE, text_color=PRIMARY,
                hover_color="#e2e8f0", font=(FONT, 11),
                command=lambda l=log: self._view_log_dialog(l)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                actions, text="Del", width=40, height=26,
                fg_color=SURFACE, text_color=DANGER,
                hover_color="#fee2e2", font=(FONT, 11),
                command=lambda l=log: self._delete_log(l)
            ).pack(side="left", padx=2)

    def _new_log_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("New Lesson Log")
        dialog.geometry("520x580")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="New Lesson Log",
            font=(FONT, 16, "bold")
        ).pack(pady=(20, 16), padx=24, anchor="w")

        # Subject
        ctk.CTkLabel(dialog, text="Subject", font=(FONT, 12)).pack(anchor="w", padx=24)
        subjects = self._load_subjects()
        sub_names = [s["name"] for s in subjects]
        sub_var = ctk.StringVar(value=sub_names[0] if sub_names else "")
        ctk.CTkOptionMenu(
            dialog, values=sub_names if sub_names else ["No subjects"],
            variable=sub_var, width=470
        ).pack(padx=24, pady=(2, 10))

        # Date
        ctk.CTkLabel(dialog, text="Date", font=(FONT, 12)).pack(anchor="w", padx=24)
        date_e = ctk.CTkEntry(
            dialog, width=470, height=38,
            placeholder_text="YYYY-MM-DD"
        )
        date_e.insert(0, datetime.today().strftime("%Y-%m-%d"))
        date_e.pack(padx=24, pady=(2, 10))

        # Topic
        ctk.CTkLabel(dialog, text="Topic *", font=(FONT, 12)).pack(anchor="w", padx=24)
        topic_e = ctk.CTkEntry(
            dialog, placeholder_text="e.g. Pagsusulat para sa Pagtatrabaho",
            width=470, height=38
        )
        topic_e.pack(padx=24, pady=(2, 10))

        # Competency
        ctk.CTkLabel(dialog, text="Learning Competency", font=(FONT, 12)).pack(anchor="w", padx=24)
        comp_e = ctk.CTkEntry(
            dialog, placeholder_text="MELCs or learning competency...",
            width=470, height=38
        )
        comp_e.pack(padx=24, pady=(2, 10))

        # Hours
        ctk.CTkLabel(dialog, text="Hours Taught", font=(FONT, 12)).pack(anchor="w", padx=24)
        hours_e = ctk.CTkEntry(
            dialog, placeholder_text="e.g. 1.0",
            width=470, height=38
        )
        hours_e.insert(0, "1.0")
        hours_e.pack(padx=24, pady=(2, 10))

        # Objectives
        ctk.CTkLabel(dialog, text="Objectives / Notes", font=(FONT, 12)).pack(anchor="w", padx=24)
        obj_e = ctk.CTkTextbox(dialog, width=470, height=80)
        obj_e.pack(padx=24, pady=(2, 10))

        err = ctk.CTkLabel(dialog, text="", text_color=DANGER, font=(FONT, 11))
        err.pack()

        def save():
            topic = topic_e.get().strip()
            if not topic:
                err.configure(text="Topic is required.")
                return
            try:
                hours = float(hours_e.get().strip() or "1.0")
            except ValueError:
                err.configure(text="Invalid hours value.")
                return

            sub_id = None
            for s in subjects:
                if s["name"] == sub_var.get():
                    sub_id = s["id"]
                    break

            now = datetime.utcnow().isoformat()
            self.db.connect().execute(
                """INSERT INTO lesson_logs
                   (id, class_id, subject_id, date, topic, competency,
                    objectives, hours_taught, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (str(uuid.uuid4()), self.class_data["id"], sub_id,
                 date_e.get().strip(), topic,
                 comp_e.get().strip() or None,
                 obj_e.get("1.0", "end").strip() or None,
                 hours, now, now)
            )
            self.db.connect().commit()
            dialog.destroy()
            self._refresh_logs()

        ctk.CTkButton(
            dialog, text="Save Lesson Log",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            width=470, height=42, command=save
        ).pack(padx=24, pady=12)

    def _view_log_dialog(self, log: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Lesson Log")
        dialog.geometry("540x500")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=log["topic"],
            font=(FONT, 16, "bold"), wraplength=490
        ).pack(pady=(24, 4), padx=24, anchor="w")

        meta = f"{log['date'][:10]}  ·  {log.get('subject_name','—')}  ·  {log['hours_taught']}h"
        ctk.CTkLabel(
            dialog, text=meta,
            font=(FONT, 12), text_color=TEXT_SECONDARY
        ).pack(padx=24, anchor="w", pady=(0, 16))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color=SURFACE)
        scroll.pack(fill="both", expand=True, padx=16, pady=8)

        for section, content in [
            ("Learning Competency", log.get("competency")),
            ("Objectives / Notes",  log.get("objectives")),
        ]:
            if content:
                ctk.CTkLabel(
                    scroll, text=section,
                    font=(FONT, 12, "bold"), text_color=PRIMARY
                ).pack(anchor="w", pady=(8, 2))
                ctk.CTkLabel(
                    scroll, text=content,
                    font=(FONT, 12), text_color=TEXT_PRIMARY,
                    wraplength=480, justify="left"
                ).pack(anchor="w", padx=8)

        ctk.CTkButton(
            dialog, text="Close",
            fg_color=SURFACE, text_color=TEXT_SECONDARY,
            hover_color="#e2e8f0", height=38,
            command=dialog.destroy
        ).pack(padx=24, pady=12)

    def _delete_log(self, log: dict):
        from tkinter import messagebox
        if messagebox.askyesno("Delete", f"Delete log: '{log['topic']}'?"):
            self.db.connect().execute(
                "DELETE FROM lesson_logs WHERE id=?", (log["id"],)
            )
            self.db.connect().commit()
            self._refresh_logs()

    def _load_logs(self):
        rows = self.db.connect().execute(
            """SELECT l.*, s.name as subject_name
               FROM lesson_logs l
               LEFT JOIN subjects s ON l.subject_id = s.id
               WHERE l.class_id=?
               ORDER BY l.date DESC""",
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
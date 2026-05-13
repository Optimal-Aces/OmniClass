import customtkinter as ctk
import uuid
import json
from datetime import datetime
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT, DANGER, SUCCESS
)

class AssessmentsScreen(ctk.CTkFrame):
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
            ("← Class Hub",    self._back),
            ("📝 Assessments",  None),
        ]:
            ctk.CTkButton(
                sidebar, text=f"  {label}", anchor="w",
                fg_color=PRIMARY if "Assessments" in label else "#1e2d45",
                hover_color="#3d5ce0" if "Assessments" in label else "#1e2d45",
                height=38, font=(FONT, 13),
                text_color="#ffffff" if "Assessments" in label else MUTED,
                command=cmd or (lambda: None)
            ).pack(fill="x", padx=12, pady=2)

        self.content = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)
        self._render()

    def _render(self):
        for w in self.content.winfo_children():
            w.destroy()

        topbar = ctk.CTkFrame(self.content, fg_color="#ffffff", height=56, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkLabel(
            topbar, text="Assessments & TOS",
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            topbar, text="+ Create Assessment",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            height=34, font=(FONT, 13),
            command=self._create_dialog
        ).pack(side="right", padx=24, pady=11)

        body = ctk.CTkScrollableFrame(self.content, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=24, pady=24)

        # Banner
        banner = ctk.CTkFrame(body, fg_color="#1e1b4b", corner_radius=12, height=80)
        banner.pack(fill="x", pady=(0, 20))
        banner.pack_propagate(False)
        ctk.CTkLabel(
            banner, text="Test & TOS Bank",
            font=(FONT, 17, "bold"), text_color="#ffffff"
        ).pack(anchor="w", padx=24, pady=(16, 2))
        ctk.CTkLabel(
            banner,
            text="Create exams with auto-generated Table of Specifications.",
            font=(FONT, 12), text_color="#a5b4fc"
        ).pack(anchor="w", padx=24)

        # Archive table
        table = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
        table.pack(fill="both", expand=True)

        header = ctk.CTkFrame(table, fg_color="#f8fafc", height=36, corner_radius=0)
        header.pack(fill="x")
        for col, width, text in [
            (0, 120, "Date"),
            (1, 100, "Subject"),
            (2, 280, "Title"),
            (3, 70,  "Items"),
            (4, 70,  "Hours"),
            (5, 120, "Actions"),
        ]:
            ctk.CTkLabel(
                header, text=text,
                font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY,
                width=width, anchor="w"
            ).grid(row=0, column=col, padx=(12 if col == 0 else 4, 4), pady=8, sticky="w")

        assessments = self._load_assessments()

        rows_frame = ctk.CTkScrollableFrame(table, fg_color="#ffffff", corner_radius=0)
        rows_frame.pack(fill="both", expand=True)

        if not assessments:
            ctk.CTkLabel(
                rows_frame,
                text="No assessments yet.\nClick '+ Create Assessment' to get started.",
                font=(FONT, 13), text_color=TEXT_SECONDARY, justify="center"
            ).pack(pady=40)
            return

        for i, a in enumerate(assessments):
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            row = ctk.CTkFrame(rows_frame, fg_color=bg, height=44, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            ctk.CTkLabel(
                row, text=a["created_at"][:10],
                font=(FONT, 12), text_color=TEXT_SECONDARY,
                width=120, anchor="w"
            ).grid(row=0, column=0, padx=12, pady=10, sticky="w")

            pill = ctk.CTkFrame(row, fg_color="#4f46e5", corner_radius=6, height=24, width=90)
            pill.grid(row=0, column=1, padx=4, pady=10, sticky="w")
            ctk.CTkLabel(
                pill, text=(a.get("subject_name") or "—")[:10],
                font=(FONT, 10, "bold"), text_color="#ffffff"
            ).pack(expand=True)

            ctk.CTkLabel(
                row, text=a["title"],
                font=(FONT, 12), text_color=TEXT_PRIMARY,
                width=280, anchor="w"
            ).grid(row=0, column=2, padx=4, pady=10, sticky="w")

            ctk.CTkLabel(
                row, text=str(a["items"]),
                font=(FONT, 12), text_color=TEXT_SECONDARY,
                width=70, anchor="w"
            ).grid(row=0, column=3, padx=4, pady=10, sticky="w")

            ctk.CTkLabel(
                row, text=f"{a['hours']}h",
                font=(FONT, 12), text_color=TEXT_SECONDARY,
                width=70, anchor="w"
            ).grid(row=0, column=4, padx=4, pady=10, sticky="w")

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=5, padx=4, pady=6)
            ctk.CTkButton(
                actions, text="View", width=48, height=26,
                fg_color=SURFACE, text_color=PRIMARY,
                hover_color="#e2e8f0", font=(FONT, 11),
                command=lambda a=a: self._view_assessment(a)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                actions, text="Del", width=40, height=26,
                fg_color=SURFACE, text_color=DANGER,
                hover_color="#fee2e2", font=(FONT, 11),
                command=lambda a=a: self._delete_assessment(a)
            ).pack(side="left", padx=2)

    def _create_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create Assessment")
        dialog.geometry("500x500")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Create Assessment",
            font=(FONT, 16, "bold")
        ).pack(pady=(20, 16), padx=24, anchor="w")

        ctk.CTkLabel(dialog, text="Title *", font=(FONT, 12)).pack(anchor="w", padx=24)
        title_e = ctk.CTkEntry(
            dialog, placeholder_text="e.g. 1st Term Exam",
            width=450, height=38
        )
        title_e.pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Subject", font=(FONT, 12)).pack(anchor="w", padx=24)
        subjects  = self._load_subjects()
        sub_names = [s["name"] for s in subjects]
        sub_var   = ctk.StringVar(value=sub_names[0] if sub_names else "")
        ctk.CTkOptionMenu(
            dialog,
            values=sub_names if sub_names else ["No subjects"],
            variable=sub_var, width=450
        ).pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Number of Items", font=(FONT, 12)).pack(anchor="w", padx=24)
        items_e = ctk.CTkEntry(
            dialog, placeholder_text="e.g. 50",
            width=450, height=38
        )
        items_e.pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Question Types", font=(FONT, 12)).pack(anchor="w", padx=24)
        type_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        type_frame.pack(anchor="w", padx=24, pady=(2, 10))
        type_vars = {}
        for qtype in ["True or False", "Multiple Choice", "Identification", "Essay"]:
            var = ctk.BooleanVar(value=True)
            type_vars[qtype] = var
            ctk.CTkCheckBox(
                type_frame, text=qtype, variable=var,
                font=(FONT, 12)
            ).pack(side="left", padx=6)

        ctk.CTkLabel(dialog, text="Total Hours Taught", font=(FONT, 12)).pack(anchor="w", padx=24)
        hours_e = ctk.CTkEntry(
            dialog, placeholder_text="e.g. 6.0",
            width=450, height=38
        )
        hours_e.pack(padx=24, pady=(2, 10))

        err = ctk.CTkLabel(dialog, text="", text_color=DANGER, font=(FONT, 11))
        err.pack()

        def save():
            title = title_e.get().strip()
            if not title:
                err.configure(text="Title is required.")
                return
            try:
                items = int(items_e.get().strip() or "50")
                hours = float(hours_e.get().strip() or "1.0")
            except ValueError:
                err.configure(text="Invalid items or hours.")
                return

            sub_id = None
            for s in subjects:
                if s["name"] == sub_var.get():
                    sub_id = s["id"]
                    break

            selected_types = [t for t, v in type_vars.items() if v.get()]
            now = datetime.utcnow().isoformat()

            self.db.connect().execute(
                """INSERT INTO assessments
                   (id, class_id, subject_id, title, grade_level,
                    items, hours, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (str(uuid.uuid4()), self.class_data["id"], sub_id,
                 title, self.class_data["grade_level"],
                 items, hours, now, now)
            )
            self.db.connect().commit()
            dialog.destroy()
            self._render()

        ctk.CTkButton(
            dialog, text="Create Assessment",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            width=450, height=42, command=save
        ).pack(padx=24, pady=12)

    def _view_assessment(self, a: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title(a["title"])
        dialog.geometry("600x500")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=a["title"],
            font=(FONT, 16, "bold")
        ).pack(pady=(24, 4), padx=24, anchor="w")
        ctk.CTkLabel(
            dialog,
            text=f"Grade {a['grade_level']}  ·  {a.get('subject_name','—')}  ·  {a['items']} Items  ·  {a['hours']}h",
            font=(FONT, 12), text_color=TEXT_SECONDARY
        ).pack(padx=24, anchor="w", pady=(0, 16))

        # TOS table
        ctk.CTkLabel(
            dialog, text="Table of Specifications",
            font=(FONT, 13, "bold"), text_color=PRIMARY
        ).pack(anchor="w", padx=24, pady=(8, 4))

        tos_frame = ctk.CTkFrame(dialog, fg_color="#f8fafc", corner_radius=8)
        tos_frame.pack(fill="x", padx=24, pady=(0, 12))

        headers = ["Topic", "Hours", "%", "Items", "REM", "UND", "APP", "ANA", "EVA", "CRE"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(
                tos_frame, text=h,
                font=(FONT, 10, "bold"), text_color=TEXT_SECONDARY
            ).grid(row=0, column=col, padx=6, pady=6)

        # Auto-generate TOS from lesson logs
        logs  = self._get_logs_for_assessment(a)
        total_hours = sum(l["hours_taught"] for l in logs) or a["hours"]

        for row_i, log in enumerate(logs[:5], 1):
            pct   = log["hours_taught"] / total_hours
            items = round(pct * a["items"])
            for col, val in enumerate([
                log["topic"][:25],
                log["hours_taught"],
                f"{pct*100:.0f}%",
                items,
                round(items * 0.30),
                round(items * 0.25),
                round(items * 0.18),
                round(items * 0.12),
                round(items * 0.08),
                round(items * 0.07),
            ]):
                ctk.CTkLabel(
                    tos_frame, text=str(val),
                    font=(FONT, 10), text_color=TEXT_PRIMARY
                ).grid(row=row_i, column=col, padx=6, pady=4)

        ctk.CTkButton(
            dialog, text="Close",
            fg_color=SURFACE, text_color=TEXT_SECONDARY,
            hover_color="#e2e8f0", height=38,
            command=dialog.destroy
        ).pack(padx=24, pady=12)

    def _delete_assessment(self, a: dict):
        from tkinter import messagebox
        if messagebox.askyesno("Delete", f"Delete '{a['title']}'?"):
            self.db.connect().execute(
                "DELETE FROM assessments WHERE id=?", (a["id"],)
            )
            self.db.connect().commit()
            self._render()

    def _get_logs_for_assessment(self, a: dict):
        rows = self.db.connect().execute(
            """SELECT * FROM lesson_logs WHERE class_id=?
               AND (subject_id=? OR subject_id IS NULL)
               ORDER BY date DESC LIMIT 10""",
            (self.class_data["id"], a.get("subject_id"))
        ).fetchall()
        return [dict(r) for r in rows]

    def _load_assessments(self):
        rows = self.db.connect().execute(
            """SELECT a.*, s.name as subject_name
               FROM assessments a
               LEFT JOIN subjects s ON a.subject_id = s.id
               WHERE a.class_id=? ORDER BY a.created_at DESC""",
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
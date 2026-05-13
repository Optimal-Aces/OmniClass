import customtkinter as ctk
import uuid
from datetime import datetime
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT, DANGER, SUCCESS
)

class ProjectLabScreen(ctk.CTkFrame):
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
            ("🧪 Project Lab", None),
        ]:
            ctk.CTkButton(
                sidebar, text=f"  {label}", anchor="w",
                fg_color=PRIMARY if "Project" in label else "#1e2d45",
                hover_color="#3d5ce0" if "Project" in label else "#1e2d45",
                height=38, font=(FONT, 13),
                text_color="#ffffff" if "Project" in label else MUTED,
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
            topbar, text="Project Lab",
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            topbar, text="+ Design New Project",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            height=34, font=(FONT, 13),
            command=self._new_project_dialog
        ).pack(side="right", padx=24, pady=11)

        body = ctk.CTkScrollableFrame(self.content, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=24, pady=24)

        # Banner
        banner = ctk.CTkFrame(body, fg_color="#052e16", corner_radius=12, height=80)
        banner.pack(fill="x", pady=(0, 20))
        banner.pack_propagate(False)
        ctk.CTkLabel(
            banner, text="Project Lab",
            font=(FONT, 17, "bold"), text_color="#ffffff"
        ).pack(anchor="w", padx=24, pady=(16, 2))
        ctk.CTkLabel(
            banner,
            text="Design performance tasks, project briefs, and grading rubrics.",
            font=(FONT, 12), text_color="#86efac"
        ).pack(anchor="w", padx=24)

        # Archive table
        table = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
        table.pack(fill="both", expand=True)

        header = ctk.CTkFrame(table, fg_color="#f8fafc", height=36, corner_radius=0)
        header.pack(fill="x")
        for col, width, text in [
            (0, 120, "Date"),
            (1, 100, "Subject"),
            (2, 300, "Project Title"),
            (3, 90,  "Max Score"),
            (4, 120, "Actions"),
        ]:
            ctk.CTkLabel(
                header, text=text,
                font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY,
                width=width, anchor="w"
            ).grid(row=0, column=col, padx=(12 if col == 0 else 4, 4), pady=8, sticky="w")

        projects = self._load_projects()
        rows_frame = ctk.CTkScrollableFrame(table, fg_color="#ffffff", corner_radius=0)
        rows_frame.pack(fill="both", expand=True)

        if not projects:
            ctk.CTkLabel(
                rows_frame,
                text="No projects yet.\nClick '+ Design New Project' to create one.",
                font=(FONT, 13), text_color=TEXT_SECONDARY, justify="center"
            ).pack(pady=40)
            return

        for i, p in enumerate(projects):
            bg  = "#ffffff" if i % 2 == 0 else "#f8fafc"
            row = ctk.CTkFrame(rows_frame, fg_color=bg, height=44, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            ctk.CTkLabel(
                row, text=p["created_at"][:10],
                font=(FONT, 12), text_color=TEXT_SECONDARY,
                width=120, anchor="w"
            ).grid(row=0, column=0, padx=12, pady=10, sticky="w")

            pill = ctk.CTkFrame(row, fg_color="#166534", corner_radius=6, height=24, width=90)
            pill.grid(row=0, column=1, padx=4, pady=10, sticky="w")
            ctk.CTkLabel(
                pill, text=(p.get("subject_name") or "—")[:10],
                font=(FONT, 10, "bold"), text_color="#ffffff"
            ).pack(expand=True)

            ctk.CTkLabel(
                row, text=p["title"],
                font=(FONT, 12), text_color=TEXT_PRIMARY,
                width=300, anchor="w"
            ).grid(row=0, column=2, padx=4, pady=10, sticky="w")

            ctk.CTkLabel(
                row, text=f"{int(p['max_score'])} pts",
                font=(FONT, 12), text_color=TEXT_SECONDARY,
                width=90, anchor="w"
            ).grid(row=0, column=3, padx=4, pady=10, sticky="w")

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=4, padx=4, pady=6)
            ctk.CTkButton(
                actions, text="View", width=52, height=26,
                fg_color=SURFACE, text_color=PRIMARY,
                hover_color="#e2e8f0", font=(FONT, 11),
                command=lambda proj=p: self._view_project(proj)
            ).pack(side="left", padx=2)
            ctk.CTkButton(
                actions, text="Del", width=40, height=26,
                fg_color=SURFACE, text_color=DANGER,
                hover_color="#fee2e2", font=(FONT, 11),
                command=lambda proj=p: self._delete_project(proj)
            ).pack(side="left", padx=2)

    def _new_project_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("New Project")
        dialog.geometry("500x520")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Design New Project",
            font=(FONT, 16, "bold")
        ).pack(pady=(20, 16), padx=24, anchor="w")

        ctk.CTkLabel(dialog, text="Project Title *", font=(FONT, 12)).pack(anchor="w", padx=24)
        title_e = ctk.CTkEntry(
            dialog,
            placeholder_text="e.g. Mabisang Mensahe, Akmang Tono",
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

        ctk.CTkLabel(dialog, text="Max Score", font=(FONT, 12)).pack(anchor="w", padx=24)
        score_e = ctk.CTkEntry(
            dialog, placeholder_text="e.g. 100",
            width=450, height=38
        )
        score_e.insert(0, "100")
        score_e.pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Project Brief / Scenario", font=(FONT, 12)).pack(anchor="w", padx=24)
        brief_e = ctk.CTkTextbox(dialog, width=450, height=100)
        brief_e.pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Rubric Criteria", font=(FONT, 12)).pack(anchor="w", padx=24)
        rubric_e = ctk.CTkTextbox(dialog, width=450, height=80)
        rubric_e.insert("1.0", "Content (40%)\nDelivery (30%)\nOrganization (20%)\nLanguage (10%)")
        rubric_e.pack(padx=24, pady=(2, 10))

        err = ctk.CTkLabel(dialog, text="", text_color=DANGER, font=(FONT, 11))
        err.pack()

        def save():
            title = title_e.get().strip()
            if not title:
                err.configure(text="Title is required.")
                return
            try:
                max_score = float(score_e.get().strip() or "100")
            except ValueError:
                err.configure(text="Invalid max score.")
                return

            sub_id = None
            for s in subjects:
                if s["name"] == sub_var.get():
                    sub_id = s["id"]
                    break

            now = datetime.utcnow().isoformat()
            self.db.connect().execute(
                """INSERT INTO projects
                   (id, class_id, subject_id, title, max_score, brief, rubric,
                    created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (str(uuid.uuid4()), self.class_data["id"], sub_id,
                 title, max_score,
                 brief_e.get("1.0", "end").strip(),
                 rubric_e.get("1.0", "end").strip(),
                 now, now)
            )
            self.db.connect().commit()
            dialog.destroy()
            self._render()

        ctk.CTkButton(
            dialog, text="Save Project",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            width=450, height=42, command=save
        ).pack(padx=24, pady=12)

    def _view_project(self, p: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title(p["title"])
        dialog.geometry("560x560")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=p["title"],
            font=(FONT, 16, "bold"), wraplength=510
        ).pack(pady=(24, 4), padx=24, anchor="w")
        ctk.CTkLabel(
            dialog,
            text=f"{p.get('subject_name','—')}  ·  Max Score: {int(p['max_score'])} pts  ·  {p['created_at'][:10]}",
            font=(FONT, 12), text_color=TEXT_SECONDARY
        ).pack(padx=24, anchor="w", pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color=SURFACE)
        scroll.pack(fill="both", expand=True, padx=16, pady=8)

        for section, content in [
            ("📋 Project Brief / Scenario", p.get("brief")),
            ("📊 Rubric Criteria",           p.get("rubric")),
        ]:
            if content:
                ctk.CTkLabel(
                    scroll, text=section,
                    font=(FONT, 13, "bold"), text_color=PRIMARY
                ).pack(anchor="w", pady=(12, 4))
                box = ctk.CTkFrame(scroll, fg_color="#ffffff", corner_radius=8)
                box.pack(fill="x", padx=4, pady=(0, 8))
                ctk.CTkLabel(
                    box, text=content,
                    font=(FONT, 12), text_color=TEXT_PRIMARY,
                    wraplength=490, justify="left"
                ).pack(anchor="w", padx=12, pady=12)

        ctk.CTkButton(
            dialog, text="Close",
            fg_color=SURFACE, text_color=TEXT_SECONDARY,
            hover_color="#e2e8f0", height=38,
            command=dialog.destroy
        ).pack(padx=24, pady=12)

    def _delete_project(self, p: dict):
        from tkinter import messagebox
        if messagebox.askyesno("Delete", f"Delete '{p['title']}'?"):
            self.db.connect().execute(
                "DELETE FROM projects WHERE id=?", (p["id"],)
            )
            self.db.connect().commit()
            self._render()

    def _load_projects(self):
        rows = self.db.connect().execute(
            """SELECT p.*, s.name as subject_name
               FROM projects p
               LEFT JOIN subjects s ON p.subject_id = s.id
               WHERE p.class_id=? ORDER BY p.created_at DESC""",
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
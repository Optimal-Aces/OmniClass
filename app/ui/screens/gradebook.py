import customtkinter as ctk
import uuid
from datetime import datetime
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT, DANGER, SUCCESS, WARNING
)

class GradebookScreen(ctk.CTkFrame):
    def __init__(self, master, db, teacher: dict, class_data: dict, **kwargs):
        super().__init__(master, fg_color=SURFACE, **kwargs)
        self.db           = db
        self.teacher      = teacher
        self.class_data   = class_data
        self.master       = master
        self.selected_sub = None
        self.selected_term = "T1"
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
            sidebar, text=self.teacher.get("name", ""),
            font=(FONT, 12), text_color=MUTED
        ).pack(padx=20, anchor="w")
        ctk.CTkLabel(
            sidebar, text=self.class_data.get("name", ""),
            font=(FONT, 11), text_color="#475569"
        ).pack(padx=20, anchor="w", pady=(0, 16))

        ctk.CTkButton(
            sidebar, text="  ← Class Hub", anchor="w",
            fg_color="#1e2d45", hover_color="#1e2d45",
            height=38, font=(FONT, 13), text_color=MUTED,
            command=self._back
        ).pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(
            sidebar, text="SUBJECTS",
            font=(FONT, 10, "bold"), text_color="#475569"
        ).pack(anchor="w", padx=16, pady=(8, 4))

        self.sub_buttons = {}
        self.sub_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.sub_frame.pack(fill="x")
        self._render_subject_list()

        ctk.CTkButton(
            sidebar, text="+ Add Subject",
            fg_color="transparent", hover_color="#1e2d45",
            height=34, font=(FONT, 12), text_color=MUTED,
            border_width=1, border_color="#334155",
            command=self._add_subject_dialog
        ).pack(fill="x", padx=12, pady=12)

        # Main content
        self.content = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)
        self._show_select_prompt()

    def _render_subject_list(self):
        for w in self.sub_frame.winfo_children():
            w.destroy()
        subjects = self._load_subjects()
        for sub in subjects:
            is_sel = self.selected_sub and self.selected_sub["id"] == sub["id"]
            btn = ctk.CTkButton(
                self.sub_frame,
                text=f"  📊 {sub['name']}", anchor="w",
                fg_color=PRIMARY if is_sel else "transparent",
                hover_color="#3d5ce0" if is_sel else "#1e2d45",
                height=36, font=(FONT, 12),
                text_color="#ffffff" if is_sel else "#cbd5e1",
                command=lambda s=sub: self._select_subject(s)
            )
            btn.pack(fill="x", padx=12, pady=1)

    def _select_subject(self, sub: dict):
        self.selected_sub = sub
        self._render_subject_list()
        self._show_gradebook()

    def _show_select_prompt(self):
        for w in self.content.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.content,
            text="Select a subject from the sidebar\nor add a new one to get started.",
            font=(FONT, 14), text_color=TEXT_SECONDARY, justify="center"
        ).pack(expand=True)

    def _show_gradebook(self):
        for w in self.content.winfo_children():
            w.destroy()

        sub = self.selected_sub

        # Top bar
        topbar = ctk.CTkFrame(self.content, fg_color="#ffffff", height=56, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        ctk.CTkLabel(
            topbar, text=sub["name"],
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)

        # Term tabs
        term_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        term_frame.pack(side="left", padx=16, pady=12)
        for term in ["T1", "T2", "T3"]:
            is_sel = term == self.selected_term
            ctk.CTkButton(
                term_frame, text=term, width=42, height=30,
                fg_color=PRIMARY if is_sel else SURFACE,
                text_color="#ffffff" if is_sel else TEXT_SECONDARY,
                hover_color="#3d5ce0", font=(FONT, 12),
                command=lambda t=term: self._switch_term(t)
            ).pack(side="left", padx=2)

        ctk.CTkButton(
            topbar, text="+ Add Column",
            fg_color=SURFACE, text_color=PRIMARY,
            hover_color="#e2e8f0", height=32,
            font=(FONT, 12), border_width=1, border_color=PRIMARY,
            command=self._add_column_dialog
        ).pack(side="right", padx=8, pady=12)

        ctk.CTkButton(
            topbar, text="⚙ Settings",
            fg_color=SURFACE, text_color=TEXT_SECONDARY,
            hover_color="#e2e8f0", height=32,
            font=(FONT, 12),
            command=lambda: self._subject_settings_dialog(sub)
        ).pack(side="right", padx=4, pady=12)

        # Body
        body = ctk.CTkFrame(self.content, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=16, pady=16)

        # Category tabs
        cat_row = ctk.CTkFrame(body, fg_color="transparent")
        cat_row.pack(fill="x", pady=(0, 8))

        for cat, color, weight_key in [
            ("Written Works (WW)",       "#4f6ef7", "ww_weight"),
            ("Performance Tasks (PT)",   "#8b5cf6", "pt_weight"),
            ("Quarterly Assessment (QA)","#10b981", "qa_weight"),
        ]:
            pct = int(sub.get(weight_key, 0) * 100)
            ctk.CTkLabel(
                cat_row,
                text=f"● {cat} {pct}%",
                font=(FONT, 11, "bold"), text_color=color
            ).pack(side="left", padx=12)

        # Table
        table_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
        table_frame.pack(fill="both", expand=True)

        self._build_grade_table(table_frame, sub)

    def _build_grade_table(self, parent, sub: dict):
        students = self._load_students()
        columns  = self._load_columns(sub["id"], self.selected_term)

        if not students:
            ctk.CTkLabel(
                parent,
                text="No students enrolled.\nGo to Students module to add students.",
                font=(FONT, 13), text_color=TEXT_SECONDARY, justify="center"
            ).pack(expand=True, pady=40)
            return

        # Scrollable table
        scroll = ctk.CTkScrollableFrame(parent, fg_color="#ffffff", corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # Group columns by category
        ww_cols = [c for c in columns if c["category"] == "WW"]
        pt_cols = [c for c in columns if c["category"] == "PT"]
        qa_cols = [c for c in columns if c["category"] == "QA"]

        # Build header
        header = ctk.CTkFrame(scroll, fg_color="#f8fafc", height=36, corner_radius=0)
        header.pack(fill="x")

        col_idx = 0
        ctk.CTkLabel(
            header, text="Student Name",
            font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY,
            width=160, anchor="w"
        ).grid(row=0, column=col_idx, padx=8, pady=8, sticky="w")
        col_idx += 1

        for cat_cols, cat, color in [
            (ww_cols, "WW", "#4f6ef7"),
            (pt_cols, "PT", "#8b5cf6"),
            (qa_cols, "QA", "#10b981"),
        ]:
            for c in cat_cols:
                ctk.CTkLabel(
                    header,
                    text=f"{cat}{c['col_number']}",
                    font=(FONT, 10, "bold"), text_color=color,
                    width=48
                ).grid(row=0, column=col_idx, padx=2, pady=8)
                col_idx += 1
            if cat_cols:
                ctk.CTkLabel(
                    header, text="Total",
                    font=(FONT, 10, "bold"), text_color=TEXT_SECONDARY,
                    width=52
                ).grid(row=0, column=col_idx, padx=2, pady=8)
                col_idx += 1

        ctk.CTkLabel(
            header, text="Final",
            font=(FONT, 11, "bold"), text_color=TEXT_PRIMARY,
            width=56
        ).grid(row=0, column=col_idx, padx=4, pady=8)

        # Student rows
        for row_i, student in enumerate(students):
            bg = "#ffffff" if row_i % 2 == 0 else "#f8fafc"
            row_frame = ctk.CTkFrame(scroll, fg_color=bg, height=38, corner_radius=0)
            row_frame.pack(fill="x")

            col_idx = 0
            ctk.CTkLabel(
                row_frame,
                text=f"{student['last_name']}, {student['first_name']}",
                font=(FONT, 11), text_color=TEXT_PRIMARY,
                width=160, anchor="w"
            ).grid(row=0, column=col_idx, padx=8, pady=6, sticky="w")
            col_idx += 1

            ww_scores, pt_scores, qa_scores = [], [], []

            for cat_cols, scores_list, color in [
                (ww_cols, ww_scores, "#4f6ef7"),
                (pt_cols, pt_scores, "#8b5cf6"),
                (qa_cols, qa_scores, "#10b981"),
            ]:
                for c in cat_cols:
                    entry = self._get_entry(c["id"], student["id"])
                    score = entry["score"] if entry and entry["score"] is not None else None
                    scores_list.append((score, c["max_score"]))

                    e = ctk.CTkEntry(
                        row_frame, width=46, height=28,
                        font=(FONT, 11),
                        fg_color="#ffffff",
                        border_color=color, border_width=1
                    )
                    if score is not None:
                        e.insert(0, str(int(score) if score == int(score) else score))
                    e.grid(row=0, column=col_idx, padx=2, pady=4)

                    def on_change(event, col=c, sid=student["id"], entry_widget=e):
                        self._save_score(col, sid, entry_widget.get())

                    e.bind("<FocusOut>", on_change)
                    e.bind("<Return>", on_change)
                    col_idx += 1

                if cat_cols:
                    total = self._compute_total(scores_list)
                    total_color = SUCCESS if total and total >= 75 else DANGER if total else TEXT_SECONDARY
                    ctk.CTkLabel(
                        row_frame,
                        text=f"{total:.1f}" if total else "—",
                        font=(FONT, 11, "bold"), text_color=total_color,
                        width=52
                    ).grid(row=0, column=col_idx, padx=2)
                    col_idx += 1

            # Final grade
            final = self._compute_final(
                sub, ww_scores, pt_scores, qa_scores
            )
            final_color = SUCCESS if final and final >= 75 else DANGER if final else TEXT_SECONDARY
            ctk.CTkLabel(
                row_frame,
                text=f"{final:.1f}" if final else "—",
                font=(FONT, 12, "bold"), text_color=final_color,
                width=56
            ).grid(row=0, column=col_idx, padx=4)

    def _compute_total(self, scores: list) -> float:
        valid = [(s, m) for s, m in scores if s is not None and m]
        if not valid:
            return None
        total = sum(s for s, _ in valid)
        max_t = sum(m for _, m in valid)
        return (total / max_t) * 100 if max_t else None

    def _compute_final(self, sub, ww, pt, qa) -> float:
        ww_t = self._compute_total(ww)
        pt_t = self._compute_total(pt)
        qa_t = self._compute_total(qa)
        if ww_t is None and pt_t is None and qa_t is None:
            return None
        ww_t = ww_t or 0
        pt_t = pt_t or 0
        qa_t = qa_t or 0
        return (ww_t * sub["ww_weight"] +
                pt_t * sub["pt_weight"] +
                qa_t * sub["qa_weight"])

    def _save_score(self, col: dict, student_id: str, value: str):
        try:
            score = float(value) if value.strip() else None
        except ValueError:
            return
        conn = self.db.connect()
        now  = datetime.utcnow().isoformat()
        existing = conn.execute(
            "SELECT id FROM grade_entries WHERE column_id=? AND student_id=?",
            (col["id"], student_id)
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE grade_entries SET score=?, updated_at=? WHERE id=?",
                (score, now, existing["id"])
            )
        else:
            conn.execute(
                """INSERT INTO grade_entries
                   (id, column_id, student_id, score, created_at, updated_at)
                   VALUES (?,?,?,?,?,?)""",
                (str(uuid.uuid4()), col["id"], student_id, score, now, now)
            )
        conn.commit()

    def _add_column_dialog(self):
        if not self.selected_sub:
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Grade Column")
        dialog.geometry("360x280")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Add Grade Column",
            font=(FONT, 15, "bold")
        ).pack(pady=(20, 16), padx=24, anchor="w")

        ctk.CTkLabel(dialog, text="Category", font=(FONT, 12)).pack(anchor="w", padx=24)
        cat_var = ctk.StringVar(value="WW")
        ctk.CTkOptionMenu(
            dialog, values=["WW", "PT", "QA"],
            variable=cat_var, width=310
        ).pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Max Score", font=(FONT, 12)).pack(anchor="w", padx=24)
        max_entry = ctk.CTkEntry(dialog, placeholder_text="e.g. 50", width=310, height=38)
        max_entry.pack(padx=24, pady=(2, 10))

        err = ctk.CTkLabel(dialog, text="", text_color=DANGER, font=(FONT, 11))
        err.pack()

        def save():
            try:
                max_score = float(max_entry.get().strip() or "100")
            except ValueError:
                err.configure(text="Invalid max score.")
                return

            cat = cat_var.get()
            conn = self.db.connect()
            existing = conn.execute(
                "SELECT COUNT(*) as c FROM grade_columns WHERE subject_id=? AND term=? AND category=?",
                (self.selected_sub["id"], self.selected_term, cat)
            ).fetchone()["c"]

            conn.execute(
                """INSERT INTO grade_columns
                   (id, subject_id, term, category, col_number, max_score, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (str(uuid.uuid4()), self.selected_sub["id"],
                 self.selected_term, cat, existing + 1,
                 max_score, datetime.utcnow().isoformat())
            )
            conn.commit()
            dialog.destroy()
            self._show_gradebook()

        ctk.CTkButton(
            dialog, text="Add Column",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            width=310, height=40, command=save
        ).pack(padx=24, pady=8)

    def _add_subject_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Subject")
        dialog.geometry("400x380")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Add Subject",
            font=(FONT, 15, "bold")
        ).pack(pady=(20, 16), padx=24, anchor="w")

        ctk.CTkLabel(dialog, text="Subject Name *", font=(FONT, 12)).pack(anchor="w", padx=24)
        name_e = ctk.CTkEntry(dialog, placeholder_text="e.g. Filipino", width=350, height=38)
        name_e.pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Written Works %", font=(FONT, 12)).pack(anchor="w", padx=24)
        ww_e = ctk.CTkEntry(dialog, placeholder_text="40", width=350, height=38)
        ww_e.pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Performance Tasks %", font=(FONT, 12)).pack(anchor="w", padx=24)
        pt_e = ctk.CTkEntry(dialog, placeholder_text="40", width=350, height=38)
        pt_e.pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Quarterly Assessment %", font=(FONT, 12)).pack(anchor="w", padx=24)
        qa_e = ctk.CTkEntry(dialog, placeholder_text="20", width=350, height=38)
        qa_e.pack(padx=24, pady=(2, 10))

        err = ctk.CTkLabel(dialog, text="", text_color=DANGER, font=(FONT, 11))
        err.pack()

        def save():
            name = name_e.get().strip()
            if not name:
                err.configure(text="Subject name is required.")
                return
            try:
                ww = float(ww_e.get() or 40) / 100
                pt = float(pt_e.get() or 40) / 100
                qa = float(qa_e.get() or 20) / 100
            except ValueError:
                err.configure(text="Invalid weights.")
                return
            if abs(ww + pt + qa - 1.0) > 0.01:
                err.configure(text="Weights must add up to 100%.")
                return

            now = datetime.utcnow().isoformat()
            self.db.connect().execute(
                """INSERT INTO subjects
                   (id, class_id, name, ww_weight, pt_weight, qa_weight, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (str(uuid.uuid4()), self.class_data["id"],
                 name, ww, pt, qa, now, now)
            )
            self.db.connect().commit()
            dialog.destroy()
            self._render_subject_list()

        ctk.CTkButton(
            dialog, text="Add Subject",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            width=350, height=40, command=save
        ).pack(padx=24, pady=8)

    def _subject_settings_dialog(self, sub: dict):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Subject Settings")
        dialog.geometry("360x200")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text=f"Delete '{sub['name']}'?",
            font=(FONT, 14, "bold")
        ).pack(pady=(24, 8), padx=24, anchor="w")
        ctk.CTkLabel(
            dialog,
            text="This will delete all grade columns and entries for this subject.",
            font=(FONT, 11), text_color=TEXT_SECONDARY,
            wraplength=310, justify="left"
        ).pack(padx=24, anchor="w")

        ctk.CTkButton(
            dialog, text="Delete Subject",
            fg_color=DANGER, hover_color="#dc2626",
            width=310, height=40,
            command=lambda: self._delete_subject(sub, dialog)
        ).pack(padx=24, pady=20)

    def _delete_subject(self, sub: dict, dialog):
        conn = self.db.connect()
        cols = conn.execute(
            "SELECT id FROM grade_columns WHERE subject_id=?", (sub["id"],)
        ).fetchall()
        for c in cols:
            conn.execute("DELETE FROM grade_entries WHERE column_id=?", (c["id"],))
        conn.execute("DELETE FROM grade_columns WHERE subject_id=?", (sub["id"],))
        conn.execute("DELETE FROM subjects WHERE id=?", (sub["id"],))
        conn.commit()
        self.selected_sub = None
        dialog.destroy()
        self._render_subject_list()
        self._show_select_prompt()

    def _switch_term(self, term: str):
        self.selected_term = term
        self._show_gradebook()

    def _load_subjects(self):
        rows = self.db.connect().execute(
            "SELECT * FROM subjects WHERE class_id=? ORDER BY name",
            (self.class_data["id"],)
        ).fetchall()
        return [dict(r) for r in rows]

    def _load_students(self):
        rows = self.db.connect().execute(
            "SELECT * FROM students WHERE class_id=? ORDER BY last_name, first_name",
            (self.class_data["id"],)
        ).fetchall()
        return [dict(r) for r in rows]

    def _load_columns(self, subject_id: str, term: str):
        rows = self.db.connect().execute(
            "SELECT * FROM grade_columns WHERE subject_id=? AND term=? ORDER BY category, col_number",
            (subject_id, term)
        ).fetchall()
        return [dict(r) for r in rows]

    def _get_entry(self, column_id: str, student_id: str):
        row = self.db.connect().execute(
            "SELECT * FROM grade_entries WHERE column_id=? AND student_id=?",
            (column_id, student_id)
        ).fetchone()
        return dict(row) if row else None

    def _back(self):
        from app.ui.screens.class_hub import ClassHubScreen
        self.pack_forget()
        hub = ClassHubScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        hub.pack(fill="both", expand=True)
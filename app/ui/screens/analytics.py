import customtkinter as ctk
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT, DANGER, SUCCESS, WARNING
)

class AnalyticsScreen(ctk.CTkFrame):
    def __init__(self, master, db, teacher: dict, class_data: dict, **kwargs):
        super().__init__(master, fg_color=SURFACE, **kwargs)
        self.db         = db
        self.teacher    = teacher
        self.class_data = class_data
        self.master     = master
        self.selected_term = "T1"
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

        ctk.CTkButton(
            sidebar, text="  ← Class Hub", anchor="w",
            fg_color="#1e2d45", hover_color="#1e2d45",
            height=38, font=(FONT, 13), text_color=MUTED,
            command=self._back
        ).pack(fill="x", padx=12, pady=2)
        ctk.CTkButton(
            sidebar, text="  📈 Analytics", anchor="w",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            height=38, font=(FONT, 13), text_color="#ffffff",
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
            topbar, text="Academic Analytics",
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)

        term_frame = ctk.CTkFrame(topbar, fg_color="transparent")
        term_frame.pack(side="right", padx=24, pady=12)
        for term in ["T1", "T2", "T3"]:
            is_sel = term == self.selected_term
            ctk.CTkButton(
                term_frame, text=term, width=42, height=30,
                fg_color=PRIMARY if is_sel else SURFACE,
                text_color="#ffffff" if is_sel else TEXT_SECONDARY,
                hover_color="#3d5ce0", font=(FONT, 12),
                command=lambda t=term: self._switch_term(t)
            ).pack(side="left", padx=2)

        body = ctk.CTkScrollableFrame(self.content, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=24, pady=24)

        students  = self._load_students()
        subjects  = self._load_subjects()
        term      = self.selected_term

        if not students or not subjects:
            ctk.CTkLabel(
                body,
                text="No data yet.\nAdd students and subjects in the Gradebook first.",
                font=(FONT, 14), text_color=TEXT_SECONDARY, justify="center"
            ).pack(pady=60)
            return

        # Summary stats
        stats_frame = ctk.CTkFrame(body, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        averages   = self._compute_all_averages(students, subjects, term)
        class_avg  = sum(averages.values()) / len(averages) if averages else 0
        honors     = sum(1 for v in averages.values() if v >= 90)
        at_risk    = sum(1 for v in averages.values() if v < 75)

        for i, (label, value, color) in enumerate([
            ("Class Average",  f"{class_avg:.1f}" if class_avg else "—", PRIMARY),
            ("Honors (90+)",   str(honors),  SUCCESS),
            ("At Risk (<75)",  str(at_risk), DANGER),
            ("Total Students", str(len(students)), "#8b5cf6"),
        ]):
            card = ctk.CTkFrame(stats_frame, fg_color="#ffffff", corner_radius=10)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(
                card, text=value,
                font=(FONT, 26, "bold"), text_color=color
            ).pack(pady=(14, 2), padx=16, anchor="w")
            ctk.CTkLabel(
                card, text=label,
                font=(FONT, 11), text_color=TEXT_SECONDARY
            ).pack(pady=(0, 14), padx=16, anchor="w")

        # Subject Performance Index
        ctk.CTkLabel(
            body, text="Subject Performance Index",
            font=(FONT, 14, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))

        sub_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
        sub_frame.pack(fill="x", pady=(0, 20))

        sub_avgs = self._compute_subject_averages(students, subjects, term)
        if sub_avgs:
            max_avg = max(sub_avgs.values()) if sub_avgs else 100
            for sub_name, avg in sorted(sub_avgs.items(), key=lambda x: -x[1]):
                bar_pct = avg / 100
                color = SUCCESS if avg >= 90 else WARNING if avg >= 75 else DANGER

                row = ctk.CTkFrame(sub_frame, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=6)

                ctk.CTkLabel(
                    row, text=sub_name,
                    font=(FONT, 12), text_color=TEXT_PRIMARY,
                    width=160, anchor="w"
                ).pack(side="left")

                bar_bg = ctk.CTkFrame(row, fg_color="#f1f5f9", height=18, corner_radius=9)
                bar_bg.pack(side="left", fill="x", expand=True, padx=12)
                bar_bg.pack_propagate(False)

                bar_fill = ctk.CTkFrame(
                    bar_bg, fg_color=color,
                    height=18, corner_radius=9,
                    width=max(int(bar_pct * 300), 4)
                )
                bar_fill.place(x=0, y=0, relheight=1)

                ctk.CTkLabel(
                    row, text=f"{avg:.1f}",
                    font=(FONT, 12, "bold"), text_color=color,
                    width=48
                ).pack(side="right")
        else:
            ctk.CTkLabel(
                sub_frame, text="No grade data yet.",
                font=(FONT, 12), text_color=TEXT_SECONDARY
            ).pack(pady=20)

        # Grade Distribution
        ctk.CTkLabel(
            body, text="Grade Distribution",
            font=(FONT, 14, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))

        dist_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
        dist_frame.pack(fill="x", pady=(0, 20))

        buckets = {
            "90–100": (SUCCESS,  [v for v in averages.values() if v >= 90]),
            "85–89":  (PRIMARY,  [v for v in averages.values() if 85 <= v < 90]),
            "80–84":  ("#8b5cf6",[v for v in averages.values() if 80 <= v < 85]),
            "75–79":  (WARNING,  [v for v in averages.values() if 75 <= v < 80]),
            "Below 75":(DANGER,  [v for v in averages.values() if v < 75]),
        }

        dist_inner = ctk.CTkFrame(dist_frame, fg_color="transparent")
        dist_inner.pack(fill="x", padx=16, pady=16)

        for label, (color, vals) in buckets.items():
            count   = len(vals)
            pct     = count / len(averages) if averages else 0

            row = ctk.CTkFrame(dist_inner, fg_color="transparent")
            row.pack(fill="x", pady=4)

            ctk.CTkLabel(
                row, text=label,
                font=(FONT, 12), text_color=TEXT_PRIMARY, width=80, anchor="w"
            ).pack(side="left")

            bar_bg = ctk.CTkFrame(row, fg_color="#f1f5f9", height=18, corner_radius=9)
            bar_bg.pack(side="left", fill="x", expand=True, padx=12)
            bar_bg.pack_propagate(False)

            if pct > 0:
                ctk.CTkFrame(
                    bar_bg, fg_color=color,
                    height=18, corner_radius=9,
                    width=max(int(pct * 300), 4)
                ).place(x=0, y=0, relheight=1)

            ctk.CTkLabel(
                row, text=f"{count} student{'s' if count != 1 else ''}",
                font=(FONT, 11), text_color=TEXT_SECONDARY, width=90
            ).pack(side="right")

        # Intervention Watchlist
        ctk.CTkLabel(
            body, text="⚠ Intervention Watchlist",
            font=(FONT, 14, "bold"), text_color=DANGER
        ).pack(anchor="w", pady=(0, 8))

        watch_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
        watch_frame.pack(fill="x", pady=(0, 20))

        at_risk_students = [
            (sid, avg) for sid, avg in averages.items() if avg < 75
        ]

        if not at_risk_students:
            ctk.CTkLabel(
                watch_frame,
                text="✓ No students at risk. Great job!",
                font=(FONT, 13), text_color=SUCCESS
            ).pack(pady=20, padx=20)
        else:
            header = ctk.CTkFrame(watch_frame, fg_color="#fff1f2", corner_radius=0, height=32)
            header.pack(fill="x")
            for col, text, width in [
                (0, "Student",        200),
                (1, "Average",         80),
                (2, "Failed Subjects", 300),
            ]:
                ctk.CTkLabel(
                    header, text=text,
                    font=(FONT, 11, "bold"), text_color=DANGER,
                    width=width, anchor="w"
                ).grid(row=0, column=col, padx=12, pady=8, sticky="w")

            student_map = {s["id"]: s for s in students}
            for sid, avg in sorted(at_risk_students, key=lambda x: x[1]):
                s = student_map.get(sid)
                if not s:
                    continue
                failed = self._get_failed_subjects(sid, subjects, term)

                row = ctk.CTkFrame(watch_frame, fg_color="transparent", height=36)
                row.pack(fill="x")

                ctk.CTkLabel(
                    row,
                    text=f"{s['last_name']}, {s['first_name']}",
                    font=(FONT, 12), text_color=TEXT_PRIMARY,
                    width=200, anchor="w"
                ).grid(row=0, column=0, padx=12, pady=8, sticky="w")
                ctk.CTkLabel(
                    row, text=f"{avg:.1f}",
                    font=(FONT, 12, "bold"), text_color=DANGER,
                    width=80, anchor="w"
                ).grid(row=0, column=1, padx=12, sticky="w")
                ctk.CTkLabel(
                    row,
                    text=", ".join(failed) if failed else "—",
                    font=(FONT, 11), text_color=WARNING,
                    width=300, anchor="w"
                ).grid(row=0, column=2, padx=12, sticky="w")

        # Student ranking
        ctk.CTkLabel(
            body, text="Student Rankings",
            font=(FONT, 14, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 8))

        rank_frame = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
        rank_frame.pack(fill="x", pady=(0, 20))

        header2 = ctk.CTkFrame(rank_frame, fg_color="#f8fafc", height=32, corner_radius=0)
        header2.pack(fill="x")
        for col, text, width in [
            (0, "Rank", 50), (1, "Student", 220),
            (2, "Average", 90), (3, "Status", 100)
        ]:
            ctk.CTkLabel(
                header2, text=text,
                font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY,
                width=width, anchor="w"
            ).grid(row=0, column=col, padx=10, pady=8, sticky="w")

        student_map = {s["id"]: s for s in students}
        ranked = sorted(averages.items(), key=lambda x: -x[1])

        for rank, (sid, avg) in enumerate(ranked, 1):
            s = student_map.get(sid)
            if not s:
                continue
            bg = "#fffbeb" if rank <= 3 else "#ffffff" if rank % 2 == 0 else "#f8fafc"
            color = SUCCESS if avg >= 90 else WARNING if avg >= 75 else DANGER
            status = "Honors" if avg >= 90 else "Passed" if avg >= 75 else "At Risk"

            row = ctk.CTkFrame(rank_frame, fg_color=bg, height=36, corner_radius=0)
            row.pack(fill="x")

            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else str(rank)
            ctk.CTkLabel(
                row, text=medal,
                font=(FONT, 12), width=50, anchor="w"
            ).grid(row=0, column=0, padx=10, pady=8, sticky="w")
            ctk.CTkLabel(
                row,
                text=f"{s['last_name']}, {s['first_name']}",
                font=(FONT, 12), text_color=TEXT_PRIMARY,
                width=220, anchor="w"
            ).grid(row=0, column=1, padx=10, sticky="w")
            ctk.CTkLabel(
                row, text=f"{avg:.2f}",
                font=(FONT, 12, "bold"), text_color=color,
                width=90, anchor="w"
            ).grid(row=0, column=2, padx=10, sticky="w")
            ctk.CTkLabel(
                row, text=status,
                font=(FONT, 11), text_color=color,
                width=100, anchor="w"
            ).grid(row=0, column=3, padx=10, sticky="w")

    def _compute_all_averages(self, students, subjects, term) -> dict:
        averages = {}
        for s in students:
            grades = []
            for sub in subjects:
                cols = self._load_columns(sub["id"], term)
                ww = [(e["score"], c["max_score"]) for c in cols
                      if c["category"] == "WW"
                      for e in [self._get_entry(c["id"], s["id"])]
                      if e and e["score"] is not None]
                pt = [(e["score"], c["max_score"]) for c in cols
                      if c["category"] == "PT"
                      for e in [self._get_entry(c["id"], s["id"])]
                      if e and e["score"] is not None]
                qa = [(e["score"], c["max_score"]) for c in cols
                      if c["category"] == "QA"
                      for e in [self._get_entry(c["id"], s["id"])]
                      if e and e["score"] is not None]
                final = self._compute_final(sub, ww, pt, qa)
                if final is not None:
                    grades.append(final)
            if grades:
                averages[s["id"]] = sum(grades) / len(grades)
        return averages

    def _compute_subject_averages(self, students, subjects, term) -> dict:
        result = {}
        for sub in subjects:
            grades = []
            for s in students:
                cols = self._load_columns(sub["id"], term)
                ww = [(e["score"], c["max_score"]) for c in cols
                      if c["category"] == "WW"
                      for e in [self._get_entry(c["id"], s["id"])]
                      if e and e["score"] is not None]
                pt = [(e["score"], c["max_score"]) for c in cols
                      if c["category"] == "PT"
                      for e in [self._get_entry(c["id"], s["id"])]
                      if e and e["score"] is not None]
                qa = [(e["score"], c["max_score"]) for c in cols
                      if c["category"] == "QA"
                      for e in [self._get_entry(c["id"], s["id"])]
                      if e and e["score"] is not None]
                final = self._compute_final(sub, ww, pt, qa)
                if final is not None:
                    grades.append(final)
            if grades:
                result[sub["name"]] = sum(grades) / len(grades)
        return result

    def _get_failed_subjects(self, student_id, subjects, term) -> list:
        failed = []
        for sub in subjects:
            cols = self._load_columns(sub["id"], term)
            ww = [(e["score"], c["max_score"]) for c in cols
                  if c["category"] == "WW"
                  for e in [self._get_entry(c["id"], student_id)]
                  if e and e["score"] is not None]
            pt = [(e["score"], c["max_score"]) for c in cols
                  if c["category"] == "PT"
                  for e in [self._get_entry(c["id"], student_id)]
                  if e and e["score"] is not None]
            qa = [(e["score"], c["max_score"]) for c in cols
                  if c["category"] == "QA"
                  for e in [self._get_entry(c["id"], student_id)]
                  if e and e["score"] is not None]
            final = self._compute_final(sub, ww, pt, qa)
            if final is not None and final < 75:
                failed.append(f"{sub['name']} ({final:.0f})")
        return failed

    def _compute_final(self, sub, ww, pt, qa) -> float:
        def total(scores):
            valid = [(s, m) for s, m in scores if s is not None and m]
            if not valid:
                return None
            return (sum(s for s, _ in valid) / sum(m for _, m in valid)) * 100

        ww_t = total(ww)
        pt_t = total(pt)
        qa_t = total(qa)
        if ww_t is None and pt_t is None and qa_t is None:
            return None
        return ((ww_t or 0) * sub["ww_weight"] +
                (pt_t or 0) * sub["pt_weight"] +
                (qa_t or 0) * sub["qa_weight"])

    def _load_columns(self, subject_id, term):
        rows = self.db.connect().execute(
            "SELECT * FROM grade_columns WHERE subject_id=? AND term=?",
            (subject_id, term)
        ).fetchall()
        return [dict(r) for r in rows]

    def _get_entry(self, column_id, student_id):
        row = self.db.connect().execute(
            "SELECT * FROM grade_entries WHERE column_id=? AND student_id=?",
            (column_id, student_id)
        ).fetchone()
        return dict(row) if row else None

    def _load_students(self):
        rows = self.db.connect().execute(
            "SELECT * FROM students WHERE class_id=? ORDER BY last_name",
            (self.class_data["id"],)
        ).fetchall()
        return [dict(r) for r in rows]

    def _load_subjects(self):
        rows = self.db.connect().execute(
            "SELECT * FROM subjects WHERE class_id=?",
            (self.class_data["id"],)
        ).fetchall()
        return [dict(r) for r in rows]

    def _switch_term(self, term):
        self.selected_term = term
        self._render()

    def _back(self):
        from app.ui.screens.class_hub import ClassHubScreen
        self.pack_forget()
        hub = ClassHubScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        hub.pack(fill="both", expand=True)
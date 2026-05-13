import customtkinter as ctk
from datetime import datetime, date, timedelta
import calendar
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT, DANGER, SUCCESS, WARNING
)

class AttendanceScreen(ctk.CTkFrame):
    def __init__(self, master, db, teacher: dict, class_data: dict, **kwargs):
        super().__init__(master, fg_color=SURFACE, **kwargs)
        self.db         = db
        self.teacher    = teacher
        self.class_data = class_data
        self.master     = master
        self.current    = date.today().replace(day=1)
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
        ).pack(padx=20, anchor="w", pady=(0, 24))

        for label, cmd in [
            ("← Class Hub", self._back),
            ("📅 Attendance", None),
        ]:
            ctk.CTkButton(
                sidebar, text=f"  {label}", anchor="w",
                fg_color=PRIMARY if "Attendance" in label else "#1e2d45",
                hover_color="#3d5ce0" if "Attendance" in label else "#1e2d45",
                height=38, font=(FONT, 13),
                text_color="#ffffff" if "Attendance" in label else MUTED,
                command=cmd or (lambda: None)
            ).pack(fill="x", padx=12, pady=2)

        # Main content
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
            topbar, text="Attendance Tracker",
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)

        # Month nav
        nav = ctk.CTkFrame(topbar, fg_color="transparent")
        nav.pack(side="right", padx=24, pady=10)
        ctk.CTkButton(
            nav, text="← Prev", width=70, height=34,
            fg_color=SURFACE, text_color=TEXT_PRIMARY,
            hover_color="#e2e8f0", font=(FONT, 12),
            command=self._prev_month
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            nav, text="Today", width=60, height=34,
            fg_color=PRIMARY, hover_color="#3d5ce0",
            font=(FONT, 12),
            command=self._today
        ).pack(side="left", padx=2)
        ctk.CTkButton(
            nav, text="Next →", width=70, height=34,
            fg_color=SURFACE, text_color=TEXT_PRIMARY,
            hover_color="#e2e8f0", font=(FONT, 12),
            command=self._next_month
        ).pack(side="left", padx=2)

        body = ctk.CTkScrollableFrame(self.content, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=24, pady=24)

        # Month banner
        banner = ctk.CTkFrame(body, fg_color=SIDEBAR_BG, corner_radius=12, height=80)
        banner.pack(fill="x", pady=(0, 20))
        banner.pack_propagate(False)
        ctk.CTkLabel(
            banner,
            text=self.current.strftime("%B %Y"),
            font=(FONT, 22, "bold"), text_color="#ffffff"
        ).pack(anchor="w", padx=24, pady=(16, 0))
        ctk.CTkLabel(
            banner,
            text=f"Tracking attendance for {self.class_data['name']}",
            font=(FONT, 12), text_color=MUTED
        ).pack(anchor="w", padx=24)

        # Two column layout
        cols = ctk.CTkFrame(body, fg_color="transparent")
        cols.pack(fill="both", expand=True)
        cols.grid_columnconfigure(0, weight=3)
        cols.grid_columnconfigure(1, weight=1)

        # Calendar
        cal_frame = ctk.CTkFrame(cols, fg_color="#ffffff", corner_radius=12)
        cal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._build_calendar(cal_frame)

        # Alerts sidebar
        alert_frame = ctk.CTkFrame(cols, fg_color="transparent")
        alert_frame.grid(row=0, column=1, sticky="nsew")
        self._build_alerts(alert_frame)

    def _build_calendar(self, parent):
        # Day headers
        days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        header = ctk.CTkFrame(parent, fg_color="#f8fafc", corner_radius=0, height=32)
        header.pack(fill="x")
        header.pack_propagate(False)
        for i, d in enumerate(days):
            ctk.CTkLabel(
                header, text=d,
                font=(FONT, 10, "bold"), text_color=TEXT_SECONDARY,
                width=60
            ).grid(row=0, column=i, padx=4, pady=6)

        # Calendar grid
        grid = ctk.CTkFrame(parent, fg_color="#ffffff")
        grid.pack(fill="both", expand=True, padx=8, pady=8)

        year  = self.current.year
        month = self.current.month
        cal   = calendar.monthcalendar(year, month)
        today = date.today()

        # Get days that have attendance recorded
        recorded = self._get_recorded_days()

        for week_i, week in enumerate(cal):
            for day_i, day_num in enumerate(week):
                if day_num == 0:
                    ctk.CTkFrame(
                        grid, fg_color="transparent", width=60, height=60
                    ).grid(row=week_i, column=day_i, padx=3, pady=3)
                    continue

                d = date(year, month, day_num)
                is_today    = d == today
                is_recorded = day_num in recorded
                is_weekend  = day_i in (0, 6)
                is_future   = d > today

                if is_today:
                    bg, fg = PRIMARY, "#ffffff"
                elif is_recorded:
                    bg, fg = "#ede9fe", PRIMARY
                elif is_weekend or is_future:
                    bg, fg = "#f8fafc", MUTED
                else:
                    bg, fg = "#f1f5f9", TEXT_SECONDARY

                cell = ctk.CTkFrame(
                    grid, fg_color=bg, corner_radius=8, width=60, height=60
                )
                cell.grid(row=week_i, column=day_i, padx=3, pady=3, sticky="nsew")
                cell.pack_propagate(False)

                ctk.CTkLabel(
                    cell, text=str(day_num),
                    font=(FONT, 12, "bold" if is_today else "normal"),
                    text_color=fg
                ).pack(pady=(8, 0))

                if is_recorded:
                    ctk.CTkLabel(
                        cell, text="✓",
                        font=(FONT, 10), text_color=SUCCESS
                    ).pack()
                elif not is_weekend and not is_future:
                    btn = ctk.CTkButton(
                        cell, text="Mark",
                        font=(FONT, 9), height=20, width=44,
                        fg_color=PRIMARY, hover_color="#3d5ce0",
                        command=lambda dt=d: self._mark_attendance_dialog(dt)
                    )
                    btn.pack(pady=2)

    def _build_alerts(self, parent):
        # Absences alert
        absent_card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=12)
        absent_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            absent_card, text="⚠ 3+ Absences",
            font=(FONT, 12, "bold"), text_color=DANGER
        ).pack(anchor="w", padx=14, pady=(12, 6))

        absences = self._get_absence_alerts()
        if absences:
            for name, count in absences:
                row = ctk.CTkFrame(absent_card, fg_color="#fff1f2", corner_radius=6)
                row.pack(fill="x", padx=10, pady=2)
                ctk.CTkLabel(
                    row, text=name,
                    font=(FONT, 11), text_color=TEXT_PRIMARY
                ).pack(side="left", padx=8, pady=6)
                ctk.CTkLabel(
                    row, text=str(count),
                    font=(FONT, 11, "bold"), text_color=DANGER
                ).pack(side="right", padx=8)
        else:
            ctk.CTkLabel(
                absent_card, text="No alerts",
                font=(FONT, 11), text_color=MUTED
            ).pack(padx=14, pady=(0, 10))

        ctk.CTkFrame(absent_card, fg_color="transparent", height=8).pack()

        # Lates alert
        late_card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=12)
        late_card.pack(fill="x")

        ctk.CTkLabel(
            late_card, text="⏰ 6+ Lates",
            font=(FONT, 12, "bold"), text_color=WARNING
        ).pack(anchor="w", padx=14, pady=(12, 6))

        lates = self._get_late_alerts()
        if lates:
            for name, count in lates:
                row = ctk.CTkFrame(late_card, fg_color="#fffbeb", corner_radius=6)
                row.pack(fill="x", padx=10, pady=2)
                ctk.CTkLabel(
                    row, text=name,
                    font=(FONT, 11), text_color=TEXT_PRIMARY
                ).pack(side="left", padx=8, pady=6)
                ctk.CTkLabel(
                    row, text=str(count),
                    font=(FONT, 11, "bold"), text_color=WARNING
                ).pack(side="right", padx=8)
        else:
            ctk.CTkLabel(
                late_card, text="No alerts",
                font=(FONT, 11), text_color=MUTED
            ).pack(padx=14, pady=(0, 10))

        ctk.CTkFrame(late_card, fg_color="transparent", height=8).pack()

    def _mark_attendance_dialog(self, for_date: date):
        students = self.db.connect().execute(
            "SELECT * FROM students WHERE class_id=? ORDER BY last_name",
            (self.class_data["id"],)
        ).fetchall()

        if not students:
            from tkinter import messagebox
            messagebox.showinfo("No Students", "Add students first before marking attendance.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Attendance — {for_date.strftime('%B %d, %Y')}")
        dialog.geometry("460x520")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"Mark Attendance — {for_date.strftime('%b %d, %Y')}",
            font=(FONT, 15, "bold")
        ).pack(pady=(20, 4), padx=24, anchor="w")
        ctk.CTkLabel(
            dialog, text="Set status for each student",
            font=(FONT, 12), text_color=TEXT_SECONDARY
        ).pack(padx=24, anchor="w", pady=(0, 12))

        scroll = ctk.CTkScrollableFrame(dialog, fg_color=SURFACE)
        scroll.pack(fill="both", expand=True, padx=16, pady=8)

        status_vars = {}
        for s in students:
            existing = self.db.connect().execute(
                "SELECT status FROM attendance WHERE student_id=? AND date=?",
                (s["id"], str(for_date))
            ).fetchone()

            row = ctk.CTkFrame(scroll, fg_color="#ffffff", corner_radius=8)
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row,
                text=f"{s['last_name']}, {s['first_name']}",
                font=(FONT, 12), text_color=TEXT_PRIMARY, width=180, anchor="w"
            ).pack(side="left", padx=12, pady=8)

            var = ctk.StringVar(value=existing["status"] if existing else "present")
            status_vars[s["id"]] = var

            for status, color in [
                ("present", SUCCESS), ("absent", DANGER),
                ("late", WARNING), ("excused", "#8b5cf6")
            ]:
                ctk.CTkRadioButton(
                    row, text=status.capitalize(),
                    variable=var, value=status,
                    font=(FONT, 11),
                    fg_color=color, hover_color=color
                ).pack(side="left", padx=6)

        def save():
            conn = self.db.connect()
            now  = datetime.utcnow().isoformat()
            for student_id, var in status_vars.items():
                existing = conn.execute(
                    "SELECT id FROM attendance WHERE student_id=? AND date=?",
                    (student_id, str(for_date))
                ).fetchone()
                if existing:
                    conn.execute(
                        "UPDATE attendance SET status=?, updated_at=? WHERE id=?",
                        (var.get(), now, existing["id"])
                    )
                else:
                    conn.execute(
                        """INSERT INTO attendance
                           (id, class_id, student_id, date, status, created_at, updated_at)
                           VALUES (?,?,?,?,?,?,?)""",
                        (str(uuid.uuid4()) if True else "",
                         self.class_data["id"], student_id,
                         str(for_date), var.get(), now, now)
                    )
            conn.commit()
            dialog.destroy()
            self._render()

        import uuid
        ctk.CTkButton(
            dialog, text="Save Attendance",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            height=42, font=(FONT, 13), command=save
        ).pack(fill="x", padx=24, pady=12)

    def _get_recorded_days(self) -> set:
        year, month = self.current.year, self.current.month
        rows = self.db.connect().execute(
            """SELECT DISTINCT date FROM attendance
               WHERE class_id=? AND date LIKE ?""",
            (self.class_data["id"], f"{year}-{month:02d}-%")
        ).fetchall()
        return {int(r["date"].split("-")[2]) for r in rows}

    def _get_absence_alerts(self):
        rows = self.db.connect().execute(
            """SELECT s.last_name || ', ' || s.first_name as name,
                      COUNT(*) as cnt
               FROM attendance a JOIN students s ON a.student_id = s.id
               WHERE a.class_id=? AND a.status='absent'
               GROUP BY a.student_id HAVING cnt >= 3
               ORDER BY cnt DESC""",
            (self.class_data["id"],)
        ).fetchall()
        return [(r["name"], r["cnt"]) for r in rows]

    def _get_late_alerts(self):
        rows = self.db.connect().execute(
            """SELECT s.last_name || ', ' || s.first_name as name,
                      COUNT(*) as cnt
               FROM attendance a JOIN students s ON a.student_id = s.id
               WHERE a.class_id=? AND a.status='late'
               GROUP BY a.student_id HAVING cnt >= 6
               ORDER BY cnt DESC""",
            (self.class_data["id"],)
        ).fetchall()
        return [(r["name"], r["cnt"]) for r in rows]

    def _prev_month(self):
        self.current = (self.current.replace(day=1) - timedelta(days=1)).replace(day=1)
        self._render()

    def _next_month(self):
        last = calendar.monthrange(self.current.year, self.current.month)[1]
        self.current = (self.current.replace(day=last) + timedelta(days=1)).replace(day=1)
        self._render()

    def _today(self):
        self.current = date.today().replace(day=1)
        self._render()

    def _back(self):
        from app.ui.screens.class_hub import ClassHubScreen
        self.pack_forget()
        hub = ClassHubScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        hub.pack(fill="both", expand=True)
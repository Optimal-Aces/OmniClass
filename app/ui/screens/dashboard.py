import customtkinter as ctk
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, BORDER,
    TEXT_PRIMARY, TEXT_SECONDARY, MUTED, FONT
)

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, db, teacher: dict, **kwargs):
        super().__init__(master, fg_color=SURFACE, **kwargs)
        self.db      = db
        self.teacher = teacher
        self.master  = master
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
            sidebar, text=self.teacher.get("school", ""),
            font=(FONT, 11), text_color="#475569"
        ).pack(padx=20, anchor="w", pady=(0, 24))

        # Sidebar nav items
        nav_items = [
            ("Dashboard",    "🏠", self._show_dashboard),
        ]
        for label, icon, cmd in nav_items:
            btn = ctk.CTkButton(
                sidebar, text=f"  {icon}  {label}",
                anchor="w", fg_color=PRIMARY,
                hover_color="#3d5ce0", height=38,
                font=(FONT, 13), command=cmd
            )
            btn.pack(fill="x", padx=12, pady=2)

        # Sign out at bottom
        ctk.CTkButton(
            sidebar, text="  🚪  Sign Out",
            anchor="w", fg_color="transparent",
            hover_color="#1e2d45", height=38,
            text_color=MUTED, font=(FONT, 13),
            command=self._sign_out
        ).pack(fill="x", padx=12, pady=2, side="bottom")

        # Main content area
        self.content = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        self._show_dashboard()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_dashboard(self):
        self._clear_content()

        # Top bar
        topbar = ctk.CTkFrame(self.content, fg_color="#ffffff", height=56, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkLabel(
            topbar, text="Overview",
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            topbar, text="+ New Class",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            height=34, font=(FONT, 13),
            command=self._new_class_dialog
        ).pack(side="right", padx=24, pady=11)

        # Scrollable body
        body = ctk.CTkScrollableFrame(self.content, fg_color=SURFACE)
        body.pack(fill="both", expand=True, padx=24, pady=24)

        # Banner
        banner = ctk.CTkFrame(body, fg_color=SIDEBAR_BG, corner_radius=12, height=90)
        banner.pack(fill="x", pady=(0, 20))
        banner.pack_propagate(False)
        ctk.CTkLabel(
            banner,
            text=f"Welcome back, {self.teacher.get('name', 'Teacher')}! 👋",
            font=(FONT, 17, "bold"), text_color="#ffffff"
        ).pack(anchor="w", padx=24, pady=(20, 2))
        ctk.CTkLabel(
            banner, text="Here are your active classes.",
            font=(FONT, 12), text_color=MUTED
        ).pack(anchor="w", padx=24)

        # Classes
        classes = self._load_classes()

        if not classes:
            empty = ctk.CTkFrame(body, fg_color="#ffffff", corner_radius=12)
            empty.pack(fill="x", pady=8)
            ctk.CTkLabel(
                empty,
                text="No classes yet.\nClick '+ New Class' to create your first section.",
                font=(FONT, 13), text_color=TEXT_SECONDARY,
                justify="center"
            ).pack(pady=40)
        else:
            ctk.CTkLabel(
                body, text="Your Classes",
                font=(FONT, 14, "bold"), text_color=TEXT_PRIMARY
            ).pack(anchor="w", pady=(0, 10))

            grid = ctk.CTkFrame(body, fg_color="transparent")
            grid.pack(fill="x")

            for i, cls in enumerate(classes):
                self._class_card(grid, cls, i)

    def _class_card(self, parent, cls, index):
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=12)
        card.grid(row=index // 3, column=index % 3, padx=6, pady=6, sticky="nsew")
        parent.grid_columnconfigure(index % 3, weight=1)

        # Color bar on top
        bar = ctk.CTkFrame(card, fg_color=PRIMARY, height=4, corner_radius=0)
        bar.pack(fill="x")

        ctk.CTkLabel(
            card,
            text=f"SY {cls['school_year']}",
            font=(FONT, 10), text_color=MUTED
        ).pack(anchor="w", padx=16, pady=(10, 0))
        ctk.CTkLabel(
            card, text=cls["name"],
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(anchor="w", padx=16)

        ctk.CTkLabel(
            card,
            text=f"Grade {cls['grade_level']}  ·  {cls['term']}",
            font=(FONT, 11), text_color=TEXT_SECONDARY
        ).pack(anchor="w", padx=16, pady=(2, 10))

        # Student count
        count = self._student_count(cls["id"])
        ctk.CTkLabel(
            card, text=f"👥 {count} Students",
            font=(FONT, 12), text_color=TEXT_SECONDARY
        ).pack(anchor="w", padx=16, pady=(0, 12))

        ctk.CTkButton(
            card, text="Open →",
            fg_color=SURFACE, text_color=PRIMARY,
            hover_color="#e2e8f0", height=32,
            font=(FONT, 12),
            command=lambda c=cls: self._open_class(c)
        ).pack(fill="x", padx=16, pady=(0, 12))

    def _load_classes(self):
        conn = self.db.connect()
        rows = conn.execute(
            "SELECT * FROM classes WHERE teacher_id = ? AND is_archived = 0 ORDER BY created_at DESC",
            (self.teacher["id"],)
        ).fetchall()
        return [dict(r) for r in rows]

    def _student_count(self, class_id: str) -> int:
        conn = self.db.connect()
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM students WHERE class_id = ?", (class_id,)
        ).fetchone()
        return row["cnt"] if row else 0

    def _new_class_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("New Class")
        dialog.geometry("420x480")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="Create New Class",
            font=(FONT, 16, "bold")
        ).pack(pady=(24, 16), padx=24, anchor="w")

        fields = {}

        for label, key, placeholder in [
            ("Section Name", "name", "e.g. Section Rizal"),
            ("School Year",  "sy",   "e.g. 2025-2026"),
        ]:
            ctk.CTkLabel(dialog, text=label, font=(FONT, 12)).pack(anchor="w", padx=24)
            e = ctk.CTkEntry(dialog, placeholder_text=placeholder, width=370, height=40)
            e.pack(padx=24, pady=(2, 10))
            fields[key] = e

        ctk.CTkLabel(dialog, text="Grade Level", font=(FONT, 12)).pack(anchor="w", padx=24)
        grade_var = ctk.StringVar(value="5")
        grade_menu = ctk.CTkOptionMenu(
            dialog, values=[str(i) for i in range(1, 13)],
            variable=grade_var, width=370
        )
        grade_menu.pack(padx=24, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Term", font=(FONT, 12)).pack(anchor="w", padx=24)
        term_var = ctk.StringVar(value="Full Year")
        term_menu = ctk.CTkOptionMenu(
            dialog,
            values=["Full Year", "1st Semester", "2nd Semester", "T1", "T2", "T3"],
            variable=term_var, width=370
        )
        term_menu.pack(padx=24, pady=(2, 10))

        err = ctk.CTkLabel(dialog, text="", text_color="#ef4444", font=(FONT, 11))
        err.pack()

        def save():
            name = fields["name"].get().strip()
            sy   = fields["sy"].get().strip()
            if not name or not sy:
                err.configure(text="Please fill in all fields.")
                return
            import uuid
            from datetime import datetime
            conn = self.db.connect()
            conn.execute(
                """INSERT INTO classes (id, teacher_id, name, grade_level, school_year, term, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), self.teacher["id"], name,
                 int(grade_var.get()), sy, term_var.get(),
                 datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
            )
            conn.commit()
            dialog.destroy()
            self._show_dashboard()

        ctk.CTkButton(
            dialog, text="Create Class",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            width=370, height=42, command=save
        ).pack(padx=24, pady=16)

    def _open_class(self, cls: dict):
        from app.ui.screens.class_hub import ClassHubScreen
        self.pack_forget()
        hub = ClassHubScreen(self.master, self.db, teacher=self.teacher, class_data=cls)
        hub.pack(fill="both", expand=True)

    def _sign_out(self):
        from app.ui.screens.login import LoginScreen
        self.pack_forget()
        login = LoginScreen(self.master, self.db)
        login.pack(fill="both", expand=True)
import customtkinter as ctk
import bcrypt
import uuid
import re
from datetime import datetime
from tkinter import messagebox
from app.ui.styles.theme import SIDEBAR_BG, PRIMARY, MUTED

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, fg_color=SIDEBAR_BG, **kwargs)
        self.db = db
        self.master = master
        self._mode = "login"
        self._build()

    def _build(self):
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(expand=True)
        self._render()

    def _clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def _render(self):
        self._clear()

        ctk.CTkLabel(
            self.container, text="OmniClass",
            font=("Segoe UI", 32, "bold"), text_color="#ffffff"
        ).pack(pady=(0, 6))
        ctk.CTkLabel(
            self.container,
            text="Classroom management for Filipino teachers",
            font=("Segoe UI", 13), text_color=MUTED
        ).pack(pady=(0, 36))

        if self._mode == "register":
            self.name_entry = ctk.CTkEntry(
                self.container, placeholder_text="Full name",
                width=320, height=44
            )
            self.name_entry.pack(pady=5)

            self.school_entry = ctk.CTkEntry(
                self.container, placeholder_text="School name",
                width=320, height=44
            )
            self.school_entry.pack(pady=5)

        self.email_entry = ctk.CTkEntry(
            self.container, placeholder_text="Email address",
            width=320, height=44
        )
        self.email_entry.pack(pady=5)

        self.password_entry = ctk.CTkEntry(
            self.container, placeholder_text="Password",
            show="*", width=320, height=44
        )
        self.password_entry.pack(pady=5)

        if self._mode == "register":
            self.confirm_entry = ctk.CTkEntry(
                self.container, placeholder_text="Confirm password",
                show="*", width=320, height=44
            )
            self.confirm_entry.pack(pady=5)

        self.error_label = ctk.CTkLabel(
            self.container, text="", text_color="#ef4444",
            font=("Segoe UI", 12)
        )
        self.error_label.pack(pady=(4, 0))

        if self._mode == "login":
            ctk.CTkButton(
                self.container, text="Sign In",
                width=320, height=44,
                fg_color=PRIMARY, hover_color="#3d5ce0",
                command=self._sign_in
            ).pack(pady=12)
            ctk.CTkButton(
                self.container, text="Create account",
                width=320, height=36,
                fg_color="transparent", border_width=1,
                border_color="#334155", text_color=MUTED,
                hover_color="#1e2d45",
                command=self._switch_to_register
            ).pack()
        else:
            ctk.CTkButton(
                self.container, text="Create Account",
                width=320, height=44,
                fg_color=PRIMARY, hover_color="#3d5ce0",
                command=self._create_account
            ).pack(pady=12)
            ctk.CTkButton(
                self.container, text="Back to Sign In",
                width=320, height=36,
                fg_color="transparent", border_width=1,
                border_color="#334155", text_color=MUTED,
                hover_color="#1e2d45",
                command=self._switch_to_login
            ).pack()

    def _switch_to_register(self):
        self._mode = "register"
        self._render()

    def _switch_to_login(self):
        self._mode = "login"
        self._render()

    def _show_error(self, msg: str):
        self.error_label.configure(text=msg)

    def _sign_in(self):
        email    = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email or not password:
            self._show_error("Please fill in all fields.")
            return

        conn = self.db.connect()
        row  = conn.execute(
            "SELECT * FROM teachers WHERE email = ?", (email,)
        ).fetchone()

        if not row:
            self._show_error("No account found with that email.")
            return

        if not bcrypt.checkpw(password.encode(), row["password"].encode()):
            self._show_error("Incorrect password.")
            return

        self._go_to_dashboard(dict(row))

    def _create_account(self):
        name     = self.name_entry.get().strip()
        school   = self.school_entry.get().strip()
        email    = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm  = self.confirm_entry.get()

        if not all([name, email, password, confirm]):
            self._show_error("Please fill in all required fields.")
            return

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self._show_error("Please enter a valid email address.")
            return

        if len(password) < 6:
            self._show_error("Password must be at least 6 characters.")
            return

        if password != confirm:
            self._show_error("Passwords do not match.")
            return

        conn = self.db.connect()
        existing = conn.execute(
            "SELECT id FROM teachers WHERE email = ?", (email,)
        ).fetchone()

        if existing:
            self._show_error("An account with that email already exists.")
            return

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        teacher_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        conn.execute(
            """INSERT INTO teachers (id, name, email, school, password, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (teacher_id, name, email, school, hashed, now, now)
        )
        conn.commit()

        self._go_to_dashboard({
            "id": teacher_id, "name": name,
            "email": email, "school": school
        })

    def _go_to_dashboard(self, teacher: dict):
        from app.ui.screens.dashboard import DashboardScreen
        self.pack_forget()
        dash = DashboardScreen(self.master, self.db, teacher=teacher)
        dash.pack(fill="both", expand=True)
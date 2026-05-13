import customtkinter as ctk
import uuid
from datetime import datetime
from app.ui.styles.theme import (
    PRIMARY, SIDEBAR_BG, SURFACE, MUTED,
    TEXT_PRIMARY, TEXT_SECONDARY, FONT, DANGER
)

class StudentProfileScreen(ctk.CTkFrame):
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
            sidebar, text=self.teacher.get("name", ""),
            font=(FONT, 12), text_color=MUTED
        ).pack(padx=20, anchor="w")
        ctk.CTkLabel(
            sidebar, text=self.class_data.get("name", ""),
            font=(FONT, 11), text_color="#475569"
        ).pack(padx=20, anchor="w", pady=(0, 24))

        for label, cmd in [
            ("← Class Hub", self._back),
            ("👥 Students",  None),
        ]:
            ctk.CTkButton(
                sidebar, text=f"  {label}", anchor="w",
                fg_color=PRIMARY if label.endswith("Students") else "#1e2d45",
                hover_color="#3d5ce0" if label.endswith("Students") else "#1e2d45",
                height=38, font=(FONT, 13),
                text_color="#ffffff" if label.endswith("Students") else MUTED,
                command=cmd or (lambda: None)
            ).pack(fill="x", padx=12, pady=2)

        # Main content
        self.content = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)
        self._show_roster()

    def _show_roster(self):
        for w in self.content.winfo_children():
            w.destroy()

        # Top bar
        topbar = ctk.CTkFrame(self.content, fg_color="#ffffff", height=56, corner_radius=0)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        ctk.CTkLabel(
            topbar, text="Students",
            font=(FONT, 16, "bold"), text_color=TEXT_PRIMARY
        ).pack(side="left", padx=24, pady=16)
        ctk.CTkButton(
            topbar, text="+ Add Student",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            height=34, font=(FONT, 13),
            command=self._add_student_dialog
        ).pack(side="right", padx=24, pady=11)

        # Search bar
        search_frame = ctk.CTkFrame(self.content, fg_color=SURFACE)
        search_frame.pack(fill="x", padx=24, pady=(16, 0))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._refresh_table())
        ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by name or LRN...",
            textvariable=self.search_var,
            width=340, height=38
        ).pack(side="left")

        # Count label
        self.count_label = ctk.CTkLabel(
            search_frame, text="",
            font=(FONT, 12), text_color=TEXT_SECONDARY
        )
        self.count_label.pack(side="left", padx=16)

        # Table frame
        table_container = ctk.CTkFrame(self.content, fg_color="#ffffff", corner_radius=12)
        table_container.pack(fill="both", expand=True, padx=24, pady=16)

        # Table header
        header = ctk.CTkFrame(table_container, fg_color="#f8fafc", corner_radius=0, height=36)
        header.pack(fill="x")
        header.pack_propagate(False)

        for col, width, text in [
            (0, 40,  "#"),
            (1, 180, "Last Name"),
            (2, 160, "First Name"),
            (3, 140, "LRN"),
            (4, 80,  "Sex"),
            (5, 160, "Guardian"),
            (6, 120, "Actions"),
        ]:
            ctk.CTkLabel(
                header, text=text,
                font=(FONT, 11, "bold"), text_color=TEXT_SECONDARY,
                width=width, anchor="w"
            ).grid(row=0, column=col, padx=(12 if col == 0 else 4, 4), pady=8, sticky="w")

        # Scrollable rows
        self.table_body = ctk.CTkScrollableFrame(
            table_container, fg_color="#ffffff", corner_radius=0
        )
        self.table_body.pack(fill="both", expand=True)

        self._refresh_table()

    def _refresh_table(self):
        for w in self.table_body.winfo_children():
            w.destroy()

        query = self.search_var.get().strip().lower()
        conn  = self.db.connect()
        rows  = conn.execute(
            "SELECT * FROM students WHERE class_id = ? ORDER BY last_name, first_name",
            (self.class_data["id"],)
        ).fetchall()

        students = [dict(r) for r in rows]
        if query:
            students = [
                s for s in students
                if query in s["last_name"].lower()
                or query in s["first_name"].lower()
                or (s["lrn"] and query in s["lrn"].lower())
            ]

        self.count_label.configure(text=f"{len(students)} student{'s' if len(students) != 1 else ''}")

        if not students:
            ctk.CTkLabel(
                self.table_body,
                text="No students found.\nClick '+ Add Student' to enroll students.",
                font=(FONT, 13), text_color=TEXT_SECONDARY, justify="center"
            ).pack(pady=40)
            return

        for i, s in enumerate(students):
            bg = "#ffffff" if i % 2 == 0 else "#f8fafc"
            row_frame = ctk.CTkFrame(self.table_body, fg_color=bg, height=40, corner_radius=0)
            row_frame.pack(fill="x")
            row_frame.pack_propagate(False)

            for col, width, value in [
                (0, 40,  str(i + 1)),
                (1, 180, s["last_name"]),
                (2, 160, s["first_name"]),
                (3, 140, s["lrn"] or "—"),
                (4, 80,  s["sex"] or "—"),
                (5, 160, s["guardian_name"] or "—"),
            ]:
                ctk.CTkLabel(
                    row_frame, text=value,
                    font=(FONT, 12), text_color=TEXT_PRIMARY,
                    width=width, anchor="w"
                ).grid(row=0, column=col, padx=(12 if col == 0 else 4, 4), pady=8, sticky="w")

            # Action buttons
            actions = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions.grid(row=0, column=6, padx=4, pady=4, sticky="w")

            ctk.CTkButton(
                actions, text="Edit", width=50, height=26,
                fg_color=SURFACE, text_color=PRIMARY,
                hover_color="#e2e8f0", font=(FONT, 11),
                command=lambda st=s: self._edit_student_dialog(st)
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                actions, text="Del", width=44, height=26,
                fg_color=SURFACE, text_color=DANGER,
                hover_color="#fee2e2", font=(FONT, 11),
                command=lambda st=s: self._delete_student(st)
            ).pack(side="left", padx=2)

    def _add_student_dialog(self):
        self._student_dialog()

    def _edit_student_dialog(self, student: dict):
        self._student_dialog(student)

    def _student_dialog(self, student: dict = None):
        is_edit = student is not None
        dialog  = ctk.CTkToplevel(self)
        dialog.title("Edit Student" if is_edit else "Add Student")
        dialog.geometry("440x560")
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Edit Student" if is_edit else "Add Student",
            font=(FONT, 16, "bold")
        ).pack(pady=(24, 16), padx=24, anchor="w")

        fields = {}
        field_defs = [
            ("Last Name *",       "last_name",        "e.g. Dela Cruz"),
            ("First Name *",      "first_name",       "e.g. Juan"),
            ("Middle Name",       "middle_name",      "optional"),
            ("LRN",               "lrn",              "12-digit LRN"),
            ("Guardian Name",     "guardian_name",    "Parent or guardian"),
            ("Emergency Contact", "emergency_contact","Phone number"),
        ]

        for label, key, placeholder in field_defs:
            ctk.CTkLabel(dialog, text=label, font=(FONT, 12)).pack(anchor="w", padx=24)
            e = ctk.CTkEntry(dialog, placeholder_text=placeholder, width=390, height=38)
            if is_edit and student.get(key):
                e.insert(0, student[key])
            e.pack(padx=24, pady=(2, 8))
            fields[key] = e

        ctk.CTkLabel(dialog, text="Sex", font=(FONT, 12)).pack(anchor="w", padx=24)
        sex_var = ctk.StringVar(value=student.get("sex", "Male") if is_edit else "Male")
        ctk.CTkOptionMenu(
            dialog, values=["Male", "Female"],
            variable=sex_var, width=390
        ).pack(padx=24, pady=(2, 8))

        err = ctk.CTkLabel(dialog, text="", text_color=DANGER, font=(FONT, 11))
        err.pack()

        def save():
            last  = fields["last_name"].get().strip()
            first = fields["first_name"].get().strip()
            if not last or not first:
                err.configure(text="Last name and first name are required.")
                return

            conn = self.db.connect()
            now  = datetime.utcnow().isoformat()

            if is_edit:
                conn.execute(
                    """UPDATE students SET last_name=?, first_name=?, middle_name=?,
                       lrn=?, guardian_name=?, emergency_contact=?, sex=?, updated_at=?
                       WHERE id=?""",
                    (last, first,
                     fields["middle_name"].get().strip() or None,
                     fields["lrn"].get().strip() or None,
                     fields["guardian_name"].get().strip() or None,
                     fields["emergency_contact"].get().strip() or None,
                     sex_var.get(), now, student["id"])
                )
            else:
                conn.execute(
                    """INSERT INTO students
                       (id, class_id, last_name, first_name, middle_name,
                        lrn, guardian_name, emergency_contact, sex, created_at, updated_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (str(uuid.uuid4()), self.class_data["id"],
                     last, first,
                     fields["middle_name"].get().strip() or None,
                     fields["lrn"].get().strip() or None,
                     fields["guardian_name"].get().strip() or None,
                     fields["emergency_contact"].get().strip() or None,
                     sex_var.get(), now, now)
                )
            conn.commit()
            dialog.destroy()
            self._refresh_table()

        ctk.CTkButton(
            dialog,
            text="Save Changes" if is_edit else "Add Student",
            fg_color=PRIMARY, hover_color="#3d5ce0",
            width=390, height=42, command=save
        ).pack(padx=24, pady=12)

    def _delete_student(self, student: dict):
        from tkinter import messagebox
        if messagebox.askyesno(
            "Delete Student",
            f"Delete {student['last_name']}, {student['first_name']}?\nThis cannot be undone."
        ):
            self.db.connect().execute(
                "DELETE FROM students WHERE id=?", (student["id"],)
            )
            self.db.connect().commit()
            self._refresh_table()

    def _back(self):
        from app.ui.screens.class_hub import ClassHubScreen
        self.pack_forget()
        hub = ClassHubScreen(
            self.master, self.db,
            teacher=self.teacher, class_data=self.class_data
        )
        hub.pack(fill="both", expand=True)
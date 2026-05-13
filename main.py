"""
TeachCRM — Desktop classroom management for Filipino teachers
Entry point
"""
import customtkinter as ctk
from app.core.dao.database import Database
from app.core.sync.sync_manager import SyncManager
from app.ui.screens.login import LoginScreen

def main():
    db = Database()
    db.initialize()

    sync = SyncManager(db)
    sync.start()

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("OmniClass")
    app.geometry("1280x800")
    app.minsize(1024, 680)

    app.protocol("WM_DELETE_WINDOW", lambda: (sync.stop(), db.close(), app.destroy()))

    login = LoginScreen(app, db)
    login.pack(fill="both", expand=True)

    app.mainloop()

if __name__ == "__main__":
    main()
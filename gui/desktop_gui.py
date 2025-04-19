import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from servermaster import core

class ServerMasterGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ServerMaster Desktop UI")
        self.geometry("800x600")
        self.configure(bg="#2b2b2b")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#2b2b2b")
        self.style.configure("TLabel", background="#2b2b2b", foreground="white")
        self.style.configure("TButton", background="#3c3f41", foreground="white")
        self.style.configure("TCheckbutton", background="#2b2b2b", foreground="white")

        self.server_list = core.scan_servers()
        self.config = core.load_config()

        self.server_frames = {}
        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        for server_path in self.server_list:
            name = server_path.name
            frame = ttk.LabelFrame(self, text=name)
            frame.pack(fill="x", padx=10, pady=5)

            running = core.is_running(name)
            players = core.get_players(server_path)
            modded = self.config.get(name, {}).get("modded", False)

            ttk.Label(frame, text=f"Status: {'Running' if running else 'Stopped'}").pack(anchor="w")
            ttk.Label(frame, text=f"Players: {', '.join(players) if players else 'None'}").pack(anchor="w")

            btn_start = ttk.Button(frame, text="Start", command=lambda p=server_path: self.start_server(p))
            btn_start.pack(side="left", padx=5)

            btn_stop = ttk.Button(frame, text="Stop", command=lambda n=name: self.stop_server(n))
            btn_stop.pack(side="left", padx=5)

            ram_var = tk.StringVar()
            core_var = tk.StringVar()

            ttk.Entry(frame, textvariable=ram_var, width=5).pack(side="left")
            ttk.Entry(frame, textvariable=core_var, width=5).pack(side="left")

            ttk.Button(frame, text="Apply JVM", command=lambda p=server_path, r=ram_var, c=core_var: self.apply_jvm(p, r.get(), c.get())).pack(side="left", padx=5)

            mod_var = tk.BooleanVar(value=modded)
            mod_check = ttk.Checkbutton(frame, text="Modded", variable=mod_var, command=lambda n=name, v=mod_var: self.toggle_modded(n, v))
            mod_check.pack(side="left")

            ttk.Button(frame, text="View Mods", command=lambda p=server_path: self.view_mods(p)).pack(side="left", padx=5)

            self.server_frames[name] = frame

    def start_server(self, path):
        core.start_server(path)
        self.refresh()

    def stop_server(self, name):
        core.stop_server_by_name(name)
        self.refresh()

    def apply_jvm(self, path, ram, cores):
        core.update_jvm_args(path, ram, cores)
        messagebox.showinfo("JVM Updated", "JVM arguments updated successfully.")

    def toggle_modded(self, name, var):
        core.toggle_modded(name, var.get())
        self.refresh()

    def view_mods(self, path):
        mods = core.get_mods(path)
        messagebox.showinfo("Mods", "\n".join(mods) if mods else "No mods found.")

    def refresh(self):
        self.server_list = core.scan_servers()
        self.config = core.load_config()
        self.build_ui()

if __name__ == "__main__":
    app = ServerMasterGUI()
    app.mainloop()

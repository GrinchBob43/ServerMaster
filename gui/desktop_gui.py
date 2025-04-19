import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from servermaster import core
import threading
import socket
import subprocess
import os

root = tk.Tk()

# --- INIT ---
root = tk.Tk()
root.title("ServerMaster Desktop UI")
root.geometry("800x600")
root.configure(bg="#2e2e2e")

# --- STYLING ---
style = ttk.Style()
style.theme_use("alt")

style.configure(".", 
    background="#2e2e2e", 
    foreground="#ffffff", 
    font=("Segoe UI", 10)
)
style.configure("TButton", 
    background="#444", 
    foreground="white", 
    padding=6,
    relief="flat"
)
style.map("TButton",
    background=[("active", "#666")],
    relief=[("pressed", "sunken")]
)
style.configure("TLabel", background="#2e2e2e", foreground="#dddddd")
style.configure("TCheckbutton", background="#2e2e2e", foreground="white")
style.configure("TFrame", background="#2e2e2e")


# --- 🔧 AUTO-LAUNCH WEB API ---

def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0

def launch_web_api():
    if not is_port_open("127.0.0.1", 5000):
        subprocess.Popen(["python3", "-m", "web.api"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Fire up the web API as a background process
threading.Thread(target=launch_web_api, daemon=True).start()


main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

header = ttk.Label(main_frame, text="ServerMaster", font=("Segoe UI", 18, "bold"))
header.pack(pady=(0, 20))

server_frame = ttk.Frame(main_frame)
server_frame.pack(fill="x", expand=True)

def refresh_servers():
    for widget in server_frame.winfo_children():
        widget.destroy()
    servers = core.scan_servers()
    for path in servers:
        name = path.name
        running = core.is_running(name)
        modded = core.load_config().get(name, {}).get("modded", False)
        players = core.get_players(path)
        mods = core.get_mods(path) if modded else []

        status_text = "[ONLINE]" if running else "[OFFLINE]"
        status_color = "lightgreen" if running else "gray"
        label = ttk.Label(server_frame, text=f"{name} {status_text}", foreground=status_color)
        label.pack(anchor="w")

        btn_frame = ttk.Frame(server_frame)
        btn_frame.pack(fill="x", pady=5)

        ttk.Button(btn_frame, text="Start", command=lambda p=path: core.start_server(p)).pack(side="left")
        ttk.Button(btn_frame, text="Stop", command=lambda n=name: core.stop_server_by_name(n)).pack(side="left")
        ttk.Button(btn_frame, text="Open Folder", command=lambda p=path: subprocess.run(["xdg-open", str(p)])).pack(side="left")
        ttk.Button(btn_frame, text="Open in Web UI", command=lambda: webbrowser.open("http://localhost:5000")).pack(side="left")

        var = tk.BooleanVar(value=modded)
        toggle = ttk.Checkbutton(btn_frame, text="Modded", variable=var, 
                                 command=lambda n=name, v=var: core.toggle_modded(n, v.get()))
        toggle.pack(side="left")

        if players:
            ttk.Label(btn_frame, text=f"Players: {', '.join(players)}").pack(side="left", padx=10)
        if mods:
            ttk.Label(btn_frame, text=f"Mods: {len(mods)}").pack(side="left", padx=10)

refresh_button = ttk.Button(main_frame, text="🔄 Refresh", command=refresh_servers)
refresh_button.pack(pady=10)

refresh_servers()
root.mainloop()



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

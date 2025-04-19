import os
import json
import subprocess
from pathlib import Path
import psutil

SERVER_DIR = str(Path.home() / "Mc_servers")
CONFIG_PATH = Path(__file__).parent / "config.json"

def scan_servers():
    return [f for f in Path(SERVER_DIR).iterdir() if (f / "start.sh").exists()]

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

def is_running(name):
    result = subprocess.run(["tmux", "ls"], capture_output=True, text=True)
    return name in result.stdout

def start_server(path):
    name = path.name
    if is_running(name):
        return
    subprocess.run(["tmux", "new-session", "-d", "-s", name, "./start.sh"], cwd=path)

def stop_server_by_name(name):
    subprocess.run(["tmux", "kill-session", "-t", name])

def get_players(path):
    logs = path / "logs/latest.log"
    if not logs.exists():
        return []
    with open(logs, "r", errors="ignore") as f:
        lines = f.readlines()
    players = set()
    for line in lines[-50:]:
        if "joined the game" in line:
            players.add(line.split()[3])
        if "left the game" in line:
            players.discard(line.split()[3])
    return list(players)

def toggle_modded(name, state):
    cfg = load_config()
    if name not in cfg:
        cfg[name] = {}
    cfg[name]["modded"] = state
    save_config(cfg)

def update_jvm_args(path, ram=None, cores=None):
    script_path = path / "start.sh"
    if not script_path.exists():
        return
    with open(script_path, "r") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if "-Xmx" in line and "java" in line:
            parts = line.split()
            new_parts = []
            for p in parts:
                if p.startswith("-Xmx") and ram:
                    new_parts.append(f"-Xmx{ram}G")
                elif p.startswith("-XX:ActiveProcessorCount") and cores:
                    new_parts.append(f"-XX:ActiveProcessorCount={cores}")
                else:
                    new_parts.append(p)
            lines[i] = " ".join(new_parts) + "\n"
            break
    with open(script_path, "w") as f:
        f.writelines(lines)

def get_mods(path):
    mods_dir = path / "mods"
    if not mods_dir.exists():
        return []
    return [f.name for f in mods_dir.iterdir() if f.suffix == ".jar"]
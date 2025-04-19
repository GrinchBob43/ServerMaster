from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os

from servermaster import core

app = Flask(__name__)
CORS(app)

@app.route("/api/servers", methods=["GET"])
def list_servers():
    servers = []
    for path in core.scan_servers():
        name = path.name
        running = core.is_running(name)
        players = core.get_players(path)
        mods = core.get_mods(path)
        modded = core.load_config().get(name, {}).get("modded", False)
        servers.append({
            "name": name,
            "running": running,
            "players": players,
            "modded": modded,
            "mods": mods
        })
    return jsonify(servers)

@app.route("/api/server/<name>/start", methods=["POST"])
def start_server(name):
    path = Path(core.SERVER_DIR) / name
    if not path.exists():
        return jsonify({"error": "Server not found"}), 404
    core.start_server(path)
    return jsonify({"status": "started"})

@app.route("/api/server/<name>/stop", methods=["POST"])
def stop_server(name):
    core.stop_server_by_name(name)
    return jsonify({"status": "stopped"})

@app.route("/api/server/<name>/toggle_modded", methods=["POST"])
def toggle_modded(name):
    data = request.json
    state = data.get("state", False)
    core.toggle_modded(name, state)
    return jsonify({"modded": state})

@app.route("/api/server/<name>/jvm", methods=["POST"])
def update_jvm(name):
    data = request.json
    ram = data.get("ram")   # Integer in GB
    cores = data.get("cores")  # Integer
    path = Path(core.SERVER_DIR) / name
    if not path.exists():
        return jsonify({"error": "Server not found"}), 404
    core.update_jvm_args(path, ram=ram, cores=cores)
    return jsonify({"status": "jvm updated"})

@app.route("/api/server/<name>/mods", methods=["GET"])
def list_mods(name):
    path = Path(core.SERVER_DIR) / name
    return jsonify(core.get_mods(path))

@app.route("/api/server/<name>/mods", methods=["POST"])
def upload_mod(name):
    path = Path(core.SERVER_DIR) / name / "mods"
    if not path.exists():
        path.mkdir(parents=True)
    if "mod" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["mod"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    dest = path / file.filename
    file.save(str(dest))
    return jsonify({"status": "uploaded", "mod": file.filename})

@app.route("/api/server/<name>/mods/<mod_name>", methods=["DELETE"])
def delete_mod(name, mod_name):
    path = Path(core.SERVER_DIR) / name / "mods" / mod_name
    if path.exists():
        os.remove(path)
        return jsonify({"status": "deleted", "mod": mod_name})
    return jsonify({"error": "Mod not found"}), 404

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "ServerMaster API running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


# ServerMaster

ServerMaster is a cross-platform management tool for Minecraft servers running on a Linux-based system. It allows users to easily start, stop, configure, and monitor Minecraft server instances from a unified interface.

## Features

- **Server Management:**
  - Automatically scans the `Mc_servers` directory for server folders.
  - Start and stop servers using `tmux` for process isolation.
  - View the current players on each server by parsing `latest.log`.
  - Update JVM arguments (RAM allocation, CPU cores).
  
- **Mod Management:**
  - Toggle "uses mods" flag for each server.
  - View and manage server mods stored in the `mods` directory.
  
- **GUI:**
  - A desktop UI for managing Minecraft servers using `tkinter` with a dark mode toggle (default).

- **Web API:**
  - A Flask-based web API for managing servers remotely.

## Requirements

- Python 3.6+
- `tmux`
- Dependencies:
  - Flask
  - Flask-Cors
  - psutil

To install dependencies, run:

```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ServerMaster.git
   cd ServerMaster
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Minecraft servers:
   - Place each server in the `~/Mc_servers` directory.
   - Ensure each server has a `start.sh` script for starting the server.

4. To run the **Desktop UI**:
   ```bash
   python3 -m gui.desktop_gui
   ```

5. To access the **Web UI**, run:
   ```bash
   python3 -m web.api
   ```

## Usage

### Desktop UI:
- The desktop UI allows you to start, stop, and configure your servers.
- Toggle "modded" status and manage JVM arguments (RAM/cores).
- Monitor player activity on each server.

### Web API:
- **GET** `/api/servers`: Get a list of all servers.
- **POST** `/api/server/<name>/start`: Start a specific server.
- **POST** `/api/server/<name>/stop`: Stop a specific server.
- **POST** `/api/server/<name>/toggle_modded`: Toggle "modded" status.
- **POST** `/api/server/<name>/jvm`: Update JVM arguments (RAM, cores).
- **GET** `/api/server/<name>/mods`: List mods for a server.
- **POST** `/api/server/<name>/mods`: Upload a mod `.jar`.
- **DELETE** `/api/server/<name>/mods/<mod_name>`: Remove a mod file.

## License

This project is licensed under the MIT License.

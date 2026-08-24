import os
import sys
import subprocess
import shutil
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# --- LAUNCHER SCRIPT CONTENT ---

LAUNCHER_PY_CONTENT = """import subprocess
import time
import tkinter as tk
from tkinter import ttk

def launch_tint2():
    status_label.config(text="Cleaning existing instances...")
    progress['value'] = 25
    root.update()
    
    subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", "pkill", "-9", "tint2"], 
                   creationflags=subprocess.CREATE_NO_WINDOW)
    time.sleep(0.3)

    status_label.config(text="Launching Tint2 panel...")
    progress['value'] = 65
    root.update()

    wslg_path = r"C:\\Program Files\\WSL\\wslg.exe"
    subprocess.Popen([wslg_path, "-d", "Ubuntu", "--cd", "~", "--", "tint2"], 
                     creationflags=subprocess.CREATE_NO_WINDOW)

    time.sleep(2.5)
    progress['value'] = 100
    status_label.config(text="Panel loaded!")
    root.update()
    
    time.sleep(0.4)
    root.destroy()

root = tk.Tk()
root.title("tin2win Launcher")
root.geometry("380x120")
root.resizable(False, False)
root.configure(bg="#1e1e2e")
root.eval('tk::PlaceWindow . center')

style = ttk.Style()
style.theme_use('clam')
style.configure("Custom.Horizontal.TProgressbar", 
                troughcolor='#313244', 
                background='#89b4fa', 
                bordercolor='#1e1e2e', 
                lightcolor='#89b4fa', 
                darkcolor='#89b4fa')

status_label = tk.Label(root, text="Initializing environment...", 
                        fg="#cdd6f4", bg="#1e1e2e", 
                        font=("Segoe UI", 10, "bold"))
status_label.pack(pady=(15, 8))

progress = ttk.Progressbar(root, style="Custom.Horizontal.TProgressbar", 
                           orient="horizontal", length=320, mode="determinate")
progress.pack(pady=5)

root.after(100, launch_tint2)
root.mainloop()
"""

# --- INSTALLER GUI CLASS ---

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("tin2win Setup")
        self.root.geometry("450x360")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")
        self.root.eval('tk::PlaceWindow . center')

        # Custom Styling
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Custom.Horizontal.TProgressbar", 
                            troughcolor='#313244', 
                            background='#89b4fa', 
                            bordercolor='#1e1e2e', 
                            lightcolor='#89b4fa', 
                            darkcolor='#89b4fa')

        # UI Elements
        self.title_label = tk.Label(root, text="tin2win Setup Wizard", 
                                    fg="#cdd6f4", bg="#1e1e2e", 
                                    font=("Segoe UI", 14, "bold"))
        self.title_label.pack(pady=(15, 2))

        self.desc_label = tk.Label(root, text="Automated Tint2 panel installer for WSLg.", 
                                   fg="#a6adc8", bg="#1e1e2e", 
                                   font=("Segoe UI", 9))
        self.desc_label.pack(pady=(0, 10))

        # Config Options Container
        self.opts_frame = tk.Frame(root, bg="#1e1e2e")
        self.opts_frame.pack(pady=5, fill="x", px=30)

        # Panel Position Selector
        self.pos_label = tk.Label(self.opts_frame, text="Panel Position:", 
                                  fg="#cdd6f4", bg="#1e1e2e", font=("Segoe UI", 9, "bold"))
        self.pos_label.grid(row=0, column=0, sticky="w", pady=5)

        self.pos_var = tk.StringVar(value="Bottom")
        self.pos_dropdown = ttk.Combobox(self.opts_frame, textvariable=self.pos_var, 
                                         values=["Bottom", "Top", "Left", "Right"], 
                                         state="readonly", width=12)
        self.pos_dropdown.grid(row=0, column=1, sticky="w", px=15, pady=5)

        # Browser Selection
        self.browser_label = tk.Label(self.opts_frame, text="Preferred Browser:", 
                                      fg="#cdd6f4", bg="#1e1e2e", font=("Segoe UI", 9, "bold"))
        self.browser_label.grid(row=1, column=0, sticky="nw", pady=5)

        self.browser_radio_frame = tk.Frame(self.opts_frame, bg="#1e1e2e")
        self.browser_radio_frame.grid(row=1, column=1, sticky="w", px=15, pady=5)

        self.browser_var = tk.StringVar(value="chrome")
        self.chrome_radio = tk.Radiobutton(self.browser_radio_frame, text="Google Chrome", variable=self.browser_var, 
                                           value="chrome", bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244", 
                                           activebackground="#1e1e2e", activeforeground="#cdd6f4", font=("Segoe UI", 9))
        self.chrome_radio.pack(anchor="w")

        self.firefox_radio = tk.Radiobutton(self.browser_radio_frame, text="Mozilla Firefox", variable=self.browser_var, 
                                            value="firefox", bg="#1e1e2e", fg="#cdd6f4", selectcolor="#313244", 
                                            activebackground="#1e1e2e", activeforeground="#cdd6f4", font=("Segoe UI", 9))
        self.firefox_radio.pack(anchor="w")

        # Progress & Status
        self.status_label = tk.Label(root, text="Click 'Install' to start setup.", 
                                     fg="#cdd6f4", bg="#1e1e2e", 
                                     font=("Segoe UI", 9))
        self.status_label.pack(pady=(10, 2))

        self.progress = ttk.Progressbar(root, style="Custom.Horizontal.TProgressbar", 
                                        orient="horizontal", length=380, mode="determinate")
        self.progress.pack(pady=5)

        self.install_btn = tk.Button(root, text="Install", command=self.start_installation,
                                     bg="#89b4fa", fg="#11111b", activebackground="#b4befe",
                                     font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=3)
        self.install_btn.pack(pady=(10, 0))

    def update_status(self, text, value):
        self.status_label.config(text=text)
        self.progress['value'] = value
        self.root.update_idletasks()

    def is_ubuntu_installed(self):
        try:
            res = subprocess.run(["wsl.exe", "-l", "-q"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return "Ubuntu" in res.stdout
        except FileNotFoundError:
            return False

    def generate_tint2_rc(self, position_choice, browser_choice):
        # Resolve Browser desktop launcher path
        browser_desktop = "/usr/share/applications/google-chrome.desktop"
        if browser_choice == "firefox":
            browser_desktop = "/var/lib/snapd/desktop/applications/firefox_firefox.desktop"

        # Resolve position and dimensions
        pos_map = {
            "Bottom": ("bottom left horizontal", "2560 36"),
            "Top": ("top left horizontal", "2560 36"),
            "Left": ("top left vertical", "36 1440"),
            "Right": ("top right vertical", "36 1440")
        }
        panel_pos, panel_sz = pos_map.get(position_choice, ("bottom left horizontal", "2560 36"))

        return f"""# --- TINT2 POSITION CONFIG FOR WSLg ---
panel_monitor = all
panel_position = {panel_pos}
panel_size = {panel_sz}
panel_margin = 0 0
panel_padding = 4 4 4

panel_dock = 0
panel_layer = top
strut_policy = none
wm_menu = 0

background_color_1 = #1e1e2e 100
border_color_1 = #89b4fa 100
background_color_id = 1
border_width = 1
rounded = 0

panel_items = LTC

launcher_padding = 4 4 2
launcher_background_id = 0
launcher_icon_background_id = 0
launcher_icon_size = 22
launcher_icon_theme = Adwaita
launcher_item_app = /usr/share/applications/xfce4-terminal.desktop
launcher_item_app = {browser_desktop}
launcher_item_app = /usr/share/applications/xfce4-file-manager.desktop

taskbar_mode = single_desktop
taskbar_padding = 4 2 2
taskbar_background_id = 1
taskbar_active_background_id = 1

time1_format = %I:%M %p
time1_font = Monospace 10
clock_font_color = #cdd6f4 100

disable_transparency = 1
"""

    def start_installation(self):
        self.install_btn.config(state="disabled")
        self.chrome_radio.config(state="disabled")
        self.firefox_radio.config(state="disabled")
        self.pos_dropdown.config(state="disabled")
        threading.Thread(target=self.run_install_process, daemon=True).start()

    def run_install_process(self):
        try:
            browser_choice = self.browser_var.get()
            position_choice = self.pos_var.get()

            # 1. Check WSL / Ubuntu
            if not self.is_ubuntu_installed():
                self.update_status("Installing WSL & Ubuntu (Elevated)...", 10)
                cmd = "Start-Process wsl.exe -ArgumentList '--install', '-d', 'Ubuntu' -Verb RunAs -Wait"
                subprocess.run(["powershell", "-Command", cmd], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(3)
            
            # 2. Base package installation
            self.update_status("Installing Tint2 & base desktop dependencies...", 30)
            pkg_cmd = "sudo apt update && sudo apt install -y tint2 xfce4-terminal xfce4-appfinder adwaita-icon-theme wget"
            subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", "bash", "-c", pkg_cmd], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

            # 3. Browser specific installation
            if browser_choice == "chrome":
                self.update_status("Downloading & installing Google Chrome...", 40)
                chrome_cmd = "cd ~ && wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && sudo apt install -y ./google-chrome-stable_current_amd64.deb && rm google-chrome-stable_current_amd64.deb"
                subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", "bash", "-c", chrome_cmd], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                self.update_status("Installing Firefox...", 40)
                ff_cmd = "sudo apt install -y firefox"
                subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", "bash", "-c", ff_cmd], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

            # 4. Deploy tint2rc configuration
            self.update_status(f"Deploying tint2rc ({position_choice} position)...", 55)
            tint2_rc_content = self.generate_tint2_rc(position_choice, browser_choice)
            rc_cmd = f"mkdir -p ~/.config/tint2 && cat << 'EOF' > ~/.config/tint2/tint2rc\n{tint2_rc_content}\nEOF"
            subprocess.run(["wsl.exe", "-d", "Ubuntu", "--", "bash", "-c", rc_cmd], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

            # 5. Generate Launcher Script
            self.update_status("Creating launcher script...", 70)
            app_dir = os.path.join(os.environ["LOCALAPPDATA"], "tin2win")
            os.makedirs(app_dir, exist_ok=True)
            
            script_path = os.path.join(app_dir, "tin2win_gui.py")
            with open(script_path, "w") as f:
                f.write(LAUNCHER_PY_CONTENT)

            # 6. Build Executable
            self.update_status("Compiling tin2win executable...", 85)
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            subprocess.run([
                "pyinstaller", "--noconsole", "--onefile",
                "--distpath", app_dir,
                "--workpath", os.path.join(app_dir, "build"),
                "--specpath", app_dir,
                "--name", "tin2win",
                script_path
            ], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

            exe_path = os.path.join(app_dir, "tin2win.exe")

            # 7. Shortcut Setup
            self.update_status("Creating Start Menu shortcut...", 95)
            start_menu = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs")
            shortcut_path = os.path.join(start_menu, "tin2win.lnk")

            ps_shortcut = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
            $Shortcut.TargetPath = '{exe_path}'
            $Shortcut.WorkingDirectory = '{app_dir}'
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-Command", ps_shortcut], check=True, creationflags=subprocess.CREATE_NO_WINDOW)

            # Cleanup
            shutil.rmtree(os.path.join(app_dir, "build"), ignore_errors=True)

            self.update_status("Installation Complete!", 100)
            messagebox.showinfo("tin2win", "tin2win has been installed successfully!\n\nYou can now search for 'tin2win' in your Windows Start Menu.")
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Installation Error", f"An error occurred during setup:\n{str(e)}")
            self.install_btn.config(state="normal")
            self.chrome_radio.config(state="normal")
            self.firefox_radio.config(state="normal")
            self.pos_dropdown.config(state="readonly")
            self.update_status("Installation failed. Click 'Install' to retry.", 0)

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
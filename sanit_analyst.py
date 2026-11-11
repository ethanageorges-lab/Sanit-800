import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
import threading
import sys
import os
import re
from sanit_core import Sanit800, EXIFTOOL_PATH

# Configuration du thème global
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class ConsoleRedirector:
    """Capture les 'print()' du backend pour les envoyer dans l'interface UI."""
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        self.textbox.after(0, self._write_to_textbox, text)

    def _write_to_textbox(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def flush(self):
        pass

# --- FUSION DE CUSTOMTKINTER ET TKINTERDND2 ---
class CTk_DnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class SanitUI(CTk_DnD):
    def __init__(self):
        super().__init__()
        
        self.title("SANIT-800 | MetaData Destroyer")
        self.geometry("800x550")
        self.iconbitmap("logo.ico")
        self.resizable(False, False)

        self.core = Sanit800(EXIFTOOL_PATH)

        # --- TITRE ---
        self.title_label = ctk.CTkLabel(
            self, 
            text="TERMINAL SANIT-800", 
            font=("Courier New", 28, "bold"), 
            text_color="#ff3333"
        )
        self.title_label.pack(pady=(20, 5))

        self.subtitle_label = ctk.CTkLabel(
            self, 
            text="Système de purge absolue | [ GLISSEZ-DÉPOSEZ VOS FICHIERS ICI ]", 
            font=("Courier New", 12)
        )
        self.subtitle_label.pack(pady=(0, 20))

        # --- BOUTONS ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)

        self.btn_file = ctk.CTkButton(
            self.btn_frame, 
            text="[ SÉLECTIONNER UN FICHIER ]", 
            font=("Courier New", 14, "bold"),
            fg_color="#333333", 
            hover_color="#aa0000",
            command=self.select_file
        )
        self.btn_file.pack(side="left", padx=15)

        self.btn_folder = ctk.CTkButton(
            self.btn_frame, 
            text="[ SÉLECTIONNER UN DOSSIER ]", 
            font=("Courier New", 14, "bold"),
            fg_color="#333333", 
            hover_color="#aa0000",
            command=self.select_folder
        )
        self.btn_folder.pack(side="left", padx=15)

        # --- CONSOLE DE LOGS ---
        self.console = ctk.CTkTextbox(
            self, 
            width=700, 
            height=300, 
            font=("Consolas", 13),
            fg_color="#1e1e1e",
            text_color="#00ff00",
            state="disabled"
        )
        self.console.pack(pady=20)

        sys.stdout = ConsoleRedirector(self.console)
        print("=== INTERFACE SANIT-800 PRÊTE ===")
        print("[+] En attente de cible... (Glissez un fichier ou un dossier dans la fenêtre)")

        # --- CONFIGURATION DU DRAG & DROP ---
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        """Gère les fichiers relâchés sur la fenêtre"""
        dropped_data = event.data
        
        # Nettoyage des chemins (TkinterDnD2 ajoute parfois des accolades si le chemin contient des espaces)
        if '{' in dropped_data:
            paths = [p for p in re.split(r'[{}]', dropped_data) if p.strip()]
        else:
            paths = dropped_data.split()

        for path in paths:
            self.launch_purge(path)

    def select_file(self):
        file_path = filedialog.askopenfilename(title="Sélectionner un fichier à purger")
        if file_path:
            self.launch_purge(file_path)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Sélectionner un dossier complet")
        if folder_path:
            self.launch_purge(folder_path)

    def launch_purge(self, target_path):
        threading.Thread(target=self.run_backend, args=(target_path,), daemon=True).start()

    def run_backend(self, target_path):
        print(f"\n[>] CIBLE VERROUILLÉE : {target_path}")
        self.core.process_target(target_path)
        print("-" * 50)

if __name__ == "__main__":
    app = SanitUI()
    app.mainloop()
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
import threading
import sys
import re
from sanit_core import Sanit800, EXIFTOOL_PATH

# Configuration du thème global (Dark/Cyber)
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
        self.geometry("850x600")
        self.iconbitmap("logo.ico")
        self.minsize(800, 500) # Permet de redimensionner la fenêtre de manière fluide
        
        # Initialisation du moteur
        self.core = Sanit800(EXIFTOOL_PATH)

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(15, 5), padx=20)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="[ SANIT-800 ]", 
            font=("Courier New", 28, "bold"), 
            text_color="#ff3333"
        )
        self.title_label.pack(side="left")

        # Boutons de secours discrets à droite (au cas où on ne veut pas drag & drop)
        self.btn_folder = ctk.CTkButton(
            self.header_frame, text="Parcourir...", width=100,
            font=("Courier New", 12), fg_color="#2b2b2b", hover_color="#aa0000",
            command=self.select_folder
        )
        self.btn_folder.pack(side="right")

        # --- DROP ZONE (ZONE D'ANIMATION) ---
        # Un grand cadre au centre avec des bordures pointillées/épaisses
        self.drop_zone = ctk.CTkFrame(
            self, 
            height=150, 
            corner_radius=15, 
            border_width=2, 
            border_color="#444444", 
            fg_color="#1a1a1a"
        )
        self.drop_zone.pack(fill="x", padx=20, pady=10)
        self.drop_zone.pack_propagate(False) # Force la hauteur fixe

        self.drop_label = ctk.CTkLabel(
            self.drop_zone, 
            text=">> GLISSEZ VOS CIBLES ICI <<", 
            font=("Courier New", 20, "bold"), 
            text_color="#555555"
        )
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        # --- CONSOLE DE LOGS ---
        self.console = ctk.CTkTextbox(
            self, 
            font=("Consolas", 12),
            fg_color="#0a0a0a", # Presque noir absolu
            text_color="#00ff00", # Vert Matrix/Terminal
            border_color="#333333",
            border_width=1,
            state="disabled"
        )
        self.console.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Redirection des logs
        sys.stdout = ConsoleRedirector(self.console)
        print("=== TERMINAL OPÉRATIONNEL ===")
        print("[+] En attente de verrouillage de cible...\n")

        # --- BINDING DES ÉVÉNEMENTS DRAG & DROP ---
        # On enregistre la fenêtre principale ET la zone de drop
        self.drop_target_register(DND_FILES)
        self.drop_zone.drop_target_register(DND_FILES)
        
        # Animations au survol
        self.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    # --- EFFETS VISUELS ---
    def on_drag_enter(self, event):
        """Déclenché quand un fichier survole la fenêtre."""
        self.drop_zone.configure(border_color="#ff3333", fg_color="#3a0a0a")
        self.drop_label.configure(text="[ VERROUILLAGE EN COURS ]", text_color="#ff3333")

    def on_drag_leave(self, event):
        """Déclenché quand le fichier quitte la zone sans être lâché."""
        self.drop_zone.configure(border_color="#444444", fg_color="#1a1a1a")
        self.drop_label.configure(text=">> GLISSEZ VOS CIBLES ICI <<", text_color="#555555")

    # --- LOGIQUE MÉTIER ---
    def handle_drop(self, event):
        """Gère le relâchement des fichiers."""
        # On remet l'UI à son état normal
        self.on_drag_leave(event)
        
        dropped_data = event.data
        if '{' in dropped_data:
            paths = [p for p in re.split(r'[{}]', dropped_data) if p.strip()]
        else:
            paths = dropped_data.split()

        for path in paths:
            self.launch_purge(path)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Sélectionner un dossier complet")
        if folder_path:
            self.launch_purge(folder_path)

    def launch_purge(self, target_path):
        # On lance dans un thread pour que les animations et l'UI restent fluides
        threading.Thread(target=self.run_backend, args=(target_path,), daemon=True).start()

    def run_backend(self, target_path):
        self.core.process_target(target_path)
        print("-" * 60)

if __name__ == "__main__":
    app = SanitUI()
    app.mainloop()
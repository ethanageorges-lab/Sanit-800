import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import filedialog
import threading
import re
from sanit_core import Sanit800, EXIFTOOL_PATH

# Configuration du thème global (Dark/Cyber)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# --- FUSION DE CUSTOMTKINTER ET TKINTERDND2 ---
class CTk_DnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class SanitUI3(CTk_DnD):
    def __init__(self):
        super().__init__()
        
        self.title("SANIT-800 | Édition Minimaliste")
        self.geometry("600x400") 
        self.iconbitmap("logo.ico")
        self.resizable(False, False)
        
        # --- FENÊTRE PRINCIPALE COMME ZONE DE DROP ---
        self.configure(fg_color="#1a1a1a")
        
        self.core = Sanit800(EXIFTOOL_PATH)

        self.title_label = ctk.CTkLabel(
            self, 
            text="[ SANIT-800 ]", 
            font=("Courier New", 36, "bold"), 
            text_color="#ff3333"
        )
        self.title_label.pack(pady=(80, 10))

        self.status_label = ctk.CTkLabel(
            self, 
            text=">> GLISSEZ VOS CIBLES ICI <<", 
            font=("Courier New", 16), 
            text_color="#555555"
        )
        self.status_label.pack(pady=(20, 20))

        # --- ANIMATION DE CHARGEMENT ---
        self.loader = ctk.CTkProgressBar(
            self, 
            width=300,
            mode="indeterminate",
            fg_color="#1a1a1a",
            progress_color="#ff3333"
        )
        self.loader.set(0)

        # --- BOUTONS DE SECOURS (Fichier ET Dossier) ---
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(side="bottom", pady=30)

        self.btn_file = ctk.CTkButton(
            self.btn_frame, text="Fichier...", width=100, height=28,
            font=("Courier New", 12), fg_color="transparent", hover_color="#333333",
            border_width=1, border_color="#444444",
            command=self.select_file
        )
        self.btn_file.pack(side="left", padx=10)

        self.btn_folder = ctk.CTkButton(
            self.btn_frame, text="Dossier...", width=100, height=28,
            font=("Courier New", 12), fg_color="transparent", hover_color="#333333",
            border_width=1, border_color="#444444",
            command=self.select_folder
        )
        self.btn_folder.pack(side="left", padx=10)

        # --- BINDING DES ÉVÉNEMENTS DRAG & DROP ---
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<DragEnter>>', self.on_drag_enter)
        self.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def on_drag_enter(self, event):
        self.configure(fg_color="#3a0a0a") 
        self.status_label.configure(text="[ VERROUILLAGE EN COURS ]", text_color="#ff3333")

    def on_drag_leave(self, event):
        self.configure(fg_color="#1a1a1a")
        self.status_label.configure(text=">> GLISSEZ VOS CIBLES ICI <<", text_color="#555555")

    def handle_drop(self, event):
        self.on_drag_leave(event)
        dropped_data = event.data
        if '{' in dropped_data:
            paths = [p for p in re.split(r'[{}]', dropped_data) if p.strip()]
        else:
            paths = dropped_data.split()
        
        self.start_processing(paths)

    # NOUVELLE FONCTION POUR LES FICHIERS ISOLÉS
    def select_file(self):
        file_path = filedialog.askopenfilename(title="Sélectionner un fichier à purger")
        if file_path:
            self.start_processing([file_path])

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Sélectionner un dossier complet")
        if folder_path:
            self.start_processing([folder_path])

    def start_processing(self, paths):
        self.status_label.configure(text="[ PURGE EN COURS... ]", text_color="#ffaa00")
        self.loader.pack(pady=10)
        self.loader.start()
        # On désactive les deux boutons pendant la purge
        self.btn_file.configure(state="disabled")
        self.btn_folder.configure(state="disabled")

        threading.Thread(target=self.run_backend, args=(paths,), daemon=True).start()

    def run_backend(self, paths):
        for path in paths:
            self.core.process_target(path)
        
        self.after(500, self.stop_processing)

    def stop_processing(self):
        self.loader.stop()
        self.loader.pack_forget() 
        
        self.status_label.configure(text="[ MISSION TERMINÉE ]", text_color="#00ff00")
        # On réactive les deux boutons
        self.btn_file.configure(state="normal")
        self.btn_folder.configure(state="normal")
        
        self.after(2000, lambda: self.status_label.configure(
            text=">> GLISSEZ VOS CIBLES ICI <<", text_color="#555555"
        ))

if __name__ == "__main__":
    app = SanitUI3()
    app.mainloop()
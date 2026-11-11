import exiftool
import os
import time

EXIFTOOL_PATH = os.path.abspath(r"bin\exiftool.exe")

class Sanit800:
    def __init__(self, executable_path):
        if not os.path.exists(executable_path):
            raise FileNotFoundError(f"[!] Erreur critique : {executable_path} introuvable.")
        self.executable = executable_path

    def analyze(self, file_path):
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            return

        print(f"\n[*] Scan de : {os.path.basename(abs_path)}")
        with exiftool.ExifToolHelper(executable=self.executable) as et:
            try:
                metadata = et.get_metadata(abs_path)
                for d in metadata:
                    for key, value in d.items():
                        if "SourceFile" not in key and "ExifTool:Error" not in key:
                            print(f"  -> {key} : {value}")
            except Exception as e:
                print(f"[!] Échec de l'analyse : {e}")

    def purge_file(self, file_path):
        abs_path = os.path.abspath(file_path)
        with exiftool.ExifToolHelper(executable=self.executable) as et:
            try:
                # -all= : Détruit toutes les métadonnées internes
                # -FileModifyDate=now et -FileCreateDate=now : Réinitialise les traces temporelles du disque dur
                # -overwrite_original : Écrase le fichier sans laisser de copie de secours
                et.execute(
                    "-all=", 
                    "-FileModifyDate=now", 
                    "-FileCreateDate=now", 
                    "-overwrite_original", 
                    abs_path
                )
                print(f"[+] NEUTRALISÉ : {os.path.basename(abs_path)}")
            except Exception as e:
                print(f"[!] Échec sur {os.path.basename(abs_path)} : {e}")

    def process_target(self, target_path):
        """Détecte si la cible est un fichier unique ou un dossier complet."""
        abs_path = os.path.abspath(target_path)
        
        if not os.path.exists(abs_path):
            print(f"[!] Cible introuvable : {abs_path}")
            return

        print(f"\n[!] DÉMARRAGE DE LA PURGE ABSOLUE : {abs_path}")
        start_time = time.time()
        
        if os.path.isfile(abs_path):
            # C'est un seul fichier
            self.purge_file(abs_path)
            count = 1
        elif os.path.isdir(abs_path):
            # C'est un dossier, on scanne tout le contenu (même dans les sous-dossiers)
            count = 0
            for root, dirs, files in os.walk(abs_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.purge_file(file_path)
                    count += 1
        
        elapsed_time = round(time.time() - start_time, 2)
        print(f"\n[=] MISSION TERMINÉE : {count} fichier(s) purgé(s) en {elapsed_time} secondes.")

if __name__ == "__main__":
    print("=== MOTEUR SANIT-800 ===")
    try:
        core = Sanit800(EXIFTOOL_PATH)
        print("[+] Moteur initialisé avec succès.")
        
        # --- ZONE DE TEST ---
        # Tu peux mettre le nom d'un fichier (ex: "test.jpg") 
        # OU le nom d'un dossier complet (ex: "dossier_test")
        
        cible = "dossier_test" 
        
        # Si tu veux créer un dossier "dossier_test" avec plein de fichiers dedans, 
        # change juste la variable au-dessus : cible = "dossier_test"
        
        core.process_target(cible)
        
    except Exception as e:
        print(e)
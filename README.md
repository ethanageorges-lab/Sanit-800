# 🛡️ SANIT-800 | MetaData Destroyer

SANIT-800 est un outil de cybersécurité (Open Source) conçu pour la purge absolue et irréversible des métadonnées (EXIF, ID3, XML, XMP) sur plus de 100 formats de fichiers (Images, PDF, Vidéos, Audio, Office).

Basé sur un wrapper Python exploitant la puissance du moteur `ExifTool`, il ne se contente pas d'effacer les balises en surface : il écrase les données structurelles, réinitialise les traces temporelles du système d'exploitation et ne laisse aucun fichier de sauvegarde.

## 🚀 3 Niveaux d'Interface (UI)
Parce que chaque utilisateur a des besoins différents, SANIT-800 est livré avec 3 interfaces distinctes exploitant le même moteur de destruction :
* **Édition Express (`sanit_express.py`) :** UI minimaliste avec Drag & Drop géant et barre de progression. Idéal pour un nettoyage rapide et sans friction.
* **Édition Opérateur (`sanit_operator.py`) :** Le compromis parfait. Drag & Drop réactif avec une console de monitoring intégrée pour un retour visuel.
* **Édition Analyste (`sanit_analyst.py`) :** Interface austère, sélection stricte des chemins et affichage exhaustif des balises avant/après purge.

## 🛠️ Installation (Code Source)
```bash
git clone [https://github.com/ethanageorges-lab/Sanit-800.git](https://github.com/ethanageorges-lab/Sanit-800.git)
cd Sanit-800
pip install -r requirements.txt
<p align="center">
  <img src="docs/logo_readme.png" alt="HyStudio" width="380">
</p>

#

Logiciel de bureau pour personnaliser un modèle 3D de voiture et en produire une
rotation 360° fluide, affichée par la visionneuse `i20view` de l'autoradio.
Tout se fait à la souris : choix des matières, aperçu réaliste, génération, copie
sur la carte SD.

![Vue 3D et panneau Matière](docs/01_vue3d_matiere.png)

## Démarrer

Double-cliquez sur **`HyStudio.exe`** (version compilée, dossier `dist\HyStudio`) ou
sur **`HyStudio.pyw`** (depuis les sources). Au premier lancement, un projet
Hyundai i20 prêt à l'emploi est créé avec des réglages déjà validés sur
l'autoradio. Les projets s'enregistrent en `.hysp`.

Pour partir d'un autre véhicule : **Fichier › Nouveau projet** puis choisissez un
modèle `.obj`, `.gltf` ou `.glb`.

**glTF (recommandé quand il existe)** : le fichier porte les textures (tableau de
bord, compteurs, logos, intérieur…) et des matériaux complets. Les matériaux
texturés gardent la matière **Matériau d'origine** : ils s'affichent tels que le
fichier les décrit, dans la vue 3D comme dans le rendu. Les autres deviennent des
matières HyStudio modifiables (peinture, verre, chrome…). Chaque matériau peut
passer de l'un à l'autre dans le panneau Matière.

**OBJ** : les matières de départ sont devinées d'après les noms des matériaux du
fichier.

Si le modèle est accompagné d'un fichier de matériaux `.mtl` contenant de vraies
valeurs (couleurs, transparences, reflets), HyStudio propose de les reprendre :
**Utiliser le MTL** ou **Ignorer**. Beaucoup d'exportateurs n'y écrivent qu'un
gris uniforme : dans ce cas, rien n'est proposé. Le choix n'est pas définitif :
**Fichier › Importer les matériaux d'un fichier MTL** l'applique à un projet
existant (les pièces qui ont une matière propre ne changent pas, `Ctrl+Z`
annule). Les textures d'image citées par le `.mtl` ne sont pas reprises.

## Personnaliser le véhicule

- **Choisir une pièce** : cliquez dans la vue 3D (glisser pour tourner, molette
  pour zoomer) ou dans la liste de gauche. Un clic sur un groupe de la liste
  sélectionne toutes ses pièces.
- **Changer sa matière** dans le panneau Matière : peinture (brillante, satinée,
  mate), chrome, métal, plastique, caoutchouc, verre, image, ou masque pour la
  faire disparaître.
- **Une pièce ou tout le groupe** : « Cette pièce seulement » lui donne une
  matière propre (marquée • dans la liste) ; l'autre choix modifie toutes les
  pièces du même matériau.
- **Renommer** une pièce avec le champ Nom, pour s'y retrouver dans la liste.

### Poser une image : autocollant ou plaque

Deux façons, selon la pièce :

- **Autocollant** (logo sur une portière, bande sur le capot…) : gardez la vraie
  matière de la pièce (peinture, plastique, métal…), tournez la vue 3D face à
  l'endroit voulu, puis **Autocollant › Poser une image**. L'image se pose
  par-dessus la matière, sans déformation, et seulement sur les faces tournées
  vers cette vue. Réglez sa taille, sa position et sa rotation ; **Orienter
  depuis la vue actuelle** la réoriente. Posé sur un groupe (par exemple
  « Peinture carrosserie »), un seul autocollant couvre tout le groupe, à
  cheval sur plusieurs pièces si besoin. Un PNG à fond transparent donne un
  contour net.
- **Matière Image** : l'image remplace toute la matière et s'étire jusqu'aux
  bords de la pièce. C'est fait pour une pièce plate et rectangulaire, comme une
  plaque d'immatriculation (520 × 110 mm) ; sur une pièce bombée, elle se
  déforme.

![Image posée sur la plaque arrière](docs/03_image_sur_piece.png)

*Les captures utilisent une plaque fictive.*

## Vérifier avant de lancer le calcul

La vue 3D sert à reconnaître les pièces ; elle ne montre pas le rendu final.
L'onglet **Aperçu réaliste** calcule en quelques secondes une vue sous l'angle
choisi, exactement telle que l'autoradio l'affichera (800 × 424).

![Aperçu réaliste](docs/02_apercu_realiste.png)

Le panneau **Studio** règle l'exposition, la netteté, le nombre de vues
(180, 360 ou 720, soit 2°, 1° ou 0,5° par vue), la qualité du calcul et la
lumière d'habitacle. La durée et la taille estimées se mettent à jour à chaque
changement.

## Générer et installer sur l'autoradio

1. **Générer pour l'autoradio** : toutes les vues sont calculées puis compressées
   au fur et à mesure. La barre indique l'avancement et l'heure de fin prévue.
   Le calcul peut être annulé ; le fichier n'est écrit que s'il est complet.
2. **Copier sur la carte SD** : insérez la carte SD de l'autoradio dans le PC.
   HyStudio la reconnaît, refuse d'écrire si elle est endommagée, copie la
   rotation et la visionneuse, vérifie la copie puis éjecte la carte.

![Génération en cours](docs/04_generation.png)

## Langue

HyStudio s'affiche dans la langue de Windows : français, anglais, espagnol,
allemand, italien, russe, chinois, japonais ou coréen (anglais pour toute
autre langue). Le menu **Langue** permet d'en choisir une autre ; la fenêtre
change aussitôt, sans perdre le projet en cours ni l'historique d'annulation.
**Automatique** revient à la langue de Windows.

## Annuler une modification

`Ctrl+Z` annule, `Ctrl+Y` (ou `Ctrl+Maj+Z`) rétablit, aussi depuis le menu
Édition. Cela couvre les matières, les noms et les réglages du studio. Plusieurs
petits ajustements d'un même réglage à la suite s'annulent en une fois.

## Modèles compatibles

- **Formats** : glTF 2.0 (`.gltf` avec ses textures, ou `.glb`) et OBJ. L'OBJ
  doit avoir l'axe Y vers le haut, le réglage par défaut de l'export OBJ de
  Blender ; un modèle exporté avec Z vers le haut apparaît couché sur le côté :
  réexportez-le. Un OBJ ne conserve en général pas les textures : préférez le
  glTF quand le modèle en propose un.
- **Unités** : détectées automatiquement (m, dm, cm, mm ou 1/10 mm) d'après la
  longueur plausible d'une voiture. La lumière du studio et de l'habitacle
  s'adapte à la taille du véhicule.
- **Pièces séparées** : pour sélectionner une pièce seule ou y poser une image,
  le modèle doit être découpé en objets. Si ce n'est pas le cas, HyStudio
  prévient à l'ouverture. Les matières par matériau, le masquage, l'aperçu et
  la génération restent disponibles.

![Avertissement pour un modèle non découpé](docs/05_modele_non_decoupe.png)

## Bon à savoir

- **Durée** : chaque vue est un vrai calcul de lumière. Comptez environ 35 minutes
  pour 720 vues avec une carte graphique récente (RTX 3080). Baisser la qualité
  accélère le calcul ; vérifiez le grain dans l'aperçu.
- **Place sur l'autoradio** : environ 100 Ko par vue, soit ~73 Mo pour 720 vues.
  HyStudio prévient si le fichier devient trop gros pour la mémoire disponible.
- **Intérieur sombre** : la lumière d'habitacle éclaire peu un intérieur presque
  noir ; éclaircissez plutôt la matière de l'habitacle.
- **Anciens projets** : les projets `.hyproj` et `.carproj` (Car Studio, l'ancien
  nom) s'ouvrent toujours. Le projet de démarrage est copié au format `.hysp`,
  l'ancien fichier reste en place.

## Prérequis

- Windows avec une carte graphique compatible OpenGL 3.3.
- Version compilée : rien d'autre que Blender. Depuis les sources : Python 3.14
  avec PySide6, PyOpenGL, numpy et Pillow ; PyInstaller pour compiler
  (`build_exe.py`, qui produit le dossier `dist\HyStudio`, environ 170 Mo).
- Blender 4.2 : la version portable du dossier `tools/` du dépôt, ou une
  installation standard, trouvée automatiquement. Il n'est pas inclus dans
  l'exe : placé dans un dossier `blender…` à côté de `HyStudio.exe`, il est
  aussi reconnu.
- Version compilée : le cache (géométrie, textures) va dans
  `%LOCALAPPDATA%\HyStudio`, les projets dans `projets` à côté de l'exe.

## Organisation du code

| élément | rôle |
|---|---|
| `core/objmodel.py` | lecture OBJ pièce par pièce, détection des unités, cache |
| `core/presets.py` | types de matière, partagés par l'interface et le rendu |
| `core/gltfmodel.py` | lecture glTF : géométrie, coordonnées de texture, matériaux et textures |
| `core/mtl.py` | lecture du fichier `.mtl` et conversion en matières |
| `core/project.py` | projet `.hysp` (JSON) et profil i20 |
| `core/paths.py` | emplacements : sources ou exe, cache, projets, Blender |
| `core/pipeline.py` | pilotage de Blender : aperçu, génération et compression |
| `core/encoder.py` | format `I20P` lu par `i20view.exe` |
| `core/i18n.py`, `core/translations.py` | langues de l'interface et table des traductions |
| `core/device.py` | carte SD : intégrité, copie vérifiée, éjection |
| `blender/render_project.py` | scène Cycles construite depuis le projet |
| `ui/viewport.py` | vue 3D OpenGL, sélection des pièces |
| `ui/mainwindow.py` | fenêtre, panneaux, tâches en arrière-plan |
| `build_exe.py` | compilation en `HyStudio.exe` (PyInstaller) |
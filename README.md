# ERO1 💻

Optimisation hivernale

#Epita/ING1/ERO1

Bienvenue sur le README du groupe **La TEAMZ**. Vous trouverez ci-dessous toutes les instructions et les librairies utilisées.
Ainsi que l'architecture du projet.

---

## Les librairies nécessaires 📚 :

- `osmnx`

Si vous souhaitez installer les librairies passer par pip avec cette commande:

- `pip install osmnx`

## Utiliser notre projet 🔎 :

Depuis la racine faites `python main.py -h`

Vous aurez plusieurs possibilité de commandes, voici une liste non exhaustive :

- `--place` avec le quartier souahité
- `--scenario` avec le scenario souhaité
- `--multi` avec les quartiers souahaité

Par défault si aucun arguments n'est donné vous lancer le programme de "Déneigement de Montreal"

A titre d'exemple `python main.py --place verdun --scenario deneigement` lancera le deneigement de verdun qui prend 1 s

Pour un peu plus de détails voici un tableau recapitulatifs des temps :

|  Scenario   |   Quartier    |  Temps   |
| :---------: | :-----------: | :------: |
|    scan     |   Montreal    | `7 min`  |
|    scan     |   Outremont   | `4 sec`  |
|    scan     |    Verdun     | `4 sec`  |
|    scan     | Saint Leonard | `4 sec`  |
|    scan     |  Mont Royal   | `6 sec`  |
|    scan     |    Rivière    | `10 sec` |
| deneigement |   Outremont   | `1 sec`  |
| deneigement |    Verdun     | `2 sec`  |
| deneigement | Saint Leonard | `2 sec`  |
| deneigement |  Mont Royal   | `3 min`  |
| deneigement |    Riviere    | `20 min` |

NB: Ces temps on été réaliser sur un processeur Intel(R) Core(TM) i7-10750H et 16GB de RAM. Vos temps peuvent varier en fonction de votre matériel

Il ne vous reste plus qu’à utiliser notre superbe programme 🎉

## L'architecture du projet 📐 :

Le rendu doit suivre les contraintes ci-dessous, elles sont liées aux au travail de recherche et développement
qu’on souhaite vous voir faire.
Le rendu est composé d’une archive dont la racine contient :

1. un AUTHORS contenant la liste des auteurs ;
2. un README contenant les instructions d’installation et d’exécution ainsi qu’un descriptif de la structure
   de votre rendu ;
3. un fichier pdf d’un maximum de 4 pages qui effectue une synthèse des réflexions de l’équipe et doit
   contenir :
   - un résumé des données utilisées, ainsi que du périmètre considéré (quelles contraintes sont prises en
     compte)
   - les hypothèses et choix de modélisation
   - la ou les solutions retenues, les indicateurs, la comparaison des scenarios
   - les limites du modèle
4. un script exécutant une démonstration de votre solution ;
5. une sous-arborescence conscacrée à l’étude du vol de reconnaissance du drone ;
6. une sous-arborescence consacrée à l’étude du plan de déneigement des véhicules, sur les secteurs :
   - Outremont,
   - Verdun,
   - Saint-Léonard,
   - Rivière-des-prairies-pointe-aux-trembles,
   - et Le Plateau-Mont-Royal.

## Les membres du groupe 👨‍🏫 :

- Todd Tavernier
- Emil Toulouse
- Thibault de Lattre
- Antoine Montaldo

---

README écrit par Emil Toulouse.

import argparse
import sys
sys.path.append('./deneigement')
sys.path.append('./scan')
from scan import scan
from deneigement.deneigement_euler import deneigement_euler,meilleur_split

deneigeuse_T1 = {
    "nom" : "deneigeuse Type1",
    "vitesse" :  10,
    "cout_jour": 500,
    "cout_kilo": 1.1,
    "cout_horaires_8":1.1,
    "cout_horaires_8p":1.3
}

deneigeuse_T2 = {
    "nom" : "deneigeuse Type2",
    "vitesse" :  20,
    "cout_jour": 800,
    "cout_kilo": 1.3,
    "cout_horaires_8":1.3,
    "cout_horaires_8p":1.5
}

def run_scenario(scenario, place, multi=None):
    print(f'Lancement du scenario {scenario}')
    if scenario == "scan":
        if place:
            return scan(place)
    elif scenario == "deneigement":
        if multi is not None:
            return meilleur_split(multi)
        else:
            return deneigement_euler(place,deneigeuse_T1)
    elif scenario == "presentation":
        if place != "montreal":
            scan(place)
            input()
            deneigement_euler(place,deneigeuse_T1)
            input()
            meilleur_split(["outremont","verdun","saintLeonard"])
        else:
            print(f"Pour le bien de cette présentation nous ne nous pencherons pas sur ce quartier !")


def main():
    parser = argparse.ArgumentParser(description='ERO1 Optimisation Hivernale')
    parser.add_argument('--scenario', choices=['scan', 'deneigement', 'presentation'], default='presentation', help='Le scénario à exécuter (par défaut: presentation)')
    parser.add_argument('--place', choices=['montreal', 'outremont', 'verdun', 'riviere', 'saintLeonard', 'montRoyal'], default='montreal', help="Choix de l'endroit ou effectuer le scenario (par défaut: montreal)")
    parser.add_argument('--multi', nargs='+',choices=['outremont', 'verdun', 'riviere', 'saintLeonard', 'montRoyal'] ,help="Exécuter le scénario de déneigement avec les quartiers spécifiés pour savoir laquelle choisir")
    
    args = parser.parse_args()

    if args.scenario == 'scan':
        return run_scenario(args.scenario, args.place)
    elif args.scenario == 'deneigement':
        run_scenario(args.scenario, args.place,args.multi)
    elif args.scenario == 'presentation':
        run_scenario(args.scenario, args.place)

# Appel de la fonction main() lorsque le fichier est exécuté
if __name__ == '__main__':
    main()

import argparse
import os
import sys
sys.path.append('./deneigement')
sys.path.append('./scan')
from scan import scan
from deneigement import deneigement_euler

def run_scenario(scenario, place, multi=False):
    print(f'Lancement du scenario {scenario} à {place}')
    if scenario == "scan":
        if place:
            return scan(place)
    # if scenario == "deneigement":
    #     if place == "montreal" and not multi:
    #         return 


def main():
    parser = argparse.ArgumentParser(description='ERO1 Optimisation Hivernale')
    parser.add_argument('--scenario', choices=['scan', 'scenario2', 'scenario3'], default='scan', help='Le scénario à exécuter (par défaut: scan)')
    parser.add_argument('--place', choices=['montreal', 'outremont', 'verdun', 'riviere', 'saintLeonard', 'montRoyal'], default='montreal', help="Choix de l'endroit ou effectuer le scenario (par défaut: montreal)")
    parser.add_argument('--multi', action='store_true', help="Exécuter le scénario de déneigement en mode multi-deneigeuse")
    
    args = parser.parse_args()

    if args.scenario == 'scan':
        return run_scenario(args.scenario, args.place)
    elif args.scenario == 'deneigement':
        run_scenario(args.scenario, args.place,args.multi)  # Ajouter un cas si nécessaire
    elif args.scenario == 'presentation':
        run_scenario(args.scenario, None)  # Ajouter un cas si nécessaire

# Appel de la fonction main() lorsque le fichier est exécuté
if __name__ == '__main__':
    main()

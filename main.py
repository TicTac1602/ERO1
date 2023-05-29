import argparse
import os
import sys
sys.path.append('./scan')
from scan import scan

def run_scenario(scenario, place):
    print(f'Lancement du scenario {scenario} à {place}')
    if scenario == "scan":
        if place:
            return scan(place)

def main():
    parser = argparse.ArgumentParser(description='ERO1 Optimisation Hivernale')
    parser.add_argument('--scenario', choices=['scan', 'scenario2', 'scenario3'], default='scan', help='Le scénario à exécuter (par défaut: scan)')
    parser.add_argument('--place', choices=['montreal', 'outremont', 'verdun', 'riviere', 'saintLeonard', 'montRoyal'], default='montreal', help="Choix de l'endroit ou effectuer le scenario (par défaut: montreal)")

    args = parser.parse_args()

    if args.scenario == 'scan':
        return run_scenario(args.scenario, args.place)
    elif args.scenario == 'scenario2':
        run_scenario(args.scenario, None)  # Ajouter un cas si nécessaire
    elif args.scenario == 'scenario3':
        run_scenario(args.scenario, None)  # Ajouter un cas si nécessaire

# Appel de la fonction main() lorsque le fichier est exécuté
if __name__ == '__main__':
    main()

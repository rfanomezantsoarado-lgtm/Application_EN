# Importation des bibliothèques utiles

from kivy.config import Config

# Taille téléphone Android
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', '0')

import traceback
import os
import sys

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.logger import Logger

# Importation des écrans
from accueil import AccueilScreen
from clients import ClientScreen
from produits import ProduitScreen
from commande import CommandeScreen
from historique_commande import HistoriqueCommandeScreen
from backup_restore import SauvegardeScreen

from database import sauvegarder_base_donnees

def verifier_et_sauvegarder_avant_mise_a_jour():
    """Vérifie si c'est une nouvelle version et sauvegarde si nécessaire"""
    import json

    version_file = "version.json"
    current_version = "1.0"  # Version actuelle de l'app

    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            data = json.load(f)
            ancienne_version = data.get('version', '1.0')

            if ancienne_version != current_version:
                print(f"Mise à jour détectée : {ancienne_version} -> {current_version}")
                print("Sauvegarde automatique en cours...")
                sauvegarder_base_donnees()

                # Mettre à jour la version
                data['version'] = current_version
                with open(version_file, 'w') as f:
                    json.dump(data, f)
    else:
        # Première installation
        with open(version_file, 'w') as f:
            json.dump({'version': current_version}, f)

class ENApp(App):

    def build(self):

        try:

            Logger.info("ENAPP: Demarrage application")

            sm = ScreenManager()

            sm.add_widget(AccueilScreen(name="accueil"))
            sm.add_widget(ClientScreen(name="clients"))
            sm.add_widget(ProduitScreen(name="produits"))
            sm.add_widget(CommandeScreen(name="commande"))
            sm.add_widget(HistoriqueCommandeScreen(name="historique_commande"))
            sm.add_widget(SauvegardeScreen(name="sauvegarde"))

            return sm

        except Exception as e:

            print("ERREUR BUILD APPLICATION")
            print(str(e))

            traceback.print_exc()

            Logger.error(f"ENAPP: {str(e)}")

            raise e


if __name__ == "__main__":

    try:

        ENApp().run()

    except Exception as e:

        print("ERREUR LANCEMENT APPLICATION")
        print(str(e))

        traceback.print_exc()

        Logger.error(f"ENAPP: Crash -> {str(e)}")

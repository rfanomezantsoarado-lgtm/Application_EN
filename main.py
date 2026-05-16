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

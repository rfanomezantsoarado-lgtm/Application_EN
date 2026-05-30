# backup_restore.py

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle, Rectangle
import os

# Import des fonctions de sauvegarde depuis database
from database import sauvegarder_base_donnees, restaurer_derniere_sauvegarde, lister_sauvegardes, supprimer_sauvegarde

# ===================================================
# COULEURS
# ===================================================
BG_DARK       = (0.04, 0.07, 0.16, 1)
BG_CARD       = (0.07, 0.11, 0.22, 1)
ACCENT        = (0.08, 0.45, 0.82, 1)
ACCENT_GREEN  = (0.05, 0.68, 0.38, 1)
ACCENT_RED    = (0.82, 0.08, 0.08, 1)
ACCENT_ORANGE = (0.95, 0.55, 0.08, 1)
TEXT_WHITE    = (1, 1, 1, 1)
TEXT_DIM      = (0.6, 0.6, 0.6, 1)

def _bg(widget, color, radius=0):
    with widget.canvas.before:
        Color(*color)
        if radius:
            rr = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[radius])
        else:
            rr = Rectangle(pos=widget.pos, size=widget.size)
        widget.bind(
            pos=lambda i, v, r=rr: setattr(r, 'pos', v),
            size=lambda i, v, r=rr: setattr(r, 'size', v)
        )

class SauvegardeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        _bg(layout, BG_DARK)

        # Titre
        title = Label(
            text="[b]GESTION DES SAUVEGARDES[/b]",
            markup=True,
            font_size=20,
            color=ACCENT,
            size_hint=(1, None),
            height=50
        )
        layout.add_widget(title)

        # Bouton sauvegarde
        btn_sauvegarder = Button(
            text="CREER UNE SAUVEGARDE",
            size_hint=(1, None),
            height=60,
            font_size=16,
            bold=True,
            background_normal="",
            background_color=ACCENT_GREEN,
            color=TEXT_WHITE
        )
        _bg(btn_sauvegarder, ACCENT_GREEN, radius=10)
        btn_sauvegarder.bind(on_release=self.creer_sauvegarde)
        layout.add_widget(btn_sauvegarder)

        # Bouton restaurer
        btn_restaurer = Button(
            text="RESTAURER LA DERNIERE SAUVEGARDE",
            size_hint=(1, None),
            height=60,
            font_size=16,
            bold=True,
            background_normal="",
            background_color=ACCENT_ORANGE,
            color=TEXT_WHITE
        )
        _bg(btn_restaurer, ACCENT_ORANGE, radius=10)
        btn_restaurer.bind(on_release=self.restaurer_sauvegarde)
        layout.add_widget(btn_restaurer)

        # Liste des sauvegardes
        layout.add_widget(Label(
            text="[b]SAUVEGARDES EXISTANTES[/b]",
            markup=True,
            font_size=14,
            color=TEXT_WHITE,
            size_hint=(1, None),
            height=30
        ))

        # ScrollView pour la liste
        scroll = ScrollView(size_hint=(1, 1))
        self.liste_backups = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.liste_backups.bind(minimum_height=self.liste_backups.setter('height'))
        scroll.add_widget(self.liste_backups)
        layout.add_widget(scroll)

        # Bouton retour
        btn_retour = Button(
            text="< RETOUR",
            size_hint=(1, None),
            height=50,
            font_size=14,
            background_normal="",
            background_color=ACCENT_RED,
            color=TEXT_WHITE
        )
        _bg(btn_retour, ACCENT_RED, radius=8)
        btn_retour.bind(on_release=self.retour_accueil)
        layout.add_widget(btn_retour)

        self.add_widget(layout)

        # Charger la liste au demarrage
        Clock.schedule_once(lambda dt: self.actualiser_liste(), 0.5)

    def actualiser_liste(self):
        """Affiche la liste des sauvegardes"""
        # Vider la liste
        self.liste_backups.clear_widgets()

        # Recuperer les sauvegardes
        sauvegardes = lister_sauvegardes()

        if not sauvegardes:
            self.liste_backups.add_widget(Label(
                text="Aucune sauvegarde trouvee",
                color=TEXT_DIM,
                size_hint=(1, None),
                height=40
            ))
            return

        for backup in sauvegardes:
            # Conteneur pour chaque backup
            item = BoxLayout(size_hint=(1, None), height=100, spacing=10, padding=[10, 5])
            _bg(item, BG_CARD, radius=5)

            # Infos
            info = Label(
                text=f"[b]{backup['nom']}[/b]\n{backup['date']} - {backup['taille']:,} o",
                markup=True,
                color=TEXT_WHITE,
                size_hint=(0.7, 1),
                halign="left",
                valign="middle"
            )
            info.bind(size=lambda inst, v: setattr(inst, "text_size", (v[0] - 10, None)))
            item.add_widget(info)

            # Bouton supprimer
            btn_suppr = Button(
                text="SUPPRIMER",
                size_hint=(0.3, 0.8),
                background_normal="",
                background_color=ACCENT_RED,
                color=TEXT_WHITE,
                font_size=12,
                bold=True
            )
            _bg(btn_suppr, ACCENT_RED, radius=5)
            btn_suppr.bind(on_release=lambda x, chem=backup['chemin'], nom=backup['nom']: self.confirmer_suppression(chem, nom))
            item.add_widget(btn_suppr)

            self.liste_backups.add_widget(item)

    def confirmer_suppression(self, chemin, nom):
        """Demande confirmation avant suppression"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(
            text=f"Supprimer la sauvegarde :\n\n{nom}\n\nCette action est irreversible.\n\nContinuer ?",
            color=TEXT_WHITE,
            font_size=13,
            halign="center"
        ))

        btn_box = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        btn_oui = Button(text="OUI", background_color=ACCENT_RED, color=TEXT_WHITE)
        btn_non = Button(text="NON", background_color=ACCENT_GREEN, color=TEXT_WHITE)
        btn_box.add_widget(btn_oui)
        btn_box.add_widget(btn_non)
        content.add_widget(btn_box)

        popup = Popup(title="Confirmation suppression", content=content, size_hint=(0.8, 0.4))

        def confirmer(x):
            popup.dismiss()
            if supprimer_sauvegarde(chemin):
                self.show_message("Succes", "Sauvegarde supprimee avec succes")
                self.actualiser_liste()
            else:
                self.show_message("Erreur", "Echec de la suppression")

        btn_oui.bind(on_release=confirmer)
        btn_non.bind(on_release=popup.dismiss)
        popup.open()

    def creer_sauvegarde(self, instance):
        """Cree une nouvelle sauvegarde"""
        chemin = sauvegarder_base_donnees()
        if chemin:
            self.show_message("Succes", f"Sauvegarde creee avec succes !\n\n{os.path.basename(chemin)}")
            self.actualiser_liste()
        else:
            self.show_message("Erreur", "Echec de la creation de la sauvegarde\n\nVerifiez les permissions de stockage")

    def restaurer_sauvegarde(self, instance):
        """Restaure la derniere sauvegarde"""
        # Verifier s'il y a des sauvegardes
        sauvegardes = lister_sauvegardes()
        if not sauvegardes:
            self.show_message("Information", "Aucune sauvegarde disponible a restaurer")
            return

        # Demander confirmation
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(
            text="ATTENTION !\n\nLa restauration remplacera\nTOUTES les donnees actuelles.\n\nCette action est irreversible !\n\nContinuer ?",
            color=ACCENT_ORANGE,
            font_size=14,
            halign="center"
        ))

        btn_box = BoxLayout(size_hint=(1, None), height=50, spacing=10)
        btn_oui = Button(text="OUI, RESTAURER", background_color=ACCENT_RED, color=TEXT_WHITE, bold=True)
        btn_non = Button(text="NON", background_color=ACCENT_GREEN, color=TEXT_WHITE, bold=True)
        btn_box.add_widget(btn_oui)
        btn_box.add_widget(btn_non)
        content.add_widget(btn_box)

        popup = Popup(title="Confirmation restauration", content=content, size_hint=(0.85, 0.45))

        def confirmer(x):
            popup.dismiss()
            # Afficher un message de chargement
            self.show_message("Restauration", "Restauration en cours...\n\nVeuillez patienter...")
            if restaurer_derniere_sauvegarde():
                self.show_message("Succes", "Restauration reussie !\n\nL'application va redemarrer.")
                Clock.schedule_once(lambda dt: self.redemarrer_app(), 2)
            else:
                self.show_message("Erreur", "Echec de la restauration\n\nVerifiez que les sauvegardes sont accessibles")

        btn_oui.bind(on_release=confirmer)
        btn_non.bind(on_release=popup.dismiss)
        popup.open()

    def redemarrer_app(self):
        """Redemarre l'application"""
        from kivy.app import App
        App.get_running_app().stop()
        # Sur Android, forcer la fermeture
        if platform == 'android':
            import sys
            sys.exit(0)

    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=message, color=TEXT_WHITE, font_size=13, halign="center"))
        btn = Button(text="OK", size_hint=(1, None), height=40, font_size=14, bold=True)
        btn.background_normal = ""
        btn.background_color = ACCENT_GREEN
        btn.color = TEXT_WHITE
        popup = Popup(title=title, content=content, size_hint=(0.85, 0.4))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def retour_accueil(self, instance):
        self.manager.current = "accueil"
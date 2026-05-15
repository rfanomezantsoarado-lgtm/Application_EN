#Importation des bibliothèques utiles
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.app import App


# Largeur du menu
MENU_WIDTH = 280


# ===================================================
# ITEM MENU (ICONE + TEXTE)
# ===================================================
class MenuItem(BoxLayout):

    def __init__(self, text, icon, callback, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=55,
            spacing=15,
            padding=[20, 0, 10, 0],
            **kwargs
        )

        self.callback = callback

        with self.canvas.before:
            Color(0.07, 0.10, 0.22, 0.8)  # Plus transparent
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

        self.bind(
            pos=lambda i, v: setattr(self.bg, "pos", v),
            size=lambda i, v: setattr(self.bg, "size", v)
        )

        icon_img = Image(
            source=icon,
            size_hint=(None, None),
            size=(28, 28),
            pos_hint={"center_y": 0.5}
        )

        label = Label(
            text=text,
            color=(0.95, 0.95, 1, 1),
            font_size=16,
            halign="left",
            valign="middle"
        )

        label.bind(size=lambda i, v: setattr(i, "text_size", v))

        self.add_widget(icon_img)
        self.add_widget(label)

        self.bind(on_touch_down=self._on_touch)

    def _on_touch(self, instance, touch):
        if self.collide_point(*touch.pos):
            self.callback()
            return True
        return False


# ===================================================
# ECRAN ACCUEIL
# ===================================================
class AccueilScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = RelativeLayout()

        # ───────────────────────────────────────────────
        # FOND
        # ───────────────────────────────────────────────
        fond = Image(
            source="images/background.png",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1)
        )
        layout.add_widget(fond)

        # ───────────────────────────────────────────────
        # OVERLAY
        # ───────────────────────────────────────────────
        overlay = FloatLayout(size_hint=(1, 1))

        with overlay.canvas.before:
            Color(0, 0, 0, 0.30)
            self.overlay_rect = Rectangle(pos=overlay.pos, size=overlay.size)

        overlay.bind(
            pos=lambda i, v: setattr(self.overlay_rect, "pos", v),
            size=lambda i, v: setattr(self.overlay_rect, "size", v)
        )

        layout.add_widget(overlay)

        # ───────────────────────────────────────────────
        # BOUTON MENU (rectangle arrondi, en haut)
        # ───────────────────────────────────────────────
        self.menu_button = Button(
            text="MENU",
            size_hint=(0.15, 0.07),
            pos_hint={"right": 0.97, "top": 0.97},
            background_normal="",
            background_color=(0.08, 0.45, 0.82, 1),
            color=(1, 1, 1, 1),
            font_size=14,
            bold=True
        )

        # Rendre le bouton rectangulaire avec coins arrondis
        with self.menu_button.canvas.before:
            Color(0.08, 0.45, 0.82, 1)
            self.btn_bg = RoundedRectangle(pos=self.menu_button.pos, size=self.menu_button.size, radius=[10])

        def update_btn_bg(instance, value):
            self.btn_bg.pos = instance.pos
            self.btn_bg.size = instance.size

        self.menu_button.bind(pos=update_btn_bg, size=update_btn_bg)
        self.menu_button.background_color = (0, 0, 0, 0)  # Transparent pour laisser voir notre rectangle

        self.menu_button.bind(on_release=lambda x: self.toggle_drawer())
        layout.add_widget(self.menu_button)

        # ───────────────────────────────────────────────
        # DRAWER (MENU DROITE centré verticalement)
        # ───────────────────────────────────────────────
        self.drawer_open = False

        self.drawer = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),  # Changé pour hauteur personnalisée
            width=MENU_WIDTH,
            height=520,  # Hauteur augmentée pour inclure le bouton quitter
            pos=(self.width, (Window.height - 520) / 2),  # Centré verticalement
            padding=[20, 30, 20, 30],
            spacing=15
        )

        with self.drawer.canvas.before:
            Color(0.07, 0.10, 0.22, 0.85)  # Fond semi-transparent
            self.drawer_bg = RoundedRectangle(pos=self.drawer.pos, size=self.drawer.size, radius=[15])

        self.drawer.bind(
            pos=lambda i, v: setattr(self.drawer_bg, "pos", v),
            size=lambda i, v: setattr(self.drawer_bg, "size", v)
        )

        # TITRE MENU
        self.drawer.add_widget(Label(
            text="MENU",
            font_size=22,
            bold=True,
            size_hint_y=None,
            height=50,
            color=(1, 1, 1, 1)
        ))

        # ITEMS MENU
        menus = [
            ("Clients", "images/user.png", "clients"),
            ("Produits", "images/produit.png", "produits"),
            ("Commande", "images/commande.png", "commande"),
            ("Historique", "images/facturation.png", "historique_commande"),
        ]

        for texte, icon, dest in menus:

            def make_action(d=dest, t=texte):
                def action():
                    self.toggle_drawer()
                    self.menu_button.text = t
                    self.manager.transition.direction = "left"
                    self.manager.current = d
                return action

            self.drawer.add_widget(MenuItem(texte, icon, make_action()))

        # SEPARATEUR
        separator = BoxLayout(
            size_hint_y=None,
            height=20
        )
        with separator.canvas.before:
            Color(0.5, 0.6, 0.75, 0.3)
            Rectangle(pos=separator.pos, size=separator.size)
        self.drawer.add_widget(separator)

        # BOUTON QUITTER
        quit_item = MenuItem(
            "Quitter",
            "images/quit.png",  # Assurez-vous d'avoir cette icône ou changez le chemin
            self.quit_app
        )
        self.drawer.add_widget(quit_item)

        layout.add_widget(self.drawer)

        # ───────────────────────────────────────────────
        # FOOTER (en bas)
        # ───────────────────────────────────────────────
        layout.add_widget(Label(
            text="© 2026 EN App — v1.0",
            font_size=11,
            color=(0.5, 0.6, 0.75, 0.8),
            size_hint=(1, None),
            height=30,
            pos_hint={"center_x": 0.5, "y": 0.01}
        ))

        self.add_widget(layout)

        # Ajustement dynamique
        self.bind(size=self._update_drawer)

    # ===================================================
    # FONCTION POUR QUITTER L'APPLICATION
    # ===================================================
    def quit_app(self):
        """Ferme l'application"""
        self.toggle_drawer()  # Ferme le menu
        App.get_running_app().stop()  # Arrête l'application
        Window.close()  # Ferme la fenêtre

    # ===================================================
    # OUVERTURE / FERMETURE MENU
    # ===================================================
    def toggle_drawer(self):

        if self.drawer_open:
            # Animation pour fermer vers la droite
            anim = Animation(x=self.width, d=0.2)
            anim.start(self.drawer)
            self.drawer_open = False
        else:
            # Animation pour ouvrir depuis la droite, centré verticalement
            target_x = self.width - MENU_WIDTH
            anim = Animation(x=target_x, d=0.2)
            anim.start(self.drawer)
            self.drawer_open = True

    # ===================================================
    # RESPONSIVE
    # ===================================================
    def _update_drawer(self, *args):
        # Mettre à jour la position du drawer pour garder le centrage vertical
        if hasattr(self, 'drawer'):
            self.drawer.y = (self.height - self.drawer.height) / 2

            if self.drawer_open:
                self.drawer.x = self.width - MENU_WIDTH
            else:
                self.drawer.x = self.width

    # ===================================================
    # RESET
    # ===================================================
    def on_enter(self):
        self.menu_button.text = "MENU"
        # Mettre à jour la position du drawer lors de l'entrée
        self._update_drawer()

    # ===================================================
    # CLEAN EXIT
    # ===================================================
    def on_pre_leave(self):
        if self.drawer_open:
            self.toggle_drawer()
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
from kivy.metrics import dp, sp
import os

# Largeur du menu - augmentée pour mobile
MENU_WIDTH = dp(320)  # Utilisation de dp pour l'échelle


# ===================================================
# ITEM MENU (ICONE + TEXTE)
# ===================================================
class MenuItem(BoxLayout):

    def __init__(self, text, icon, callback, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(65),  # Augmenté de 55 à 65
            spacing=dp(20),  # Augmenté de 15 à 20
            padding=[dp(25), dp(10), dp(15), dp(10)],  # Padding augmenté
            **kwargs
        )

        self.callback = callback

        with self.canvas.before:
            Color(0.07, 0.10, 0.22, 0.85)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])

        self.bind(
            pos=lambda i, v: setattr(self.bg, "pos", v),
            size=lambda i, v: setattr(self.bg, "size", v)
        )

        icon_img = Image(
            source=icon,
            size_hint=(None, None),
            size=(dp(36), dp(36)),  # Augmenté de 28 à 36
            pos_hint={"center_y": 0.5}
        )

        label = Label(
            text=text,
            color=(0.95, 0.95, 1, 1),
            font_size=sp(18),  # Augmenté de 16 à 18
            halign="left",
            valign="middle",
            size_hint_x=0.8
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
        
        # Obtenir les dimensions de l'écran
        self.screen_width = Window.width
        self.screen_height = Window.height

        layout = RelativeLayout()

        # ───────────────────────────────────────────────
        # FOND
        # ───────────────────────────────────────────────
        background_path = os.path.join("images", "background.png")
        fond = Image(
            source=background_path,
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
            Color(0, 0, 0, 0.35)
            self.overlay_rect = Rectangle(pos=overlay.pos, size=overlay.size)

        overlay.bind(
            pos=lambda i, v: setattr(self.overlay_rect, "pos", v),
            size=lambda i, v: setattr(self.overlay_rect, "size", v)
        )

        layout.add_widget(overlay)

        # ───────────────────────────────────────────────
        # BOUTON MENU (plus grand et visible)
        # ───────────────────────────────────────────────
        self.menu_button = Button(
            text="MENU",
            size_hint=(None, None),  # Changé pour taille fixe en dp
            width=dp(100),  # Largeur fixe en dp
            height=dp(50),  # Hauteur fixe en dp
            pos_hint={"right": 0.95, "top": 0.95},
            background_normal="",
            background_color=(0.08, 0.45, 0.82, 1),
            color=(1, 1, 1, 1),
            font_size=sp(18),  # Augmenté
            bold=True
        )

        # Rendre le bouton rectangulaire avec coins arrondis
        with self.menu_button.canvas.before:
            Color(0.08, 0.45, 0.82, 1)
            self.btn_bg = RoundedRectangle(pos=self.menu_button.pos, size=self.menu_button.size, radius=[dp(12)])

        def update_btn_bg(instance, value):
            self.btn_bg.pos = instance.pos
            self.btn_bg.size = instance.size

        self.menu_button.bind(pos=update_btn_bg, size=update_btn_bg)
        self.menu_button.background_color = (0, 0, 0, 0)

        self.menu_button.bind(on_release=lambda x: self.toggle_drawer())
        layout.add_widget(self.menu_button)

        # ───────────────────────────────────────────────
        # DRAWER (MENU - centré verticalement)
        # ───────────────────────────────────────────────
        self.drawer_open = False
        
        # Hauteur du menu basée sur l'écran
        menu_height = min(dp(600), self.screen_height * 0.7)  # Max 70% de l'écran

        self.drawer = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=MENU_WIDTH,
            height=menu_height,
            pos=(self.width, (self.screen_height - menu_height) / 2),
            padding=[dp(25), dp(35), dp(25), dp(35)],  # Padding augmenté
            spacing=dp(20)
        )

        with self.drawer.canvas.before:
            Color(0.07, 0.10, 0.22, 0.92)
            self.drawer_bg = RoundedRectangle(pos=self.drawer.pos, size=self.drawer.size, radius=[dp(20)])

        self.drawer.bind(
            pos=lambda i, v: setattr(self.drawer_bg, "pos", v),
            size=lambda i, v: setattr(self.drawer_bg, "size", v)
        )

        # TITRE MENU
        self.drawer.add_widget(Label(
            text="MENU",
            font_size=sp(28),  # Augmenté
            bold=True,
            size_hint_y=None,
            height=dp(60),  # Augmenté
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
            height=dp(25)
        )
        with separator.canvas.before:
            Color(0.5, 0.6, 0.75, 0.4)
            Rectangle(pos=separator.pos, size=separator.size)
        self.drawer.add_widget(separator)

        # BOUTON QUITTER
        quit_item = MenuItem(
            "Quitter",
            "images/quit.png",
            self.quit_app
        )
        self.drawer.add_widget(quit_item)

        layout.add_widget(self.drawer)

        # ───────────────────────────────────────────────
        # TITRE CENTRAL (optionnel pour remplir l'espace)
        # ───────────────────────────────────────────────
        title_label = Label(
            text="[b]E & N ENTREPRISE[/b]",
            markup=True,
            font_size=sp(32),
            color=(1, 1, 1, 0.95),
            size_hint=(1, None),
            height=dp(80),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            halign="center",
            valign="middle"
        )
        title_label.bind(size=lambda inst, v: setattr(inst, "text_size", v))
        layout.add_widget(title_label)
        
        # Sous-titre
        subtitle_label = Label(
            text="Materiaux de Construction",
            font_size=sp(18),
            color=(0.8, 0.8, 0.9, 0.9),
            size_hint=(1, None),
            height=dp(40),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            halign="center",
            valign="middle"
        )
        subtitle_label.bind(size=lambda inst, v: setattr(inst, "text_size", v))
        layout.add_widget(subtitle_label)

        # ───────────────────────────────────────────────
        # FOOTER (en bas)
        # ───────────────────────────────────────────────
        layout.add_widget(Label(
            text="© 2026 EN App — v1.0",
            font_size=sp(12),  # Augmenté
            color=(0.5, 0.6, 0.75, 0.9),
            size_hint=(1, None),
            height=dp(40),  # Augmenté
            pos_hint={"center_x": 0.5, "y": 0.02}
        ))

        self.add_widget(layout)
        
        # Lier l'événement de redimensionnement
        self.bind(size=self._update_drawer)
        Window.bind(on_resize=self._on_window_resize)

    # ===================================================
    # FONCTION POUR QUITTER L'APPLICATION
    # ===================================================
    def quit_app(self):
        """Ferme l'application"""
        self.toggle_drawer()
        App.get_running_app().stop()
        Window.close()

    # ===================================================
    # OUVERTURE / FERMETURE MENU
    # ===================================================
    def toggle_drawer(self):
        if self.drawer_open:
            anim = Animation(x=self.width, d=0.25, t='out_quad')
            anim.start(self.drawer)
            self.drawer_open = False
        else:
            target_x = self.width - MENU_WIDTH
            anim = Animation(x=target_x, d=0.25, t='out_quad')
            anim.start(self.drawer)
            self.drawer_open = True

    # ===================================================
    # RESPONSIVE
    # ===================================================
    def _update_drawer(self, *args):
        """Met à jour la position du drawer"""
        if hasattr(self, 'drawer'):
            # Recalculer la hauteur du menu en fonction de l'écran
            new_height = min(dp(600), self.height * 0.7)
            self.drawer.height = new_height
            self.drawer.y = (self.height - new_height) / 2
            
            if self.drawer_open:
                self.drawer.x = self.width - MENU_WIDTH
            else:
                self.drawer.x = self.width
                
            # Mettre à jour la taille du bouton menu
            if hasattr(self, 'menu_button'):
                self.menu_button.width = dp(100)
                self.menu_button.height = dp(50)
                self.menu_button.font_size = sp(18)

    def _on_window_resize(self, window, width, height):
        """Callback pour le redimensionnement de la fenêtre"""
        self.screen_width = width
        self.screen_height = height
        self._update_drawer()

    # ===================================================
    # RESET
    # ===================================================
    def on_enter(self):
        """Appelé quand l'écran est affiché"""
        self.menu_button.text = "MENU"
        self._update_drawer()

    # ===================================================
    # CLEAN EXIT
    # ===================================================
    def on_pre_leave(self):
        if self.drawer_open:
            self.toggle_drawer()

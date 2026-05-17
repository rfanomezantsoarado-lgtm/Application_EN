# ===================================================
# IMPORTATION DES BIBLIOTHEQUES
# ===================================================

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock

from database import (
    init_database,
    ajouter_produit_db,
    get_all_produits,
    supprimer_produit_db,
    modifier_produit_db
)

# ===================================================
# COULEURS
# ===================================================

BG_DARK      = (0.04, 0.07, 0.16, 1)
BG_CARD      = (0.07, 0.11, 0.22, 1)
ACCENT       = (0.08, 0.45, 0.82, 1)
ACCENT_GREEN = (0.05, 0.68, 0.38, 1)
ACCENT_RED   = (0.82, 0.08, 0.08, 1)
ACCENT_ORANGE = (0.95, 0.55, 0.08, 1)

TEXT_MAIN    = (0.92, 0.95, 1, 1)
TEXT_DIM     = (0.55, 0.65, 0.8, 1)

ROW_ODD      = (0.10, 0.16, 0.30, 1)
ROW_EVEN     = (0.07, 0.12, 0.24, 1)

HEADER_BG    = (0.05, 0.35, 0.65, 1)
BAR_TOP      = (0.05, 0.08, 0.18, 1)


# ===================================================
# FOND
# ===================================================

def _bg(widget, color, radius=0):
    with widget.canvas.before:
        Color(*color)
        if radius:
            rr = RoundedRectangle(
                pos=widget.pos,
                size=widget.size,
                radius=[radius]
            )
        else:
            rr = Rectangle(
                pos=widget.pos,
                size=widget.size
            )
        widget.bind(
            pos=lambda i, v, r=rr: setattr(r, 'pos', v),
            size=lambda i, v, r=rr: setattr(r, 'size', v)
        )


# ===================================================
# CELLULE TABLEAU
# ===================================================

def make_cell(text, w, bg_color, bold=False, font_size=13):
    lbl = Label(
        text=f"[b]{text}[/b]" if bold else str(text),
        markup=bold,
        size_hint=(None, None),
        size=(w, dp(48)),  # Augmenté de 40 à 48
        font_size=font_size,
        color=(1, 1, 1, 1),
        halign="center",
        valign="middle"
    )
    lbl.bind(
        size=lambda inst, v:
        setattr(inst, "text_size", v)
    )
    _bg(lbl, bg_color)
    return lbl


# ===================================================
# ECRAN PRODUITS
# ===================================================

class ProduitScreen(Screen):

    HEADERS = [
        "Nom du produit",
        "Prix d'achat",
        "Prix de vente",
        "Modifier",
        "Supprimer"
    ]

    # Largeurs augmentées pour mobile
    COL_WIDTHS = [dp(160), dp(110), dp(110), dp(90), dp(90)]
    ROW_H = dp(48)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialisation base
        init_database()

        # Variables modification
        self.mode_modification = False
        self.produit_selectionne = None

        # Chargement produits
        self.produits = get_all_produits()

        # ===================================================
        # ROOT
        # ===================================================
        root = BoxLayout(orientation="vertical")
        _bg(root, BG_DARK)

        # ===================================================
        # BARRE HAUTE
        # ===================================================
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(65),  # Augmenté
            padding=[dp(10), dp(5), dp(10), dp(5)],
            spacing=dp(8)
        )
        _bg(top_bar, BAR_TOP)

        btn_back = Button(
            text="< RETOUR",
            size_hint=(None, 1),
            width=dp(100),  # Augmenté
            font_size=sp(14),  # Augmenté
            bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(0.55, 0.78, 1, 1)
        )
        btn_back.bind(
            on_release=lambda *a:
            setattr(self.manager, "current", "accueil")
        )
        top_bar.add_widget(btn_back)

        title_label = Label(
            text="[b]GESTION PRODUITS[/b]",
            markup=True,
            font_size=sp(20),  # Augmenté
            color=TEXT_MAIN,
            size_hint=(1, 1),
            halign="center",
            valign="middle"
        )
        title_label.bind(size=lambda inst, v: setattr(inst, "text_size", v))
        top_bar.add_widget(title_label)

        # Espace vide pour équilibrer
        spacer = Label(size_hint=(None, 1), width=dp(100))
        top_bar.add_widget(spacer)

        root.add_widget(top_bar)

        # ===================================================
        # FORMULAIRE
        # ===================================================
        form_outer = BoxLayout(
            size_hint=(1, None),
            height=dp(320),  # Augmenté
            padding=[dp(12), dp(10), dp(12), dp(10)]
        )
        form_card = BoxLayout(
            orientation="vertical",
            padding=[dp(14), dp(12), dp(14), dp(12)],
            spacing=dp(8)
        )
        _bg(form_card, BG_CARD, radius=dp(14))

        self.lbl_form = Label(
            text="[b]AJOUTER UN PRODUIT[/b]",
            markup=True,
            font_size=sp(15),  # Augmenté
            color=ACCENT,
            size_hint=(1, None),
            height=dp(32),
            halign="center"
        )
        form_card.add_widget(self.lbl_form)

        fields = [
            ("Nom du produit *", "nom"),
            ("Prix d'achat (Ar)", "prix_achat"),
            ("Prix de vente (Ar)", "prix_vente"),
        ]

        self._inputs = {}

        for hint, key in fields:
            ti = TextInput(
                hint_text=hint,
                multiline=False,
                font_size=sp(14),
                foreground_color=TEXT_MAIN,
                hint_text_color=(0.4, 0.5, 0.65, 1),
                background_color=(0.1, 0.16, 0.30, 1),
                cursor_color=ACCENT,
                size_hint=(1, None),
                height=dp(52),  # Augmenté
                padding=[dp(12), dp(12)]
            )
            form_card.add_widget(ti)
            self._inputs[key] = ti

        self.nom = self._inputs["nom"]
        self.prix_achat = self._inputs["prix_achat"]
        self.prix_vente = self._inputs["prix_vente"]

        # Formatage des champs numériques
        self.prix_achat.bind(text=self.format_prix)
        self.prix_vente.bind(text=self.format_prix)

        form_outer.add_widget(form_card)
        root.add_widget(form_outer)

        # ===================================================
        # BOUTON
        # ===================================================
        btn_area = BoxLayout(
            size_hint=(1, None),
            height=dp(60),  # Augmenté
            padding=[dp(40), dp(8), dp(40), dp(8)]
        )
        self.btn_save = Button(
            text="ENREGISTRER",
            font_size=sp(16),  # Augmenté
            bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )
        _bg(self.btn_save, ACCENT_GREEN, radius=dp(12))
        self.btn_save.bind(on_release=self.ajouter_ou_modifier_produit)
        btn_area.add_widget(self.btn_save)
        root.add_widget(btn_area)

        # ===================================================
        # LABEL COUNT
        # ===================================================
        self.lbl_count = Label(
            text=f"📦 LISTE DES PRODUITS - {len(self.produits)} enregistré(s)",
            font_size=sp(12),
            color=TEXT_DIM,
            size_hint=(1, None),
            height=dp(32),
            halign="left",
            valign="middle",
            bold=True
        )
        self.lbl_count.bind(
            size=lambda inst, v:
            setattr(inst, "text_size", (v[0] - dp(14), None))
        )
        root.add_widget(self.lbl_count)

        # ===================================================
        # TABLE
        # ===================================================
        total_w = sum(self.COL_WIDTHS)

        self.table = GridLayout(
            cols=5,
            size_hint=(None, None),
            width=total_w,
            row_default_height=self.ROW_H,
            row_force_default=True,
            spacing=0,
            padding=0
        )
        self.table.bind(minimum_height=self.table.setter('height'))

        # Headers
        for h, w in zip(self.HEADERS, self.COL_WIDTHS):
            self.table.add_widget(
                make_cell(h, w, HEADER_BG, bold=True, font_size=sp(12))
            )

        # Produits
        self.refresh_table()

        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=True,
            bar_width=dp(6),
            bar_color=list(ACCENT[:3]) + [0.8]
        )
        scroll.add_widget(self.table)

        table_box = BoxLayout(
            size_hint=(1, 1),
            padding=[dp(6), dp(4), dp(6), dp(6)]
        )
        table_box.add_widget(scroll)
        root.add_widget(table_box)

        self.add_widget(root)

    # ===================================================
    # FORMATAGE DES PRIX
    # ===================================================
    def format_prix(self, instance, value):
        """Formatte les champs de prix pour n'accepter que des nombres"""
        if value:
            # Supprimer tout ce qui n'est pas un nombre
            cleaned = ''.join(c for c in value if c.isdigit() or c == '.')
            if cleaned != value:
                instance.text = cleaned

    # ===================================================
    # REFRESH TABLE
    # ===================================================
    def refresh_table(self):
        # Supprimer tout sauf les headers
        enfants = list(self.table.children)
        nb_header = len(self.HEADERS)
        lignes = enfants[:-nb_header] if len(enfants) > nb_header else []
        for enfant in lignes:
            self.table.remove_widget(enfant)

        self.produits = get_all_produits()

        for idx, produit in enumerate(self.produits):
            row_color = ROW_ODD if idx % 2 == 0 else ROW_EVEN
            produit_id = produit[0]
            nom = str(produit[1]) if produit[1] else ""
            prix_achat = f"{float(produit[2]):,.0f}" if produit[2] else "0"
            prix_vente = f"{float(produit[3]):,.0f}" if produit[3] else "0"

            valeurs = [nom, prix_achat, prix_vente]

            # Troncature des noms trop longs
            for i, val in enumerate(valeurs):
                if i == 0 and len(val) > 20:
                    val = val[:18] + ".."
                self.table.add_widget(
                    make_cell(val, self.COL_WIDTHS[i], row_color, bold=False, font_size=sp(11))
                )

            # Bouton Modifier
            btn_modif = Button(
                text="MODIFIER",
                size_hint=(None, None),
                size=(self.COL_WIDTHS[3], self.ROW_H),
                font_size=sp(11),
                bold=True,
                background_normal="",
                background_color=ACCENT,
                color=TEXT_MAIN
            )
            _bg(btn_modif, ACCENT, radius=dp(6))
            btn_modif.bind(on_release=lambda x, p=produit: self.charger_modification(p))
            self.table.add_widget(btn_modif)

            # Bouton Supprimer
            btn_delete = Button(
                text="SUPPRIMER",
                size_hint=(None, None),
                size=(self.COL_WIDTHS[4], self.ROW_H),
                font_size=sp(11),
                bold=True,
                background_normal="",
                background_color=ACCENT_RED,
                color=TEXT_MAIN
            )
            _bg(btn_delete, ACCENT_RED, radius=dp(6))
            btn_delete.bind(on_release=lambda x, pid=produit_id: self.supprimer_produit(pid))
            self.table.add_widget(btn_delete)

        # Mettre à jour le compteur
        self.lbl_count.text = f"📦 LISTE DES PRODUITS - {len(self.produits)} enregistré(s)"

    # ===================================================
    # AJOUT / MODIFICATION
    # ===================================================
    def ajouter_ou_modifier_produit(self, instance):
        nom = self.nom.text.strip()
        prix_achat = self.prix_achat.text.strip()
        prix_vente = self.prix_vente.text.strip()

        if not nom:
            self.nom.background_color = ACCENT_RED
            Clock.schedule_once(
                lambda dt: setattr(self.nom, 'background_color', (0.1, 0.16, 0.30, 1)), 1
            )
            self.show_message("Erreur", "Le nom du produit est obligatoire")
            return

        # Conversion des prix
        try:
            prix_achat_float = float(prix_achat) if prix_achat else 0
            prix_vente_float = float(prix_vente) if prix_vente else 0
        except ValueError:
            self.show_message("Erreur", "Les prix doivent être des nombres valides")
            return

        if prix_achat_float > prix_vente_float:
            self.show_message("Avertissement", 
                            f"Le prix d'achat ({prix_achat_float:,.0f} Ar) "
                            f"est supérieur au prix de vente ({prix_vente_float:,.0f} Ar)\n\n"
                            "Voulez-vous continuer ?", self._confirmer_ajout)
            self._ajout_en_attente = (nom, prix_achat_float, prix_vente_float)
            return

        self._executer_ajout_ou_modification(nom, prix_achat_float, prix_vente_float)

    def _confirmer_ajout(self, confirmation):
        if confirmation and hasattr(self, '_ajout_en_attente'):
            nom, prix_achat, prix_vente = self._ajout_en_attente
            self._executer_ajout_ou_modification(nom, prix_achat, prix_vente)
            delattr(self, '_ajout_en_attente')

    def _executer_ajout_ou_modification(self, nom, prix_achat, prix_vente):
        if self.mode_modification:
            modifier_produit_db(
                self.produit_selectionne,
                nom,
                str(prix_achat),
                str(prix_vente)
            )
            message = f"Produit '{nom}' modifié avec succès"
        else:
            # Vérifier si le produit existe déjà
            for p in self.produits:
                if p[1].lower() == nom.lower():
                    self.show_message("Erreur", f"Le produit '{nom}' existe déjà")
                    return
            ajouter_produit_db(nom, str(prix_achat), str(prix_vente))
            message = f"Produit '{nom}' ajouté avec succès"

        # Reset
        self.mode_modification = False
        self.produit_selectionne = None
        self.lbl_form.text = "[b]AJOUTER UN PRODUIT[/b]"
        self.btn_save.text = "ENREGISTRER"

        for ti in self._inputs.values():
            ti.text = ""

        self.refresh_table()
        self.show_message("Succès", message)

    # ===================================================
    # CHARGER MODIFICATION
    # ===================================================
    def charger_modification(self, produit):
        self.mode_modification = True
        self.produit_selectionne = produit[0]
        self.nom.text = str(produit[1])
        self.prix_achat.text = str(produit[2])
        self.prix_vente.text = str(produit[3])
        self.lbl_form.text = "[b]MODIFIER LE PRODUIT[/b]"
        self.btn_save.text = "MODIFIER"

    # ===================================================
    # SUPPRIMER
    # ===================================================
    def supprimer_produit(self, produit_id):
        # Trouver le nom du produit
        produit_nom = ""
        for p in self.produits:
            if p[0] == produit_id:
                produit_nom = p[1]
                break

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        content.add_widget(Label(
            text=f"Voulez-vous vraiment supprimer\nle produit '{produit_nom}' ?",
            color=TEXT_MAIN,
            font_size=sp(14),
            halign="center"
        ))
        btn_box = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(12))
        btn_oui = Button(text="SUPPRIMER", font_size=sp(14), bold=True)
        btn_non = Button(text="ANNULER", font_size=sp(14))
        btn_box.add_widget(btn_oui)
        btn_box.add_widget(btn_non)
        content.add_widget(btn_box)

        popup = Popup(
            title="Confirmation",
            content=content,
            size_hint=(0.8, 0.35),
            background_color=BG_CARD,
            title_size=sp(15)
        )

        btn_oui.bind(on_release=lambda x: self._executer_suppression(produit_id, popup))
        btn_non.bind(on_release=popup.dismiss)
        popup.open()

    def _executer_suppression(self, produit_id, popup):
        supprimer_produit_db(produit_id)
        popup.dismiss()
        self.refresh_table()
        self.show_message("Succès", "Produit supprimé avec succès")

    # ===================================================
    # MESSAGE POPUP
    # ===================================================
    def show_message(self, title, message, callback=None):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        content.add_widget(Label(
            text=message,
            color=TEXT_MAIN,
            font_size=sp(14),
            halign="center",
            valign="middle"
        ))
        btn = Button(
            text="OK",
            size_hint=(1, None),
            height=dp(45),
            font_size=sp(14),
            bold=True,
            background_normal="",
            background_color=ACCENT_GREEN,
            color=TEXT_MAIN
        )
        _bg(btn, ACCENT_GREEN, radius=dp(8))
        content.add_widget(btn)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.35),
            background_color=BG_CARD,
            title_size=sp(15),
            title_color=ACCENT
        )
        btn.bind(on_release=popup.dismiss)
        if callback:
            btn.bind(on_release=lambda x: callback(True))
        popup.open()

    # ===================================================
    # ON ENTER
    # ===================================================
    def on_enter(self):
        """Rafraîchir la liste quand on revient sur l'écran"""
        self.refresh_table()

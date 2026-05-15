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
from kivy.graphics import Color, RoundedRectangle, Rectangle

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

TEXT_MAIN    = (0.92, 0.95, 1,    1)
TEXT_DIM     = (0.55, 0.65, 0.8,  1)

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
        size=(w, 40),
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

    COL_WIDTHS = [140, 100, 100, 90, 90]

    ROW_H = 40

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
            height=56,
            padding=[8, 0, 8, 0],
            spacing=4
        )

        _bg(top_bar, BAR_TOP)

        btn_back = Button(
            text="< Retour",
            size_hint=(None, 1),
            width=88,
            font_size=13,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(0.55, 0.78, 1, 1)
        )

        btn_back.bind(
            on_release=lambda *a:
            setattr(self.manager, "current", "accueil")
        )

        top_bar.add_widget(btn_back)

        top_bar.add_widget(Label(
            text="[b]GESTION PRODUITS[/b]",
            markup=True,
            font_size=18,
            color=TEXT_MAIN
        ))

        root.add_widget(top_bar)

        # ===================================================
        # FORMULAIRE
        # ===================================================

        form_outer = BoxLayout(
            size_hint=(1, None),
            height=210,
            padding=[12, 8, 12, 8]
        )

        form_card = BoxLayout(
            orientation="vertical",
            padding=[12, 8, 12, 8],
            spacing=6
        )

        _bg(form_card, BG_CARD, radius=14)

        self.lbl_form = Label(
            text="[b]Nouveau produit[/b]",
            markup=True,
            font_size=14,
            color=(0.55, 0.75, 1, 1),
            size_hint=(1, None),
            height=24
        )

        form_card.add_widget(self.lbl_form)

        fields = [
            ("Nom du produit", "nom"),
            ("Prix d'achat", "prix_achat"),
            ("Prix de vente", "prix_vente"),
        ]

        self._inputs = {}

        for hint, key in fields:

            ti = TextInput(
                hint_text=hint,
                multiline=False,
                font_size=14,
                foreground_color=TEXT_MAIN,
                hint_text_color=(0.4, 0.5, 0.65, 1),
                background_color=(0.1, 0.16, 0.30, 1),
                cursor_color=ACCENT,
                size_hint=(1, None),
                height=40,
                padding=[10, 10]
            )

            form_card.add_widget(ti)

            self._inputs[key] = ti

        self.nom = self._inputs["nom"]
        self.prix_achat = self._inputs["prix_achat"]
        self.prix_vente = self._inputs["prix_vente"]

        form_outer.add_widget(form_card)

        root.add_widget(form_outer)

        # ===================================================
        # BOUTON
        # ===================================================

        btn_area = BoxLayout(
            size_hint=(1, None),
            height=52,
            padding=[36, 4, 36, 4]
        )

        self.btn_save = Button(
            text="ENREGISTRER",
            font_size=15,
            bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )

        _bg(self.btn_save, ACCENT_GREEN, radius=10)

        self.btn_save.bind(
            on_release=self.ajouter_ou_modifier_produit
        )

        btn_area.add_widget(self.btn_save)

        root.add_widget(btn_area)

        # ===================================================
        # LABEL COUNT
        # ===================================================

        self.lbl_count = Label(
            text=f"Liste des produits - {len(self.produits)} enregistre(s)",
            font_size=12,
            color=TEXT_DIM,
            size_hint=(1, None),
            height=26,
            halign="left",
            valign="middle"
        )

        self.lbl_count.bind(
            size=lambda inst, v:
            setattr(inst, "text_size", (v[0] - 14, None))
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

        self.table.bind(
            minimum_height=self.table.setter('height')
        )

        # Headers
        for h, w in zip(self.HEADERS, self.COL_WIDTHS):

            self.table.add_widget(
                make_cell(h, w, HEADER_BG, bold=True)
            )

        # Produits
        self.refresh_table()

        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=True,
            bar_width=4,
            bar_color=list(ACCENT[:3]) + [0.8]
        )

        scroll.add_widget(self.table)

        table_box = BoxLayout(
            size_hint=(1, 1),
            padding=[6, 2, 6, 6]
        )

        table_box.add_widget(scroll)

        root.add_widget(table_box)

        self.add_widget(root)

    # ===================================================
    # REFRESH TABLE
    # ===================================================

    def refresh_table(self):

        self.table.clear_widgets()

        # Headers
        for h, w in zip(self.HEADERS, self.COL_WIDTHS):

            self.table.add_widget(
                make_cell(h, w, HEADER_BG, bold=True)
            )

        self.produits = get_all_produits()

        for idx, produit in enumerate(self.produits):

            row_color = ROW_ODD if idx % 2 == 0 else ROW_EVEN

            produit_id = produit[0]

            nom = produit[1]
            prix_achat = produit[2]
            prix_vente = produit[3]

            valeurs = [nom, prix_achat, prix_vente]

            for val, w in zip(valeurs, self.COL_WIDTHS[:3]):

                self.table.add_widget(
                    make_cell(val, w, row_color)
                )

            # Modifier
            btn_modif = Button(
                text="Modifier",
                size_hint=(None, None),
                size=(90, 40),
                background_normal="",
                background_color=(0.08, 0.45, 0.82, 1)
            )

            btn_modif.bind(
                on_release=lambda x, p=produit:
                self.charger_modification(p)
            )

            self.table.add_widget(btn_modif)

            # Supprimer
            btn_delete = Button(
                text="Supprimer",
                size_hint=(None, None),
                size=(90, 40),
                background_normal="",
                background_color=(0.75, 0.15, 0.15, 1)
            )

            btn_delete.bind(
                on_release=lambda x, pid=produit_id:
                self.supprimer_produit(pid)
            )

            self.table.add_widget(btn_delete)

    # ===================================================
    # AJOUT / MODIFICATION
    # ===================================================

    def ajouter_ou_modifier_produit(self, instance):

        nom = self.nom.text.strip()

        prix_achat = self.prix_achat.text.strip()

        prix_vente = self.prix_vente.text.strip()

        if not nom:

            self.nom.background_color = (0.35, 0.08, 0.08, 1)

            from kivy.clock import Clock

            Clock.schedule_once(
                lambda dt:
                setattr(
                    self.nom,
                    'background_color',
                    (0.1, 0.16, 0.30, 1)
                ),
                1
            )

            return

        if self.mode_modification:

            modifier_produit_db(
                self.produit_selectionne,
                nom,
                prix_achat,
                prix_vente
            )

        else:

            ajouter_produit_db(
                nom,
                prix_achat,
                prix_vente
            )

        # Reset
        self.mode_modification = False

        self.produit_selectionne = None

        self.lbl_form.text = "[b]Nouveau produit[/b]"

        self.btn_save.text = "ENREGISTRER"

        for ti in self._inputs.values():
            ti.text = ""

        self.refresh_table()

        self.lbl_count.text = (
            f"Liste des produits - "
            f"{len(self.produits)} enregistre(s)"
        )

    # ===================================================
    # CHARGER MODIFICATION
    # ===================================================

    def charger_modification(self, produit):

        self.mode_modification = True

        self.produit_selectionne = produit[0]

        self.nom.text = str(produit[1])

        self.prix_achat.text = str(produit[2])

        self.prix_vente.text = str(produit[3])

        self.lbl_form.text = "[b]Modification du produit[/b]"

        self.btn_save.text = "MODIFIER"

    # ===================================================
    # SUPPRIMER
    # ===================================================

    def supprimer_produit(self, produit_id):

        supprimer_produit_db(produit_id)

        self.refresh_table()

        self.lbl_count.text = (
            f"Liste des produits - "
            f"{len(self.produits)} enregistre(s)"
        )
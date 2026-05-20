#Importation des bibliothèques utiles
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock
from database import init_database, ajouter_client_db, get_all_clients


# ===================================================
# COULEURS
# ===================================================
BG_DARK      = (0.04, 0.07, 0.16, 1)
BG_CARD      = (0.07, 0.11, 0.22, 1)
ACCENT       = (0.08, 0.45, 0.82, 1)
ACCENT_GREEN = (0.05, 0.68, 0.38, 1)
ACCENT_RED   = (0.82, 0.08, 0.08, 1)
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

    text = "" if text is None else str(text)

    lbl = Label(
        text=f"[b]{text}[/b]" if bold else text,
        markup=True if bold else False,
        size_hint=(None, None),
        size=(w, dp(48)),
        font_size=font_size,
        color=(1, 1, 1, 1),
        halign="center",
        valign="middle"
    )

    lbl.bind(
        size=lambda inst, v: setattr(inst, "text_size", v)
    )

    _bg(lbl, bg_color)

    return lbl


# ===================================================
# ECRAN CLIENT
# ===================================================
class ClientScreen(Screen):

    HEADERS = ["Nom", "Adresse", "Stat", "Contact", "Responsable"]

    COL_WIDTHS = [
        dp(130),
        dp(140),
        dp(110),
        dp(110),
        dp(120)
    ]

    ROW_H = dp(48)

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        # ==========================================
        # INITIALISATION DB
        # ==========================================
        init_database()

        self.clients = []

        clients_data = get_all_clients()

        for client in clients_data:

            self.clients.append([
                str(client[1]) if client[1] else "",
                str(client[2]) if client[2] else "",
                str(client[3]) if client[3] else "",
                str(client[4]) if client[4] else "",
                str(client[5]) if client[5] else ""
            ])

        # ==========================================
        # ROOT
        # ==========================================
        root = BoxLayout(orientation="vertical")

        _bg(root, BG_DARK)

        # ==========================================
        # TOP BAR
        # ==========================================
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(65),
            padding=[dp(10), dp(5), dp(10), dp(5)],
            spacing=dp(8)
        )

        _bg(top_bar, BAR_TOP)

        btn_back = Button(
            text="< RETOUR",
            size_hint=(None, 1),
            width=dp(100),
            font_size=sp(14),
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
            text="[b]GESTION CLIENTS[/b]",
            markup=True,
            font_size=sp(20),
            color=TEXT_MAIN,
            size_hint=(1, 1),
            halign="center",
            valign="middle"
        )

        title_label.bind(
            size=lambda inst, v:
            setattr(inst, "text_size", v)
        )

        top_bar.add_widget(title_label)

        spacer = Label(
            size_hint=(None, 1),
            width=dp(100)
        )

        top_bar.add_widget(spacer)

        root.add_widget(top_bar)

        # ==========================================
        # FORMULAIRE
        # ==========================================
        form_outer = BoxLayout(
            size_hint=(1, None),
            height=dp(380),
            padding=[dp(12), dp(10), dp(12), dp(10)]
        )

        form_card = BoxLayout(
            orientation="vertical",
            padding=[dp(14), dp(12), dp(14), dp(12)],
            spacing=dp(8)
        )

        _bg(form_card, BG_CARD, radius=dp(14))

        form_card.add_widget(
            Label(
                text="[b]AJOUTER UN CLIENT[/b]",
                markup=True,
                font_size=sp(15),
                color=ACCENT,
                size_hint=(1, None),
                height=dp(32),
                halign="center"
            )
        )

        fields = [
            ("Nom complet *", "nom"),
            ("Adresse", "adresse"),
            ("Stat", "stat"),
            ("Téléphone", "contact"),
	        ("Responsable", "responsable"),
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
                height=dp(48),
                padding=[dp(12), dp(12)]
            )

            form_card.add_widget(ti)

            self._inputs[key] = ti

        self.nom = self._inputs["nom"]
        self.adresse = self._inputs["adresse"]
        self.stat = self._inputs["stat"]
        self.contact = self._inputs["contact"]
        self.responsable = self._inputs["responsable"]

        form_outer.add_widget(form_card)

        root.add_widget(form_outer)

        # ==========================================
        # BOUTON SAVE
        # ==========================================
        btn_area = BoxLayout(
            size_hint=(1, None),
            height=dp(60),
            padding=[dp(40), dp(8), dp(40), dp(8)]
        )

        btn_save = Button(
            text="ENREGISTRER",
            font_size=sp(16),
            bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1)
        )

        _bg(btn_save, ACCENT_GREEN, radius=dp(12))

        btn_save.bind(on_release=self.ajouter_client)

        btn_area.add_widget(btn_save)

        root.add_widget(btn_area)

        # ==========================================
        # LABEL COMPTEUR
        # ==========================================
        self.lbl_count = Label(
            text=f"LISTE DES CLIENTS - {len(self.clients)} enregistré(s)",
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

        # ==========================================
        # TABLE
        # ==========================================
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

        # HEADERS
        for h, w in zip(self.HEADERS, self.COL_WIDTHS):

            self.table.add_widget(
                make_cell(
                    h,
                    w,
                    HEADER_BG,
                    bold=True,
                    font_size=sp(12)
                )
            )

        # DONNEES
        for idx, client in enumerate(self.clients):

            row_color = ROW_ODD if idx % 2 == 0 else ROW_EVEN

            for val, w in zip(client, self.COL_WIDTHS):

                val_str = str(val) if val else ""

                if len(val_str) > 20:
                    val_str = val_str[:18] + ".."

                self.table.add_widget(
                    make_cell(
                        val_str,
                        w,
                        row_color,
                        bold=False,
                        font_size=sp(11)
                    )
                )

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
    # AJOUT CLIENT
    # ===================================================
    def ajouter_client(self, instance):

        nom = self.nom.text.strip()

        adresse = self.adresse.text.strip()

        stat = self.stat.text.strip()

        contact = self.contact.text.strip()

        responsable = self.responsable.text.strip()

        # ==========================================
        # NOM OBLIGATOIRE
        # ==========================================
        if not nom:

            self.nom.background_color = ACCENT_RED

            Clock.schedule_once(
                lambda dt:
                setattr(
                    self.nom,
                    'background_color',
                    (0.1, 0.16, 0.30, 1)
                ),
                1
            )

            self.show_message(
                "Erreur",
                "Le nom du client est obligatoire"
            )

            return

        self.nom.background_color = (0.1, 0.16, 0.30, 1)

        # ==========================================
        # VERIFICATION DOUBLON
        # ==========================================
        for client in self.clients:

            nom_client = str(client[0]).strip().lower()

            if nom_client == nom.lower():

                self.show_message(
                    "Erreur",
                    f"Le client '{nom}' existe déjà"
                )

                return

        # ==========================================
        # AJOUT SQLITE
        # ==========================================
        client_id = ajouter_client_db(
            nom,
            adresse,
            stat,
            contact,
	    responsable
        )

        if client_id:

            nouveau_client = [
                nom,
            	adresse,
            	stat,
           	    contact,
	   	        responsable
            ]

            self.clients.append(nouveau_client)

            row_color = (
                ROW_ODD
                if len(self.clients) % 2 == 0
                else ROW_EVEN
            )

            for val, w in zip(nouveau_client, self.COL_WIDTHS):

                val_str = str(val) if val else ""

                if len(val_str) > 20:
                    val_str = val_str[:18] + ".."

                self.table.add_widget(
                    make_cell(
                        val_str,
                        w,
                        row_color,
                        bold=False,
                        font_size=sp(11)
                    )
                )

            # compteur
            n = len(self.clients)

            self.lbl_count.text = (
                f"LISTE DES CLIENTS - "
                f"{n} enregistré(s)"
            )

            # vider formulaire
            for ti in self._inputs.values():
                ti.text = ""

            self.show_message(
                "Succès",
                f"Client '{nom}' ajouté avec succès"
            )

        else:

            self.show_message(
                "Erreur",
                "Erreur lors de l'ajout du client"
            )

    # ===================================================
    # POPUP
    # ===================================================
    def show_message(self, title, message):

        from kivy.uix.popup import Popup

        content = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=dp(16)
        )

        _bg(content, BG_DARK)

        lbl = Label(
            text=message,
            color=TEXT_MAIN,
            font_size=sp(14),
            size_hint=(1, 0.8),
            halign="center",
            valign="middle"
        )

        lbl.bind(
            size=lambda inst, s:
            setattr(
                inst,
                'text_size',
                (s[0] - dp(10), s[1])
            )
        )

        content.add_widget(lbl)

        btn = Button(
            text="OK",
            size_hint=(1, 0.2),
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

        popup.open()

    # ===================================================
    # ON ENTER
    # ===================================================
    def on_enter(self):

        self.rafraichir_liste()

    # ===================================================
    # RAFRAICHIR
    # ===================================================
    def rafraichir_liste(self):

        self.clients = []

        clients_data = get_all_clients()

        for client in clients_data:

            self.clients.append([
                str(client[1]) if client[1] else "",
                str(client[2]) if client[2] else "",
                str(client[3]) if client[3] else "",
                str(client[4]) if client[4] else "",
                str(client[5]) if client[5] else ""
            ])

        enfants = list(self.table.children)

        nb_header = len(self.HEADERS)

        lignes = (
            enfants[:-nb_header]
            if len(enfants) > nb_header
            else []
        )

        for enfant in lignes:
            self.table.remove_widget(enfant)

        for idx, client in enumerate(self.clients):

            row_color = ROW_ODD if idx % 2 == 0 else ROW_EVEN

            for val, w in zip(client, self.COL_WIDTHS):

                val_str = str(val) if val else ""

                if len(val_str) > 20:
                    val_str = val_str[:18] + ".."

                self.table.add_widget(
                    make_cell(
                        val_str,
                        w,
                        row_color,
                        bold=False,
                        font_size=sp(11)
                    )
                )

        n = len(self.clients)

        self.lbl_count.text = (
            f"LISTE DES CLIENTS - "
            f"{n} enregistré(s)"
        )

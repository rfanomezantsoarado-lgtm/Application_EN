#Importation des bibliothèques utiles
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp, sp
from kivy.clock import Clock
from database import init_database, ajouter_client_db, get_all_clients, modifier_client_db, supprimer_client_db


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

    HEADERS = ["Nom", "Adresse", "Contact", "Responsable", "Modifier", "Supprimer"]
    COL_WIDTHS = [dp(130), dp(140), dp(110), dp(110), dp(90), dp(90)]
    ROW_H = dp(48)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialisation DB
        init_database()

        self.clients = []
        self.client_ids = []
        self.client_en_modification = None

        clients_data = get_all_clients()
        for client in clients_data:
            self.clients.append([
                str(client[1]) if client[1] else "",
                str(client[2]) if client[2] else "",
                str(client[3]) if client[3] else "",
                str(client[4]) if client[4] else ""
            ])
            self.client_ids.append(client[0])

        # ROOT
        root = BoxLayout(orientation="vertical")
        _bg(root, BG_DARK)

        # TOP BAR
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
        btn_back.bind(on_release=lambda *a: setattr(self.manager, "current", "accueil"))
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
        title_label.bind(size=lambda inst, v: setattr(inst, "text_size", v))
        top_bar.add_widget(title_label)

        spacer = Label(size_hint=(None, 1), width=dp(100))
        top_bar.add_widget(spacer)
        root.add_widget(top_bar)

        # FORMULAIRE
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

        self.form_title = Label(
            text="[b]AJOUTER UN CLIENT[/b]",
            markup=True,
            font_size=sp(15),
            color=ACCENT,
            size_hint=(1, None),
            height=dp(32),
            halign="center"
        )
        form_card.add_widget(self.form_title)

        fields = [
            ("Nom complet *", "nom"),
            ("Adresse", "adresse"),
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
        self.contact = self._inputs["contact"]
        self.responsable = self._inputs["responsable"]

        form_outer.add_widget(form_card)
        root.add_widget(form_outer)

        # BOUTONS
        btn_area = BoxLayout(
            size_hint=(1, None),
            height=dp(60),
            padding=[dp(40), dp(8), dp(40), dp(8)],
            spacing=dp(10)
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
        btn_save.bind(on_release=self.ajouter_ou_modifier_client)
        btn_area.add_widget(btn_save)

        self.btn_cancel = Button(
            text="ANNULER",
            font_size=sp(16),
            bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            size_hint=(0.5, 1)
        )
        _bg(self.btn_cancel, ACCENT_RED, radius=dp(12))
        self.btn_cancel.bind(on_release=self.annuler_modification)
        self.btn_cancel.opacity = 0
        self.btn_cancel.disabled = True
        btn_area.add_widget(self.btn_cancel)

        root.add_widget(btn_area)

        # LABEL COMPTEUR
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
        self.lbl_count.bind(size=lambda inst, v: setattr(inst, "text_size", (v[0] - dp(14), None)))
        root.add_widget(self.lbl_count)

        # TABLE
        total_w = sum(self.COL_WIDTHS)
        self.table = GridLayout(
            cols=6,
            size_hint=(None, None),
            width=total_w,
            row_default_height=self.ROW_H,
            row_force_default=True,
            spacing=0,
            padding=0
        )
        self.table.bind(minimum_height=self.table.setter('height'))

        # HEADERS
        for h, w in zip(self.HEADERS, self.COL_WIDTHS):
            self.table.add_widget(make_cell(h, w, HEADER_BG, bold=True, font_size=sp(12)))

        # DONNEES
        self.ajouter_lignes_tableau()

        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=True,
            bar_width=dp(6),
            bar_color=list(ACCENT[:3]) + [0.8]
        )
        scroll.add_widget(self.table)

        table_box = BoxLayout(size_hint=(1, 1), padding=[dp(6), dp(4), dp(6), dp(6)])
        table_box.add_widget(scroll)
        root.add_widget(table_box)

        self.add_widget(root)

    # ===================================================
    # AJOUTER LIGNES TABLEAU
    # ===================================================
    def ajouter_lignes_tableau(self):
        """Ajoute toutes les lignes du tableau avec les boutons Modifier/Supprimer"""

        # Supprimer les anciennes lignes (garder seulement l'en-tête)
        enfants = list(self.table.children)
        nb_header = len(self.HEADERS)

        if len(enfants) > nb_header:
            for i in range(len(enfants) - nb_header):
                enfant = enfants[i]
                self.table.remove_widget(enfant)

        # Ajouter les nouvelles lignes
        for idx, client in enumerate(self.clients):
            row_color = ROW_ODD if idx % 2 == 0 else ROW_EVEN

            # Tronquer les textes trop longs
            nom = client[0][:18] + ".." if len(client[0]) > 20 else client[0]
            adresse = client[1][:18] + ".." if len(client[1]) > 20 else client[1]
            contact = client[2][:18] + ".." if len(client[2]) > 20 else client[2]
            responsable = client[3][:18] + ".." if len(client[3]) > 20 else client[3]

            # Cellules de texte
            self.table.add_widget(make_cell(nom, self.COL_WIDTHS[0], row_color, False, sp(11)))
            self.table.add_widget(make_cell(adresse, self.COL_WIDTHS[1], row_color, False, sp(11)))
            self.table.add_widget(make_cell(contact, self.COL_WIDTHS[2], row_color, False, sp(11)))
            self.table.add_widget(make_cell(responsable, self.COL_WIDTHS[3], row_color, False, sp(11)))

            # Bouton MODIFIER
            btn_modifier = Button(
                text="Modifier",
                font_size=sp(15),
                size_hint=(None, None),
                size=(self.COL_WIDTHS[4], self.ROW_H),
                background_normal="",
                background_color=(0.08, 0.45, 0.82, 1),
                color=TEXT_MAIN
            )
            btn_modifier.bind(on_release=lambda btn, i=idx: self.modifier_client(i))
            self.table.add_widget(btn_modifier)

            # Bouton SUPPRIMER
            btn_supprimer = Button(
                text="Supprimer",
                font_size=sp(15),
                size_hint=(None, None),
                size=(self.COL_WIDTHS[5], self.ROW_H),
                background_normal="",
                background_color=(0.82, 0.08, 0.08, 1),
                color=TEXT_MAIN
            )
            btn_supprimer.bind(on_release=lambda btn, i=idx: self.confirmer_suppression(i))
            self.table.add_widget(btn_supprimer)

        self.table.height = len(self.clients) * self.ROW_H

    # ===================================================
    # AJOUT OU MODIFICATION CLIENT
    # ===================================================
    def ajouter_ou_modifier_client(self, instance):
        nom = self.nom.text.strip()
        adresse = self.adresse.text.strip()
        contact = self.contact.text.strip()
        responsable = self.responsable.text.strip()

        if not nom:
            self.nom.background_color = ACCENT_RED
            Clock.schedule_once(lambda dt: setattr(self.nom, 'background_color', (0.1, 0.16, 0.30, 1)), 1)
            self.show_message("Erreur", "Le nom du client est obligatoire")
            return

        self.nom.background_color = (0.1, 0.16, 0.30, 1)

        # Mode MODIFICATION
        if self.client_en_modification is not None:
            for i, client in enumerate(self.clients):
                if i != self.client_en_modification:
                    if str(client[0]).strip().lower() == nom.lower():
                        self.show_message("Erreur", f"Le client '{nom}' existe déjà")
                        return

            client_id = self.client_ids[self.client_en_modification]
            if modifier_client_db(client_id, nom, adresse, contact, responsable):
                self.clients[self.client_en_modification] = [nom, adresse, contact, responsable]
                self.ajouter_lignes_tableau()
                self.lbl_count.text = f"LISTE DES CLIENTS - {len(self.clients)} enregistré(s)"
                for ti in self._inputs.values():
                    ti.text = ""
                self.btn_cancel.opacity = 0
                self.btn_cancel.disabled = True
                self.form_title.text = "[b]AJOUTER UN CLIENT[/b]"
                self.client_en_modification = None
                self.show_message("Succès", f"Client '{nom}' modifié avec succès")
            else:
                self.show_message("Erreur", "Erreur lors de la modification")

        # Mode AJOUT
        else:
            for client in self.clients:
                if str(client[0]).strip().lower() == nom.lower():
                    self.show_message("Erreur", f"Le client '{nom}' existe déjà")
                    return

            client_id = ajouter_client_db(nom, adresse, contact, responsable)
            if client_id:
                self.clients.append([nom, adresse, contact, responsable])
                self.client_ids.append(client_id)
                self.ajouter_lignes_tableau()
                self.lbl_count.text = f"LISTE DES CLIENTS - {len(self.clients)} enregistré(s)"
                for ti in self._inputs.values():
                    ti.text = ""
                self.show_message("Succès", f"Client '{nom}' ajouté avec succès")
            else:
                self.show_message("Erreur", "Erreur lors de l'ajout du client")

    # ===================================================
    # MODIFIER CLIENT
    # ===================================================
    def modifier_client(self, index):
        client = self.clients[index]
        self.nom.text = client[0]
        self.adresse.text = client[1]
        self.contact.text = client[2]
        self.responsable.text = client[3]
        self.form_title.text = "[b]MODIFIER LE CLIENT[/b]"
        self.btn_cancel.opacity = 1
        self.btn_cancel.disabled = False
        self.client_en_modification = index

    # ===================================================
    # ANNULER MODIFICATION
    # ===================================================
    def annuler_modification(self, instance):
        for ti in self._inputs.values():
            ti.text = ""
        self.form_title.text = "[b]AJOUTER UN CLIENT[/b]"
        self.btn_cancel.opacity = 0
        self.btn_cancel.disabled = True
        self.client_en_modification = None

    # ===================================================
    # CONFIRMER SUPPRESSION
    # ===================================================
    def confirmer_suppression(self, index):
        from kivy.uix.popup import Popup
        client_nom = self.clients[index][0]

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        _bg(content, BG_DARK)

        lbl = Label(
            text=f"Voulez-vous vraiment supprimer\n'{client_nom}' ?",
            color=TEXT_MAIN,
            font_size=sp(14),
            size_hint=(1, 0.7),
            halign="center",
            valign="middle"
        )
        lbl.bind(size=lambda inst, s: setattr(inst, 'text_size', (s[0] - dp(10), s[1])))
        content.add_widget(lbl)

        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=dp(10))

        btn_oui = Button(text="OUI", font_size=sp(14), bold=True, background_normal="", background_color=ACCENT_RED, color=TEXT_MAIN)
        _bg(btn_oui, ACCENT_RED, radius=dp(8))

        btn_non = Button(text="NON", font_size=sp(14), bold=True, background_normal="", background_color=ACCENT_GREEN, color=TEXT_MAIN)
        _bg(btn_non, ACCENT_GREEN, radius=dp(8))

        btn_layout.add_widget(btn_oui)
        btn_layout.add_widget(btn_non)
        content.add_widget(btn_layout)

        popup = Popup(
            title="Confirmation",
            content=content,
            size_hint=(0.85, 0.35),
            background_color=BG_CARD,
            title_size=sp(15),
            title_color=ACCENT
        )

        btn_oui.bind(on_release=lambda *a: self.supprimer_client(index, popup))
        btn_non.bind(on_release=popup.dismiss)
        popup.open()

    # ===================================================
    # SUPPRIMER CLIENT
    # ===================================================
    def supprimer_client(self, index, popup):
        client_id = self.client_ids[index]
        client_nom = self.clients[index][0]

        if supprimer_client_db(client_id):
            del self.clients[index]
            del self.client_ids[index]
            self.ajouter_lignes_tableau()
            self.lbl_count.text = f"LISTE DES CLIENTS - {len(self.clients)} enregistré(s)"

            if self.client_en_modification is not None:
                if index == self.client_en_modification:
                    self.annuler_modification(None)
                elif index < self.client_en_modification:
                    self.client_en_modification -= 1

            self.show_message("Succès", f"Client '{client_nom}' supprimé avec succès")
        else:
            self.show_message("Erreur", "Erreur lors de la suppression")

        popup.dismiss()

    # ===================================================
    # POPUP
    # ===================================================
    def show_message(self, title, message):
        from kivy.uix.popup import Popup

        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(16))
        _bg(content, BG_DARK)

        lbl = Label(
            text=message,
            color=TEXT_MAIN,
            font_size=sp(14),
            size_hint=(1, 0.8),
            halign="center",
            valign="middle"
        )
        lbl.bind(size=lambda inst, s: setattr(inst, 'text_size', (s[0] - dp(10), s[1])))
        content.add_widget(lbl)

        btn = Button(text="OK", size_hint=(1, 0.2), font_size=sp(14), bold=True, background_normal="", background_color=ACCENT_GREEN, color=TEXT_MAIN)
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
        self.client_ids = []

        clients_data = get_all_clients()
        for client in clients_data:
            self.clients.append([
                str(client[1]) if client[1] else "",
                str(client[2]) if client[2] else "",
                str(client[3]) if client[3] else "",
                str(client[4]) if client[4] else ""
            ])
            self.client_ids.append(client[0])

        self.ajouter_lignes_tableau()
        self.lbl_count.text = f"LISTE DES CLIENTS - {len(self.clients)} enregistré(s)"
#Importation des bibliothèques utiles
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.metrics import dp, sp
from database import (init_database, get_all_commandes, get_commandes_client,
                      get_all_clients, get_commande_by_id, payer_reste_db)
import re
import os
import datetime
import subprocess
import sys
from kivy.utils import platform

# Remplacer pdf_generator par image_generator
from image_generator import generer_image_facture

# Import pour le partage sur Android
ANDROID_AVAILABLE = False
if platform == 'android':
    try:
        from android import activity
        from android.permissions import request_permissions, Permission
        from jnius import autoclass
        ANDROID_AVAILABLE = True
        
        # Classes Android pour partage
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        File = autoclass('java.io.File')
        MediaStore = autoclass('android.provider.MediaStore')
        Context = autoclass('android.content.Context')
        Build = autoclass('android.os.Build')
    except ImportError:
        pass

# ===================================================
# COULEURS
# ===================================================
BG_DARK       = (0.04, 0.07, 0.16, 1)
BG_CARD       = (0.07, 0.11, 0.22, 1)
ACCENT        = (0.08, 0.45, 0.82, 1)
ACCENT_GREEN  = (0.05, 0.68, 0.38, 1)
ACCENT_RED    = (0.82, 0.08, 0.08, 1)
ACCENT_ORANGE = (0.95, 0.55, 0.08, 1)
ACCENT_BLUE   = (0.08, 0.45, 0.82, 1)
ACCENT_PURPLE = (0.55, 0.08, 0.82, 1)
GREY          = (0.25, 0.25, 0.25, 1)
TEXT_WHITE    = (1, 1, 1, 1)
TEXT_DIM      = (0.8, 0.8, 0.8, 1)
ROW_ODD       = (0.10, 0.16, 0.30, 1)
ROW_EVEN      = (0.07, 0.12, 0.24, 1)
HEADER_BG     = (0.05, 0.35, 0.65, 1)
BAR_TOP       = (0.05, 0.08, 0.18, 1)


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


def make_cell(text, w, h, bg_color, bold=False, font_size=12, text_color=None):
    color = text_color if text_color else TEXT_WHITE
    lbl = Label(
        text=f"[b]{text}[/b]" if bold else text,
        markup=bold,
        size_hint=(None, None),
        size=(w, h),
        font_size=font_size,
        color=color,
        halign="center",
        valign="middle"
    )
    lbl.bind(size=lambda inst, v: setattr(inst, "text_size", v))
    _bg(lbl, bg_color)
    return lbl


class HistoriqueCommandeScreen(Screen):

    # N°, Client, Date, Total, Avance, Reste, Statut, VOIR, PAYER
    HEADERS    = ["N°", "Client", "Date/Heure", "Total (Ar)",
                  "Avance (Ar)", "Reste (Ar)", "Statut", "Voir", "Payer"]
    # Largeurs augmentées pour mobile
    COL_WIDTHS = [dp(45), dp(110), dp(125), dp(95),
                  dp(95), dp(90), dp(80), dp(55), dp(60)]
    ROW_H = dp(48)  # Hauteur de ligne augmentée

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.commandes = []
        self.commandes_originales = []
        self.filtre_client = "Tous"

        root_layout = BoxLayout(orientation="vertical")
        _bg(root_layout, BG_DARK)

        # ── BARRE HAUTE ───────────────────────────────────
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(65),  # Augmenté
            padding=[dp(10), dp(8), dp(10), dp(8)],
            spacing=dp(10)
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
            color=ACCENT_BLUE
        )
        btn_back.bind(on_release=lambda *a: setattr(self.manager, "current", "accueil"))
        top_bar.add_widget(btn_back)

        title_label = Label(
            text="[b]HISTORIQUE DES COMMANDES[/b]",
            markup=True,
            font_size=sp(20),  # Augmenté
            color=TEXT_WHITE,
            size_hint=(1, 1),
            halign="center",
            valign="middle"
        )
        title_label.bind(size=lambda inst, v: setattr(inst, "text_size", v))
        top_bar.add_widget(title_label)
        root_layout.add_widget(top_bar)

        # ── SECTION RECHERCHE AVANCÉE ─────────────────────
        search_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(180),  # Augmenté
            padding=[dp(12), dp(10), dp(12), dp(10)],
            spacing=dp(8)
        )
        _bg(search_card, BG_CARD, radius=dp(12))

        # Titre
        search_card.add_widget(Label(
            text="[b]RECHERCHE[/b]",
            markup=True,
            font_size=sp(14),  # Augmenté
            color=ACCENT,
            size_hint=(1, None),
            height=dp(28),
            halign="center"
        ))

        # Ligne 1: N° Facture et Client
        row1 = BoxLayout(size_hint=(1, None), height=dp(45), spacing=dp(10))
        col1 = BoxLayout(size_hint=(0.5, 1), spacing=dp(8))
        col1.add_widget(Label(
            text="N° :",
            size_hint=(0.3, 1),
            color=TEXT_WHITE,
            font_size=sp(13),
            halign="right"
        ))
        self.search_numero = TextInput(
            text="",
            multiline=False,
            font_size=sp(13),
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.7, 1),
            padding=[dp(8), dp(8)],
            hint_text="Numéro"
        )
        col1.add_widget(self.search_numero)

        col2 = BoxLayout(size_hint=(0.5, 1), spacing=dp(8))
        col2.add_widget(Label(
            text="Client :",
            size_hint=(0.3, 1),
            color=TEXT_WHITE,
            font_size=sp(13),
            halign="right"
        ))
        self.search_client = TextInput(
            text="",
            multiline=False,
            font_size=sp(13),
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.7, 1),
            padding=[dp(8), dp(8)],
            hint_text="Nom client"
        )
        col2.add_widget(self.search_client)

        row1.add_widget(col1)
        row1.add_widget(col2)
        search_card.add_widget(row1)

        # Ligne 2: Date
        row2 = BoxLayout(size_hint=(1, None), height=dp(45), spacing=dp(10))
        row2.add_widget(Label(
            text="Date :",
            size_hint=(0.2, 1),
            color=TEXT_WHITE,
            font_size=sp(13),
            halign="right"
        ))
        self.search_date = TextInput(
            text="",
            multiline=False,
            font_size=sp(13),
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.8, 1),
            padding=[dp(8), dp(8)],
            hint_text="JJ/MM/AAAA"
        )
        row2.add_widget(self.search_date)
        search_card.add_widget(row2)

        # Boutons de recherche
        btn_row = BoxLayout(size_hint=(1, None), height=dp(48), spacing=dp(10))
        btn_rechercher = Button(
            text="RECHERCHER",
            font_size=sp(13),
            bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_rechercher, ACCENT, radius=dp(8))
        btn_rechercher.bind(on_release=self.rechercher_commandes)

        btn_reset = Button(
            text="RÉINITIALISER",
            font_size=sp(13),
            bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_reset, ACCENT_ORANGE, radius=dp(8))
        btn_reset.bind(on_release=self.reset_recherche)

        btn_row.add_widget(btn_rechercher)
        btn_row.add_widget(btn_reset)
        search_card.add_widget(btn_row)

        root_layout.add_widget(search_card)

        # ── STATISTIQUES ──────────────────────────────────
        stats_card = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(90),  # Augmenté
            padding=[dp(12), dp(10), dp(12), dp(10)],
            spacing=dp(6)
        )
        _bg(stats_card, BG_CARD, radius=dp(12))

        for attr, lbl_txt, color in [
            ("lbl_total_commandes", "TOTAL\nCOMMANDES", ACCENT_GREEN),
            ("lbl_total_avances",   "TOTAL\nAVANCES",   ACCENT),
            ("lbl_total_restes",    "TOTAL\nRESTES",    ACCENT_RED),
        ]:
            box = BoxLayout(orientation="vertical", size_hint=(0.33, 1), spacing=dp(4))
            box.add_widget(Label(text=lbl_txt, font_size=sp(11),
                                 color=TEXT_DIM, halign="center"))
            lbl = Label(text="0", font_size=sp(22), color=color,
                        bold=True, halign="center")
            setattr(self, attr, lbl)
            box.add_widget(lbl)
            stats_card.add_widget(box)
            if attr != "lbl_total_restes":
                stats_card.add_widget(
                    Label(text="|", size_hint=(0.02, 1), color=TEXT_DIM, font_size=sp(22))
                )
        root_layout.add_widget(stats_card)

        # ── TITRE TABLEAU ─────────────────────────────────
        table_title = BoxLayout(size_hint=(1, None), height=dp(36), padding=[dp(10), dp(5), dp(10), 0])
        table_title.add_widget(Label(
            text="[b]LISTE DES COMMANDES[/b]",
            markup=True, font_size=sp(15), color=ACCENT,
            halign="left", size_hint=(1, 1)
        ))
        root_layout.add_widget(table_title)

        # ── TABLEAU ───────────────────────────────────────
        table_container = BoxLayout(size_hint=(1, 1), padding=[dp(6), dp(4), dp(6), dp(4)])

        total_w = sum(self.COL_WIDTHS)
        self.table = GridLayout(
            cols=9,
            size_hint=(None, None),
            width=total_w,
            row_default_height=self.ROW_H,
            row_force_default=True,
            spacing=0,
            padding=0
        )
        self.table.bind(minimum_height=self.table.setter('height'))

        for h, w in zip(self.HEADERS, self.COL_WIDTHS):
            self.table.add_widget(
                make_cell(h, w, self.ROW_H, HEADER_BG, bold=True, font_size=sp(12))
            )

        scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=True,
            bar_width=dp(8),
            bar_color=list(ACCENT[:3]) + [0.8]
        )
        scroll.add_widget(self.table)
        table_container.add_widget(scroll)
        root_layout.add_widget(table_container)

        self.add_widget(root_layout)
        Clock.schedule_once(lambda dt: self.charger_commandes(None), 0.5)

    # ═══════════════════════════════════════════════════
    def on_enter(self):
        self.charger_commandes(None)

    def charger_commandes(self, instance):
        """Charge toutes les commandes depuis la base"""
        try:
            init_database()
            self.commandes_originales = get_all_commandes()
            self.commandes = self.commandes_originales.copy()
            self.actualiser_tableau()
        except Exception as e:
            print(f"Erreur chargement commandes: {e}")

    def rechercher_commandes(self, instance):
        """Filtre les commandes selon les critères de recherche"""
        numero = self.search_numero.text.strip()
        client = self.search_client.text.strip().lower()
        date = self.search_date.text.strip()

        resultats = self.commandes_originales.copy()

        if numero:
            resultats = [c for c in resultats if str(c[0]) == numero]

        if client:
            resultats = [c for c in resultats if client in str(c[1]).lower()]

        if date:
            filtered_results = []
            for c in resultats:
                if len(c) > 6 and c[6]:
                    date_commande = str(c[6])
                    if ' ' in date_commande:
                        date_commande = date_commande.split(' ')[0]
                    try:
                        jour, mois, annee = date.split('/')
                        date_recherche = f"{annee}-{mois}-{jour}"
                        if date_commande == date_recherche:
                            filtered_results.append(c)
                    except ValueError:
                        if date in date_commande:
                            filtered_results.append(c)
            resultats = filtered_results

        self.commandes = resultats
        self.actualiser_tableau()
        self.show_message("Recherche", f"{len(resultats)} commande(s) trouvée(s)")

    def reset_recherche(self, instance):
        """Réinitialise tous les filtres et affiche toutes les commandes"""
        self.search_numero.text = ""
        self.search_client.text = ""
        self.search_date.text = ""
        self.commandes = self.commandes_originales.copy()
        self.actualiser_tableau()
        self.show_message("Recherche", "Filtres réinitialisés")

    def actualiser_tableau(self):
        """Affiche les commandes dans le tableau"""
        if not self.table:
            return

        enfants = list(self.table.children)
        nb_header = len(self.HEADERS)
        lignes = enfants[:-nb_header] if len(enfants) > nb_header else []
        for enfant in lignes:
            self.table.remove_widget(enfant)

        total_avances = 0.0
        total_restes = 0.0

        for idx, commande in enumerate(self.commandes):
            row_color = ROW_ODD if idx % 2 == 0 else ROW_EVEN

            reste_val = float(commande[4]) if len(commande) > 4 and commande[4] else 0.0
            avance_val = float(commande[3]) if len(commande) > 3 and commande[3] else 0.0

            if reste_val <= 0:
                statut, statut_color = "PAYE", ACCENT_GREEN
            elif avance_val > 0:
                statut, statut_color = "AVANCE", ACCENT_ORANGE
            else:
                statut, statut_color = "IMPAYE", ACCENT_RED

            date_str = ""
            if len(commande) > 6 and commande[6]:
                d = str(commande[6])
                if ' ' in d:
                    parts = d.split(' ')
                    date_str = parts[0] + "\n" + parts[1][:5]
                else:
                    date_str = d

            valeurs = [
                str(commande[0]) if len(commande) > 0 else "",
                str(commande[1]) if len(commande) > 1 else "",
                date_str,
                f"{commande[2]:,.0f}" if len(commande) > 2 and commande[2] else "0",
                f"{avance_val:,.0f}",
                f"{reste_val:,.0f}",
                statut,
            ]

            total_avances += avance_val
            total_restes += reste_val

            # 7 cellules de données
            for i, (val, w) in enumerate(zip(valeurs, self.COL_WIDTHS[:7])):
                tc = statut_color if i == 6 else None
                self.table.add_widget(
                    make_cell(val, w, self.ROW_H, row_color,
                              bold=False, font_size=sp(11), text_color=tc)
                )

            commande_id = commande[0]
            client_nom = str(commande[1]) if len(commande) > 1 else ""
            reste_courant = reste_val

            # BOUTON VOIR
            w_voir = self.COL_WIDTHS[7]
            btn_voir = Button(
                text="VOIR",
                size_hint=(None, None),
                size=(w_voir, self.ROW_H),
                font_size=sp(11),
                bold=True,
                background_normal="",
                background_color=(0, 0, 0, 0),
                color=TEXT_WHITE
            )
            _bg(btn_voir, ACCENT_BLUE, radius=dp(6))
            btn_voir.bind(
                on_release=lambda inst, cid=commande_id:
                self.afficher_details_commande(cid)
            )
            self.table.add_widget(btn_voir)

            # BOUTON PAYER
            w_payer = self.COL_WIDTHS[8]
            btn_payer = Button(
                text="PAYER",
                size_hint=(None, None),
                size=(w_payer, self.ROW_H),
                font_size=sp(11),
                bold=True,
                background_normal="",
                background_color=(0, 0, 0, 0),
                color=TEXT_WHITE,
                disabled=(reste_val <= 0)
            )
            _bg(btn_payer,
                GREY if reste_val <= 0 else ACCENT_ORANGE,
                radius=dp(6))
            btn_payer.bind(
                on_release=lambda inst,
                cid=commande_id,
                cl=client_nom,
                r=reste_courant:
                self.ouvrir_popup_payer(cid, cl, r)
            )
            self.table.add_widget(btn_payer)

        # Statistiques
        self.lbl_total_commandes.text = str(len(self.commandes))
        self.lbl_total_avances.text = f"{total_avances:,.0f} Ar"
        self.lbl_total_restes.text = f"{total_restes:,.0f} Ar"

        if not self.commandes:
            if len(self.table.children) == len(self.HEADERS):
                self.table.add_widget(
                    make_cell("Aucune commande trouvée",
                              sum(self.COL_WIDTHS), self.ROW_H,
                              BG_CARD, font_size=sp(13), text_color=TEXT_DIM)
                )

    # ═══════════════════════════════════════════════════
    # POPUP VOIR — détails de la commande
    # ═══════════════════════════════════════════════════
    def afficher_details_commande(self, commande_id):
        commande = get_commande_by_id(commande_id)
        if not commande:
            self.show_message("Erreur", "Commande introuvable")
            return

        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(12))
        _bg(content, BG_DARK)

        # En-tête centré
        header = BoxLayout(orientation="vertical", size_hint=(1, None), height=dp(75), spacing=dp(8))
        _bg(header, BG_CARD, radius=dp(8))

        lbl_numero = Label(
            text=f"Commande N° {commande_id}[/b]",
            markup=True, font_size=sp(18), color=ACCENT,
            size_hint=(1, None), height=dp(30),
            halign="center", valign="middle"
        )
        lbl_numero.bind(size=lambda inst, v: setattr(inst, "text_size", v))
        header.add_widget(lbl_numero)

        lbl_client = Label(
            text=f"{commande['client_nom']}",
            font_size=sp(15), color=TEXT_WHITE,
            size_hint=(1, None), height=dp(25),
            halign="center", valign="middle"
        )
        lbl_client.bind(size=lambda inst, v: setattr(inst, "text_size", v))
        header.add_widget(lbl_client)

        lbl_date = Label(
            text=f"Date : {commande['date']}",
            font_size=sp(12), color=TEXT_DIM,
            size_hint=(1, None), height=dp(25),
            halign="center", valign="middle"
        )
        lbl_date.bind(size=lambda inst, v: setattr(inst, "text_size", v))
        header.add_widget(lbl_date)

        content.add_widget(header)

        # Dépôt de sortie
        depot_sortie = commande.get('depot_sortie', 'Dépôt principal')
        depot_box = BoxLayout(size_hint=(1, None), height=dp(35), spacing=dp(10), padding=[dp(10), 0])
        _bg(depot_box, (0.15, 0.20, 0.35, 1), radius=dp(6))
        depot_box.add_widget(Label(
            text=f"DÉPÔT DE SORTIE : {depot_sortie}",
            font_size=sp(12), color=ACCENT_ORANGE,
            halign="center", valign="middle", bold=True
        ))
        content.add_widget(depot_box)

        # Tableau produits
        grid = GridLayout(
            cols=4, size_hint=(1, None),
            row_default_height=dp(42), row_force_default=True,
            spacing=dp(1)
        )
        grid.bind(minimum_height=grid.setter('height'))

        for h in ["Produit", "Prix unit.", "Qte", "Total"]:
            lbl = Label(text=f"[b]{h}[/b]", markup=True,
                        font_size=sp(12), color=TEXT_WHITE,
                        size_hint=(1, None), height=dp(42),
                        halign="center", valign="middle")
            lbl.bind(size=lambda inst, v: setattr(inst, "text_size", v))
            _bg(lbl, HEADER_BG)
            grid.add_widget(lbl)

        for i, p in enumerate(commande['produits']):
            rc = ROW_ODD if i % 2 == 0 else ROW_EVEN
            for val in [
                p.get('nom', ''),
                f"{float(p.get('prix_unitaire', 0)):,.0f}",
                str(p.get('quantite', '')),
                f"{float(p.get('total', 0)):,.0f}"
            ]:
                lbl = Label(text=val, font_size=sp(12), color=TEXT_WHITE,
                            size_hint=(1, None), height=dp(42),
                            halign="center", valign="middle")
                lbl.bind(size=lambda inst, v: setattr(inst, "text_size", v))
                _bg(lbl, rc)
                grid.add_widget(lbl)

        scroll_g = ScrollView(size_hint=(1, None), height=dp(250),
                              do_scroll_y=True, do_scroll_x=False)
        scroll_g.add_widget(grid)
        content.add_widget(scroll_g)

        # Totaux
        for lbl_txt, val, color in [
            ("Total",   f"{commande['total']:,.0f} Ar",  ACCENT_GREEN),
            ("Avance",  f"{commande['avance']:,.0f} Ar", ACCENT),
            ("Reste",   f"{commande['reste']:,.0f} Ar",  ACCENT_RED),
        ]:
            row = BoxLayout(size_hint=(1, None), height=dp(38), spacing=dp(10))
            row.add_widget(Label(text=f"[b]{lbl_txt} :[/b]", markup=True,
                                 font_size=sp(15), color=TEXT_DIM,
                                 size_hint=(0.3, 1), halign="right"))
            row.add_widget(Label(text=val, font_size=sp(15), color=color,
                                 bold=True, size_hint=(0.7, 1), halign="left"))
            content.add_widget(row)

        # Mode de paiement
        mode_paiement = commande.get('mode_paiement', 'Espèce')
        mode_row = BoxLayout(size_hint=(1, None), height=dp(38), spacing=dp(10))
        mode_row.add_widget(Label(text=f"[b]Mode :[/b]", markup=True,
                                   font_size=sp(13), color=TEXT_DIM,
                                   size_hint=(0.3, 1), halign="right"))
        mode_row.add_widget(Label(text=mode_paiement, font_size=sp(13), color=ACCENT_ORANGE,
                                   bold=True, size_hint=(0.7, 1), halign="left"))
        content.add_widget(mode_row)

        # Boutons
        btn_box = BoxLayout(size_hint=(1, None), height=dp(55), spacing=dp(12), padding=[dp(10), 0])
        btn_close = Button(
            text="FERMER",
            font_size=sp(14), bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_close, ACCENT_BLUE, radius=dp(10))

        btn_pdf = Button(
            text="GÉNÉRER FACTURE",
            font_size=sp(14), bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_pdf, ACCENT_GREEN, radius=dp(10))

        btn_box.add_widget(btn_pdf)
        btn_box.add_widget(btn_close)
        content.add_widget(btn_box)

        popup = Popup(
            title=f"Détails commande N° {commande_id}",
            content=content,
            size_hint=(0.95, 0.9),
            background_color=BG_CARD,
            title_size=sp(16),
            title_color=ACCENT
        )
        btn_close.bind(on_release=popup.dismiss)
        btn_pdf.bind(on_release=lambda x: self.generer_et_afficher_facture(commande_id, popup))
        popup.open()

    # ═══════════════════════════════════════════════════
    # GÉNÉRER ET AFFICHER FACTURE (IMAGE)
    # ═══════════════════════════════════════════════════
    def generer_et_afficher_facture(self, commande_id, popup_to_close=None, mode_paiement=None, numero_cheque=""):
        """Génère une facture au format image JPEG"""
        try:
            commande = get_commande_by_id(commande_id)
            if not commande:
                self.show_message("Erreur", "Commande introuvable")
                return

            client_info = {'adresse': '', 'nif': '', 'stat': '', 'contact': ''}
            clients_data = get_all_clients()
            for c in clients_data:
                if len(c) >= 5:
                    if isinstance(c[0], int) and c[0] is not None:
                        if str(c[1]) == commande['client_nom']:
                            client_info = {
                                'adresse': str(c[2]) if len(c) > 2 and c[2] else "",
                                'nif': str(c[3]) if len(c) > 3 and c[3] else "",
                                'stat': str(c[4]) if len(c) > 4 and c[4] else "",
                                'contact': str(c[5]) if len(c) > 5 and c[5] else ""
                            }
                            break
                    else:
                        if str(c[0]) == commande['client_nom']:
                            client_info = {
                                'adresse': str(c[1]) if len(c) > 1 and c[1] else "",
                                'nif': str(c[2]) if len(c) > 2 and c[2] else "",
                                'stat': str(c[3]) if len(c) > 3 and c[3] else "",
                                'contact': str(c[4]) if len(c) > 4 and c[4] else ""
                            }
                            break

            mode_paiement = commande.get("mode_paiement", "Espèce")
            numero_cheque = commande.get("numero_cheque", "") if mode_paiement == "Chèque" else ""
            depot_sortie = commande.get("depot_sortie", "Dépôt principal")

            filename = generer_image_facture(
                commande_id=commande_id,
                client_nom=commande['client_nom'],
                client_info=client_info,
                produits=commande.get('produits', []),
                total=float(commande.get('total', 0)),
                avance=float(commande.get('avance', 0)),
                reste=float(commande.get('reste', 0)),
                date_str=commande.get('date', datetime.datetime.now().strftime("%d/%m/%Y %H:%M")),
                mode_paiement=mode_paiement,
                depot_sortie=depot_sortie,
                numero_cheque=numero_cheque
            )

            if filename:
                if popup_to_close:
                    popup_to_close.dismiss()
                self.afficher_apercu_image(filename, commande_id)
            else:
                self.show_message("Erreur", "Erreur lors de la génération de l'image")

        except Exception as e:
            self.show_message("Erreur", f"Erreur : {str(e)}")

    def afficher_apercu_image(self, chemin_image, commande_id):
        """Affiche un popup pour visualiser l'image générée"""
        from kivy.uix.image import Image as KivyImage
        
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(18))
        _bg(content, BG_DARK)

        content.add_widget(Label(
            text=f"Facture N° {commande_id}[/b]\n\nImage générée avec succès !",
            markup=True,
            font_size=sp(15),
            color=TEXT_WHITE,
            size_hint=(1, None),
            height=dp(70),
            halign="center"
        ))

        # Aperçu de l'image
        try:
            preview = KivyImage(
                source=chemin_image,
                size_hint=(1, None),
                height=dp(180),
                allow_stretch=True,
                keep_ratio=True
            )
            content.add_widget(preview)
        except:
            pass

        info_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(40), spacing=dp(8))
        info_box.add_widget(Label(
            text=f"{os.path.basename(chemin_image)}",
            font_size=sp(11),
            color=ACCENT,
            halign="center"
        ))
        content.add_widget(info_box)

        btn_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint=(1, None))
        btn_box.height = dp(200)

        btn_partager = Button(
            text="PARTAGER",
            size_hint=(1, None), height=dp(45),
            font_size=sp(14), bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_partager, ACCENT_BLUE, radius=dp(8))
        btn_partager.bind(on_release=lambda x: self.partager_image(chemin_image))

        btn_enregistrer = Button(
            text="ENREGISTRER SUR LE TÉLÉPHONE",
            size_hint=(1, None), height=dp(45),
            font_size=sp(14), bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_enregistrer, ACCENT_GREEN, radius=dp(8))
        btn_enregistrer.bind(on_release=lambda x: self.enregistrer_sur_telephone(chemin_image))

        btn_imprimer = Button(
            text="IMPRIMER (NB80)",
            size_hint=(1, None), height=dp(45),
            font_size=sp(14), bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_imprimer, ACCENT_PURPLE, radius=dp(8))
        btn_imprimer.bind(on_release=lambda x: self.imprimer_image(chemin_image))

        btn_fermer = Button(
            text="FERMER",
            size_hint=(1, None), height=dp(45),
            font_size=sp(13),
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_fermer, ACCENT_RED, radius=dp(8))

        btn_box.add_widget(btn_partager)
        btn_box.add_widget(btn_enregistrer)
        btn_box.add_widget(btn_imprimer)
        btn_box.add_widget(btn_fermer)
        content.add_widget(btn_box)

        popup = Popup(
            title="Facture prête",
            content=content,
            size_hint=(0.9, 0.7),
            background_color=BG_CARD,
            title_size=sp(15)
        )
        btn_fermer.bind(on_release=popup.dismiss)
        popup.open()

    def partager_image(self, chemin_image):
        """Partage l'image via les applications disponibles"""
        try:
            if ANDROID_AVAILABLE:
                # Partage sur Android
                intent = Intent()
                intent.setAction(Intent.ACTION_SEND)
                intent.setType("image/jpeg")
                
                file = File(chemin_image)
                uri = Uri.fromFile(file)
                intent.putExtra(Intent.EXTRA_STREAM, uri)
                
                chooser = Intent.createChooser(intent, "Partager la facture")
                PythonActivity.mActivity.startActivity(chooser)
                self.show_message("Succès", "Partage lancé")
            else:
                import subprocess
                if sys.platform == 'win32':
                    subprocess.run(['explorer', '/select,', chemin_image])
                elif sys.platform == 'darwin':
                    subprocess.run(['open', '-R', chemin_image])
                else:
                    subprocess.run(['xdg-open', os.path.dirname(chemin_image)])
                self.show_message("Info", f"Image disponible: {chemin_image}")
        except Exception as e:
            self.show_message("Erreur", f"Erreur de partage: {e}")

    def enregistrer_sur_telephone(self, chemin_image):
        """Enregistre l'image dans la galerie du téléphone"""
        try:
            if ANDROID_AVAILABLE:
                # Pour Android, enregistrer dans les médias
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE])
                
                contentValues = MediaStore.Images.Media.getContentValues(
                    PythonActivity.mActivity, 
                    File(chemin_image), 
                    None
                )
                uri = PythonActivity.mActivity.getContentResolver().insert(
                    MediaStore.Images.Media.EXTERNAL_CONTENT_URI, 
                    contentValues
                )
                self.show_message("Succès", "Facture enregistrée dans la galerie")
            else:
                self.show_message("Info", f"Image enregistrée: {chemin_image}")
        except Exception as e:
            self.show_message("Erreur", f"Erreur d'enregistrement: {e}")

    def imprimer_image(self, chemin_image):
        """Prépare l'impression au format NB80"""
        try:
            if sys.platform == 'win32':
                os.startfile(chemin_image, "print")
            elif sys.platform == 'darwin':
                subprocess.run(['open', chemin_image])
            else:
                subprocess.run(['xdg-open', chemin_image])
            self.show_message(
                "Impression",
                f"Ouvrez l'image et utilisez l'impression.\n"
                "Pour l'impression NB80, réglez le format papier sur 80mm."
            )
        except Exception as e:
            self.show_message("Erreur", f"Erreur d'impression: {e}")

    # ═══════════════════════════════════════════════════
    # POPUP PAYER — saisie du montant
    # ═══════════════════════════════════════════════════
    def ouvrir_popup_payer(self, commande_id, client, reste_actuel):
        content = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(16))
        _bg(content, BG_DARK)

        content.add_widget(Label(
            text=f"[b]Commande N° {commande_id}  -  {client}[/b]",
            markup=True, font_size=sp(15), color=TEXT_WHITE,
            size_hint=(1, None), height=dp(32)
        ))
        content.add_widget(Label(
            text=f"Reste actuel : {reste_actuel:,.0f} Ar",
            font_size=sp(15), color=ACCENT_ORANGE,
            size_hint=(1, None), height=dp(30)
        ))
        content.add_widget(Label(
            text="Montant payé (Ar) :",
            font_size=sp(14), color=TEXT_WHITE,
            size_hint=(1, None), height=dp(28), halign="left"
        ))

        montant_input = TextInput(
            text=str(int(reste_actuel)),
            multiline=False,
            font_size=sp(15),
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(1, None),
            height=dp(50),
            padding=[dp(10), dp(10)]
        )
        content.add_widget(montant_input)

        # Mode de paiement
        mode_row = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(10))
        mode_row.add_widget(Label(
            text="Mode :",
            size_hint=(0.3, 1),
            color=TEXT_WHITE,
            font_size=sp(14),
            halign="right"
        ))
        self.mode_paiement_spinner = Spinner(
            text="Espèce",
            values=["Espèce", "Mvola", "Chèque"],
            size_hint=(0.7, 1),
            font_size=sp(14),
            background_color=(0.1, 0.16, 0.30, 1),
            color=TEXT_WHITE
        )
        mode_row.add_widget(self.mode_paiement_spinner)
        content.add_widget(mode_row)

        # Numéro de chèque (caché par défaut)
        self.cheque_row = BoxLayout(size_hint=(1, None), height=0, spacing=dp(10))
        self.cheque_row.add_widget(Label(
            text="N° Chèque :",
            size_hint=(0.3, 1),
            color=TEXT_WHITE,
            font_size=sp(14),
            halign="right"
        ))
        self.numero_cheque_input = TextInput(
            text="",
            multiline=False,
            font_size=sp(14),
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.7, 1),
            padding=[dp(8), dp(8)],
            hint_text="Numéro du chèque"
        )
        self.cheque_row.add_widget(self.numero_cheque_input)
        content.add_widget(self.cheque_row)

        # Dépôt de sortie
        depot_row = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(10))
        depot_row.add_widget(Label(
            text="Dépôt sortie :",
            size_hint=(0.3, 1),
            color=TEXT_WHITE,
            font_size=sp(14),
            halign="right"
        ))
        self.depot_sortie_input = TextInput(
            text="Dépôt principal",
            multiline=False,
            font_size=sp(14),
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.7, 1),
            padding=[dp(8), dp(8)],
            hint_text="Dépôt de sortie"
        )
        depot_row.add_widget(self.depot_sortie_input)
        content.add_widget(depot_row)

        def on_mode_change(spinner, text):
            if text == "Chèque":
                self.cheque_row.height = dp(50)
                self.cheque_row.size_hint_y = None
            else:
                self.cheque_row.height = 0
                self.cheque_row.size_hint_y = None
                self.numero_cheque_input.text = ""

        self.mode_paiement_spinner.bind(text=on_mode_change)

        btns = BoxLayout(size_hint=(1, None), height=dp(55), spacing=dp(12))
        btn_ok = Button(
            text="VALIDER",
            font_size=sp(15), bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_ok, ACCENT_GREEN, radius=dp(10))

        btn_cancel = Button(
            text="ANNULER",
            font_size=sp(15),
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_cancel, ACCENT_RED, radius=dp(10))

        btns.add_widget(btn_ok)
        btns.add_widget(btn_cancel)
        content.add_widget(btns)

        popup = Popup(
            title="Paiement du reste",
            content=content,
            size_hint=(0.9, 0.8),
            background_color=BG_CARD,
            title_size=sp(15)
        )
        btn_cancel.bind(on_release=popup.dismiss)

        btn_ok.bind(
            on_release=lambda inst: self.valider_paiement(
                popup, commande_id, client, reste_actuel, montant_input.text,
                self.mode_paiement_spinner.text, self.numero_cheque_input.text,
                self.depot_sortie_input.text
            )
        )
        popup.open()

    def valider_paiement(self, popup, commande_id, client_nom, reste_actuel, montant_txt, mode_paiement, numero_cheque, depot_sortie):
        """Valide le paiement et génère automatiquement l'image"""
        try:
            montant_txt = re.sub(r'[^0-9.]', '', montant_txt)
            if not montant_txt:
                montant_txt = "0"
            montant = float(montant_txt)

            if montant <= 0:
                self.show_message("Erreur", "Montant invalide")
                return

            if montant > reste_actuel:
                content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(12))
                content.add_widget(Label(
                    text=f"Le montant saisi ({montant:,.0f} Ar) dépasse\nle reste à payer ({reste_actuel:,.0f} Ar).\n\nVoulez-vous continuer ?",
                    color=TEXT_WHITE,
                    font_size=sp(13)
                ))
                btn_box = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(12))
                btn_oui = Button(text="OUI", size_hint=(0.5, 1), font_size=sp(14))
                btn_non = Button(text="NON", size_hint=(0.5, 1), font_size=sp(14))
                btn_box.add_widget(btn_oui)
                btn_box.add_widget(btn_non)
                content.add_widget(btn_box)

                confirm_popup = Popup(title="Confirmation", content=content, size_hint=(0.85, 0.4))
                btn_oui.bind(on_release=lambda x: self._executer_paiement(confirm_popup, popup, commande_id, client_nom, reste_actuel, montant, mode_paiement, numero_cheque, depot_sortie))
                btn_non.bind(on_release=confirm_popup.dismiss)
                confirm_popup.open()
            else:
                self._executer_paiement(None, popup, commande_id, client_nom, reste_actuel, montant, mode_paiement, numero_cheque, depot_sortie)

        except ValueError as e:
            self.show_message("Erreur", f"Montant invalide : {str(e)}")
        except Exception as e:
            self.show_message("Erreur", f"Erreur : {str(e)}")

    def _executer_paiement(self, confirm_popup, paiement_popup, commande_id, client_nom, reste_actuel, montant, mode_paiement, numero_cheque, depot_sortie):
        """Exécute le paiement après confirmation et génère l'image"""
        try:
            if confirm_popup:
                confirm_popup.dismiss()

            commande = get_commande_by_id(commande_id)
            if not commande:
                self.show_message("Erreur", f"Commande N° {commande_id} introuvable")
                return

            ancien_reste = float(commande.get('reste', reste_actuel))
            ancienne_avance = float(commande.get('avance', 0))

            nouveau_reste = max(0.0, ancien_reste - montant)
            nouvelle_avance = ancienne_avance + montant

            ok = payer_reste_db(commande_id, montant, nouveau_reste)

            if not ok:
                self.show_message("Erreur", "Erreur lors de l'enregistrement du paiement")
                return

            paiement_popup.dismiss()

            message = f"Paiement enregistré !\n\n"
            message += f"Montant payé : {montant:,.0f} Ar\n"
            message += f"Nouveau reste : {nouveau_reste:,.0f} Ar"
            message += f"\nMode : {mode_paiement}"

            if mode_paiement == "Chèque" and numero_cheque:
                message += f"\nN° Chèque : {numero_cheque}"

            # Génération automatique de l'image après paiement
            try:
                client_info = {'adresse': '', 'nif': '', 'stat': '', 'contact': ''}
                clients_data = get_all_clients()
                for c in clients_data:
                    if len(c) >= 5:
                        if isinstance(c[0], int) and c[0] is not None:
                            if str(c[1]) == client_nom:
                                client_info = {
                                    'adresse': str(c[2]) if len(c) > 2 and c[2] else "",
                                    'nif': str(c[3]) if len(c) > 3 and c[3] else "",
                                    'stat': str(c[4]) if len(c) > 4 and c[4] else "",
                                    'contact': str(c[5]) if len(c) > 5 and c[5] else ""
                                }
                                break
                        else:
                            if str(c[0]) == client_nom:
                                client_info = {
                                    'adresse': str(c[1]) if len(c) > 1 and c[1] else "",
                                    'nif': str(c[2]) if len(c) > 2 and c[2] else "",
                                    'stat': str(c[3]) if len(c) > 3 and c[3] else "",
                                    'contact': str(c[4]) if len(c) > 4 and c[4] else ""
                                }
                                break

                commande['avance'] = nouvelle_avance
                commande['reste'] = nouveau_reste

                filename = generer_image_facture(
                    commande_id=commande_id,
                    client_nom=client_nom,
                    client_info=client_info,
                    produits=commande.get('produits', []),
                    total=float(commande.get('total', 0)),
                    avance=nouvelle_avance,
                    reste=nouveau_reste,
                    date_str=datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                    mode_paiement=mode_paiement,
                    depot_sortie=depot_sortie,
                    numero_cheque=numero_cheque if mode_paiement == "Chèque" else ""
                )

                if filename:
                    message += f"\n\nFacture générée avec succès !"
                    self.afficher_apercu_image(filename, commande_id)
                else:
                    message += f"\n\nErreur lors de la génération de l'image"
            except Exception as e:
                message += f"\n\nErreur image : {str(e)}"

            self.show_message("Succès", message)
            Clock.schedule_once(lambda dt: self.charger_commandes(None), 0.5)

        except Exception as e:
            self.show_message("Erreur", f"Erreur lors du paiement : {str(e)}")

    # ═══════════════════════════════════════════════════
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(14))
        _bg(content, BG_DARK)

        lbl = Label(
            text=message,
            color=TEXT_WHITE,
            font_size=sp(13),
            size_hint=(1, 0.8),
            halign="left",
            valign="top",
            text_size=(None, None)
        )
        lbl.bind(size=lambda inst, s: setattr(inst, 'text_size', (s[0] - 10, s[1])))
        content.add_widget(lbl)

        btn = Button(
            text="OK",
            size_hint=(1, 0.15),
            font_size=sp(14),
            bold=True,
            background_normal="",
            background_color=ACCENT_GREEN,
            color=TEXT_WHITE
        )
        _bg(btn, ACCENT_GREEN, radius=dp(8))
        content.add_widget(btn)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, 0.45),
            background_color=BG_CARD,
            title_size=sp(14)
        )
        btn.bind(on_release=popup.dismiss)
        popup.open()

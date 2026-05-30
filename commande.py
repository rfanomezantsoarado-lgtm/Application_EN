# commande.py (version modifiée avec ajout du champ RENDU)
#Importation des bibliothèques utile
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from database import (init_database, get_all_produits, get_all_clients,
                      ajouter_commande_db, payer_reste_db, get_all_commandes)
import datetime
import os
import re
import subprocess
import sys
from kivy.utils import platform

# Remplacer pdf_generator par image_generator
from image_generator import generer_facture_proforma

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
ACCENT_PURPLE = (0.55, 0.08, 0.82, 1)
TEXT_WHITE    = (1, 1, 1, 1)
ROW_ODD       = (0.10, 0.16, 0.30, 1)
ROW_EVEN      = (0.07, 0.12, 0.24, 1)
HEADER_BG     = (0.05, 0.35, 0.65, 1)
BAR_TOP       = (0.05, 0.08, 0.18, 1)
TEXT_DIM      = (0.6, 0.6, 0.6, 1)
ACCENT_BLUE   = (0.08, 0.45, 0.82, 1)


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


def make_cell(text, w, bg_color, bold=False, font_size=13):
    lbl = Label(
        text=f"[b]{text}[/b]" if bold else text,
        markup=bold,
        size_hint=(None, None),
        size=(w, 45),
        font_size=font_size,
        color=TEXT_WHITE,
        halign="center",
        valign="middle"
    )
    lbl.bind(size=lambda inst, v: setattr(inst, "text_size", v))
    _bg(lbl, bg_color)
    return lbl


class CommandeScreen(Screen):

    HEADERS_COMMANDE = ["Designation", "Prix unitaire", "Quantite", "Montant", "Actions"]
    COL_WIDTHS_COMMANDE = [150, 110, 90, 110, 170]
    ROW_H = 45

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.produits_disponibles = []
        self.produits_commandes = []
        self.clients_disponibles = []
        self.total_commande = 0
        self._derniere_commande_id = None
        self.produit_selectionne_index = None

        main_scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=8,
            bar_color=list(ACCENT[:3]) + [0.8]
        )
        main_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=10,
            padding=[8, 8, 8, 8]
        )
        main_container.bind(minimum_height=main_container.setter('height'))

        # ── BARRE HAUTE ───────────────────────────────────
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=60,
            padding=[10, 8, 10, 8],
            spacing=10
        )
        _bg(top_bar, BAR_TOP)

        top_bar.add_widget(Label(size_hint=(None, 1), width=80))
        title_label = Label(
            text="[b]GESTION COMMANDE[/b]",
            markup=True, font_size=20,
            color=TEXT_WHITE, size_hint=(1, 1),
            halign="center", valign="middle"
        )
        title_label.bind(size=lambda inst, v: setattr(inst, "text_size", v))
        top_bar.add_widget(title_label)
        top_bar.add_widget(Label(size_hint=(None, 1), width=80))
        main_container.add_widget(top_bar)

        # ── SECTION DATE ET LIEU ─────────────────────────
        info_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None), height=130,
            padding=[12, 10, 12, 10],
            spacing=8
        )
        _bg(info_card, BG_CARD, radius=12)
        info_card.add_widget(Label(
            text="[b]Informations de la commande[/b]", markup=True,
            font_size=14, color=ACCENT,
            size_hint=(1, None), height=25, halign="left"
        ))

        # Ligne Date
        date_row = BoxLayout(size_hint=(1, None), height=40, spacing=10)
        date_row.add_widget(Label(
            text="Date :", size_hint=(0.25, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.date_commande = Label(
            text=datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
            size_hint=(0.75, 1),
            color=ACCENT_GREEN, font_size=13,
            halign="left", valign="middle"
        )
        self.date_commande.bind(size=lambda inst, v: setattr(inst, "text_size", (v[0], None)))
        date_row.add_widget(self.date_commande)
        info_card.add_widget(date_row)

        # Ligne Lieu de paiement
        lieu_row = BoxLayout(size_hint=(1, None), height=40, spacing=10)
        lieu_row.add_widget(Label(
            text="Lieu de paiement :", size_hint=(0.5, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.lieu_paiement = TextInput(
            text="", multiline=False, font_size=13,
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.75, 1), padding=[10, 10]
        )
        lieu_row.add_widget(self.lieu_paiement)
        info_card.add_widget(lieu_row)

        main_container.add_widget(info_card)

        # ── SECTION CLIENT ────────────────────────────────
        client_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None), height=180,
            padding=[12, 10, 12, 10],
            spacing=8
        )
        _bg(client_card, BG_CARD, radius=12)
        client_card.add_widget(Label(
            text="[b]Informations client[/b]", markup=True,
            font_size=14, color=ACCENT,
            size_hint=(1, None), height=25, halign="left"
        ))
        client_row = BoxLayout(size_hint=(1, None), height=45, spacing=10)
        client_row.add_widget(Label(
            text="Client :", size_hint=(0.2, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.client_spinner = Spinner(
            text="Choisir un client", values=[],
            size_hint=(0.8, 1), font_size=13,
            background_color=(0.1, 0.16, 0.30, 1), color=TEXT_WHITE
        )
        self.client_spinner.bind(text=self.on_client_select)
        client_row.add_widget(self.client_spinner)
        client_card.add_widget(client_row)
        self.client_details = Label(
            text="", font_size=12, color=TEXT_WHITE,
            size_hint=(1, None), height=60,
            halign="left", valign="top"
        )
        self.client_details.bind(
            size=lambda inst, v: setattr(inst, "text_size", (v[0] - 15, None))
        )
        client_card.add_widget(self.client_details)
        main_container.add_widget(client_card)

        # ── DÉPÔT DE SORTIE ──────────────────────────────
        depot_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None), height=90,
            padding=[12, 10, 12, 10],
            spacing=8
        )
        _bg(depot_card, BG_CARD, radius=12)
        depot_card.add_widget(Label(
            text="[b]Dépôt de sortie de stock[/b]", markup=True,
            font_size=14, color=ACCENT,
            size_hint=(1, None), height=25
        ))
        depot_row = BoxLayout(size_hint=(1, None), height=40, spacing=10)
        depot_row.add_widget(Label(
            text="Dépôt :", size_hint=(0.25, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.depot_sortie = TextInput(
            text="", multiline=False, font_size=13,
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.75, 1), padding=[10, 10]
        )
        depot_row.add_widget(self.depot_sortie)
        depot_card.add_widget(depot_row)
        main_container.add_widget(depot_card)

        # ── SECTION PRODUIT ───────────────────────────────
        produit_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None), height=200,
            padding=[12, 10, 12, 10],
            spacing=8
        )
        _bg(produit_card, BG_CARD, radius=12)

        self.produit_title = Label(
            text="[b]Ajouter un produit[/b]", markup=True,
            font_size=14, color=ACCENT,
            size_hint=(1, None), height=25
        )
        produit_card.add_widget(self.produit_title)

        produit_row = BoxLayout(size_hint=(1, None), height=42, spacing=10)
        produit_row.add_widget(Label(
            text="Produit :", size_hint=(0.25, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.produit_spinner = Spinner(
            text="Choisir un produit", values=[],
            size_hint=(0.75, 1), font_size=13,
            background_color=(0.1, 0.16, 0.30, 1), color=TEXT_WHITE
        )
        self.produit_spinner.bind(text=self.on_produit_select)
        produit_row.add_widget(self.produit_spinner)
        produit_card.add_widget(produit_row)

        prix_row = BoxLayout(size_hint=(1, None), height=42, spacing=10)
        prix_row.add_widget(Label(
            text="Prix unitaire (Ar) :", size_hint=(0.25, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.prix_vente_client = TextInput(
            text="", multiline=False, font_size=13,
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.5, 1), padding=[10, 10]
        )
        prix_row.add_widget(self.prix_vente_client)
        prix_row.add_widget(Label(size_hint=(0.25, 1)))
        produit_card.add_widget(prix_row)

        quantite_row = BoxLayout(size_hint=(1, None), height=42, spacing=10)
        quantite_row.add_widget(Label(
            text="Quantite :", size_hint=(0.25, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.quantite = TextInput(
            text="1", multiline=False, font_size=13,
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.2, 1), padding=[10, 10]
        )
        self.quantite.bind(text=self.on_quantite_change)
        quantite_row.add_widget(self.quantite)

        btn_container = BoxLayout(size_hint=(0.6, 1), spacing=8)
        btn_ajouter = Button(
            text="+ AJOUTER", size_hint=(1, 1),
            font_size=13, bold=True,
            background_normal="",
            background_color=ACCENT, color=TEXT_WHITE
        )
        btn_ajouter.bind(on_release=self.ajouter_produit_commande)
        btn_container.add_widget(btn_ajouter)

        btn_modifier = Button(
            text="MODIFIER", size_hint=(1, 1),
            font_size=12, bold=True,
            background_normal="",
            background_color=ACCENT_ORANGE, color=TEXT_WHITE
        )
        btn_modifier.bind(on_release=self.modifier_produit_commande)
        btn_container.add_widget(btn_modifier)

        quantite_row.add_widget(btn_container)
        quantite_row.add_widget(Label(size_hint=(0.05, 1)))
        produit_card.add_widget(quantite_row)
        main_container.add_widget(produit_card)

        # ── TABLEAU PRODUITS COMMANDES ────────────────────
        self.lbl_count_commande = Label(
            text="Produits commandes  -  0 article(s)",
            font_size=12, color=TEXT_WHITE,
            size_hint=(1, None), height=28,
            halign="left", valign="middle"
        )
        main_container.add_widget(self.lbl_count_commande)

        table_commande_container = BoxLayout(size_hint=(1, None), height=250)
        total_w_commande = sum(self.COL_WIDTHS_COMMANDE)
        self.table_commande = GridLayout(
            cols=5,
            size_hint=(None, None), width=total_w_commande,
            row_default_height=self.ROW_H, row_force_default=True,
            spacing=0, padding=0
        )
        self.table_commande.bind(minimum_height=self.table_commande.setter('height'))
        for h, w in zip(self.HEADERS_COMMANDE, self.COL_WIDTHS_COMMANDE):
            self.table_commande.add_widget(
                make_cell(h, w, HEADER_BG, bold=True, font_size=12)
            )
        scroll_commande = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True, do_scroll_y=True, bar_width=6
        )
        scroll_commande.add_widget(self.table_commande)
        table_commande_container.add_widget(scroll_commande)
        main_container.add_widget(table_commande_container)

        # ── SECTION PAIEMENT ─────────────────────────────
        paiement_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None), height=310,  # Augmenté pour inclure le champ RENDU
            padding=[12, 10, 12, 10],
            spacing=8
        )
        _bg(paiement_card, BG_CARD, radius=12)
        paiement_card.add_widget(Label(
            text="[b]Informations de paiement[/b]", markup=True,
            font_size=14, color=ACCENT,
            size_hint=(1, None), height=25
        ))

        # Mode de paiement
        mode_row = BoxLayout(size_hint=(1, None), height=40, spacing=10)
        mode_row.add_widget(Label(
            text="Mode de paiement :", size_hint=(0.3, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.mode_paiement = Spinner(
            text="Espèce",
            values=["Espèce", "Mvola", "Chèque"],
            size_hint=(0.7, 1),
            font_size=12,
            background_color=(0.1, 0.16, 0.30, 1),
            color=TEXT_WHITE
        )
        self.mode_paiement.bind(text=self.on_mode_paiement_change)
        mode_row.add_widget(self.mode_paiement)
        paiement_card.add_widget(mode_row)

        # Numéro de chèque
        cheque_row = BoxLayout(size_hint=(1, None), height=40, spacing=10)
        cheque_row.add_widget(Label(
            text="N° Chèque :", size_hint=(0.3, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.numero_cheque = TextInput(
            text="", multiline=False, font_size=13,
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.7, 1), padding=[10, 10]
        )
        cheque_row.add_widget(self.numero_cheque)
        paiement_card.add_widget(cheque_row)

        # Cacher la ligne du chèque
        self.cheque_row = cheque_row
        self.cheque_row.opacity = 0
        self.cheque_row.height = 0
        self.cheque_row.size_hint_y = None

        total_row = BoxLayout(size_hint=(1, None), height=40, spacing=10)
        total_row.add_widget(Label(
            text="Total commande (Ar) :", size_hint=(0.5, 1),
            color=TEXT_WHITE, font_size=14, bold=True, halign="right"
        ))
        self.lbl_total = Label(
            text="0", size_hint=(0.5, 1),
            color=ACCENT_GREEN, font_size=15,
            bold=True, halign="left", valign="middle"
        )
        total_row.add_widget(self.lbl_total)
        paiement_card.add_widget(total_row)

        avance_row = BoxLayout(size_hint=(1, None), height=42, spacing=10)
        avance_row.add_widget(Label(
            text="Montant versé (Ar) :", size_hint=(0.5, 1),
            color=TEXT_WHITE, font_size=13, halign="right"
        ))
        self.montant_verse = TextInput(
            text="0", multiline=False, font_size=13,
            foreground_color=TEXT_WHITE,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.5, 1), padding=[10, 10]
        )
        self.montant_verse.bind(text=self.calculer_reste_et_rendu)
        avance_row.add_widget(self.montant_verse)
        paiement_card.add_widget(avance_row)

        # Ligne RENDU (cachée par défaut, visible uniquement pour Espèce et si montant > total)
        rendu_row = BoxLayout(size_hint=(1, None), height=0, spacing=10)
        rendu_row.add_widget(Label(
            text="RENDU (Ar) :", size_hint=(0.5, 1),
            color=ACCENT_GREEN, font_size=13, bold=True, halign="right"
        ))
        self.rendu_client = TextInput(
            text="0", multiline=False, font_size=13,
            foreground_color=ACCENT_GREEN,
            background_color=(0.1, 0.16, 0.30, 1),
            size_hint=(0.5, 1), padding=[10, 10], disabled=True,
            disabled_foreground_color=ACCENT_GREEN
        )
        rendu_row.add_widget(self.rendu_client)
        paiement_card.add_widget(rendu_row)
        self.rendu_row = rendu_row

        reste_row = BoxLayout(size_hint=(1, None), height=42, spacing=10)
        reste_row.add_widget(Label(
            text="Reste à payer (Ar) :", size_hint=(0.5, 1),
            color=ACCENT_RED,
            font_size=13, bold=True, halign="right"
        ))
        self.reste_payer = TextInput(
            text="0", multiline=False, font_size=14,
            foreground_color=ACCENT_RED,
            background_color=(0.08, 0.12, 0.25, 1),
            size_hint=(0.5, 1), padding=[10, 10], disabled=True,
            disabled_foreground_color=ACCENT_RED
        )
        reste_row.add_widget(self.reste_payer)
        paiement_card.add_widget(reste_row)

        main_container.add_widget(paiement_card)

        # ── BOUTONS ────────────────────────────────────────
        btn_row = BoxLayout(
            size_hint=(1, None), height=55,
            padding=[12, 8, 12, 8], spacing=12
        )

        btn_abandonner = Button(
            text="FERMER",
            font_size=13, bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0), color=TEXT_WHITE
        )
        _bg(btn_abandonner, ACCENT_RED, radius=8)
        btn_abandonner.bind(on_release=self.abandonner_commande)

        btn_pdf = Button(
            text="ENREGISTRER",
            font_size=13, bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0), color=TEXT_WHITE
        )
        _bg(btn_pdf, ACCENT_PURPLE, radius=8)
        btn_pdf.bind(on_release=self.exporter_image)

        btn_row.add_widget(btn_abandonner)
        btn_row.add_widget(btn_pdf)
        main_container.add_widget(btn_row)

        main_scroll.add_widget(main_container)
        self.add_widget(main_scroll)
        Clock.schedule_once(lambda dt: self.initialiser_donnees(), 0.5)

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES PRINCIPALES
    # ═══════════════════════════════════════════════════════════

    def abandonner_commande(self, instance):
        self.reset_commande(None)
        self.manager.current = "accueil"

    def ajouter_produit_commande(self, instance):
        nom = self.produit_spinner.text
        if nom == "Choisir un produit":
            self.show_message("Info", "Sélectionnez un produit")
            return
        try:
            prix = float(re.sub(r'[^0-9.]', '', self.prix_vente_client.text or "0") or 0)
            qte = int(self.quantite.text or "1")
            if prix <= 0:
                self.show_message("Erreur", "Prix invalide")
                return
        except ValueError:
            self.show_message("Erreur", "Vérifiez prix et quantité")
            return

        self.produits_commandes.append(
            {'nom': nom, 'prix_unitaire': prix, 'quantite': qte, 'total': prix * qte}
        )
        self.actualiser_tableau_commande()
        self.produit_spinner.text = "Choisir un produit"
        self.prix_vente_client.text = ""
        self.quantite.text = "1"
        self.produit_selectionne_index = None
        self.produit_title.text = "[b]Ajouter un produit[/b]"

    def modifier_produit_commande(self, instance):
        if self.produit_selectionne_index is None:
            self.show_message("Info", "Sélectionnez d'abord un produit dans le tableau")
            return

        nom = self.produit_spinner.text
        if nom == "Choisir un produit":
            self.show_message("Info", "Sélectionnez un produit")
            return

        try:
            prix = float(re.sub(r'[^0-9.]', '', self.prix_vente_client.text or "0") or 0)
            qte = int(self.quantite.text or "1")
            if prix <= 0:
                self.show_message("Erreur", "Prix invalide")
                return
        except ValueError:
            self.show_message("Erreur", "Vérifiez prix et quantité")
            return

        self.produits_commandes[self.produit_selectionne_index] = {
            'nom': nom,
            'prix_unitaire': prix,
            'quantite': qte,
            'total': prix * qte
        }

        self.actualiser_tableau_commande()
        self.produit_spinner.text = "Choisir un produit"
        self.prix_vente_client.text = ""
        self.quantite.text = "1"
        self.produit_selectionne_index = None
        self.produit_title.text = "[b]Ajouter un produit[/b]"

    def supprimer_produit_commande(self, index):
        del self.produits_commandes[index]
        self.actualiser_tableau_commande()

        if self.produit_selectionne_index == index:
            self.produit_selectionne_index = None
            self.produit_title.text = "[b]Ajouter un produit[/b]"
            self.produit_spinner.text = "Choisir un produit"
            self.prix_vente_client.text = ""
            self.quantite.text = "1"
        elif self.produit_selectionne_index is not None and self.produit_selectionne_index > index:
            self.produit_selectionne_index -= 1

    def editer_produit_commande(self, index):
        produit = self.produits_commandes[index]
        self.produit_selectionne_index = index
        self.produit_title.text = "[b]MODIFIER LE PRODUIT[/b]"
        self.produit_spinner.text = produit['nom']
        self.prix_vente_client.text = str(produit['prix_unitaire'])
        self.quantite.text = str(produit['quantite'])

    def calculer_reste_et_rendu(self, *args):
        """Calcule le reste à payer et le rendu pour l'espèce"""
        try:
            montant_text = re.sub(r'[^0-9.]', '', self.montant_verse.text or "0")
            montant = float(montant_text) if montant_text else 0
            total = self.total_commande

            mode = self.mode_paiement.text

            if mode == "Espèce":
                if montant > total:
                    # Afficher le rendu
                    rendu = montant - total
                    self.rendu_client.text = f"{rendu:,.0f}"
                    self.reste_payer.text = "0"

                    # Afficher la ligne RENDU
                    self.rendu_row.height = 42
                    self.rendu_row.size_hint_y = None
                    self.rendu_row.opacity = 1
                else:
                    # Pas de rendu
                    self.rendu_client.text = "0"
                    reste = total - montant
                    self.reste_payer.text = f"{reste:,.0f}"

                    # Cacher la ligne RENDU
                    self.rendu_row.height = 0
                    self.rendu_row.size_hint_y = None
                    self.rendu_row.opacity = 0
            else:
                # Pour Mvola et Chèque, on cache toujours le rendu
                self.rendu_row.height = 0
                self.rendu_row.size_hint_y = None
                self.rendu_row.opacity = 0
                reste = max(0, total - montant)
                self.reste_payer.text = f"{reste:,.0f}"

        except ValueError:
            self.reste_payer.text = "0"
            self.rendu_client.text = "0"

    def exporter_image(self, instance):
        if not self._valider_commande():
            return
        if not self.depot_sortie.text.strip():
            self.show_message("Information", "Veuillez saisir le dépôt de sortie de stock")
            return
        try:
            montant_verse = self._get_montant_verse()
            reste = max(0, self.total_commande - montant_verse)
            mode_paiement = self.mode_paiement.text
            depot_sortie = self.depot_sortie.text.strip()
            lieu_paiement = self.lieu_paiement.text.strip() or "Non spécifié"

            # Récupérer le rendu si mode Espèce
            rendu = 0
            if mode_paiement == "Espèce" and montant_verse > self.total_commande:
                rendu = montant_verse - self.total_commande
                montant_verse = self.total_commande
                reste = 0

            numero_cheque = ""
            if mode_paiement == "Chèque":
                numero_cheque = self.numero_cheque.text.strip()
                if not numero_cheque:
                    self.show_message("Information", "Veuillez saisir le numéro du chèque")
                    return

            commande_id = ajouter_commande_db(
                client_nom=self.client_spinner.text,
                produits=self.produits_commandes,
                total=self.total_commande,
                avance=montant_verse,
                reste=reste,
                mode_paiement=mode_paiement,
                numero_cheque=numero_cheque,
                date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                depot_sortie=depot_sortie,
                lieu_paiement=lieu_paiement
            )
            if not commande_id:
                self.show_message("Erreur", "Erreur lors de l'enregistrement")
                return

            client_info = {}
            for c in self.clients_disponibles:
                if c['nom'] == self.client_spinner.text:
                    client_info = c
                    break

            filename = generer_facture_proforma(
                commande_id=commande_id,
                client_nom=self.client_spinner.text,
                client_info=client_info,
                produits=self.produits_commandes,
                total=self.total_commande,
                avance=montant_verse,
                reste=reste,
                mode_paiement=mode_paiement,
                depot_sortie=depot_sortie,
                numero_cheque=numero_cheque,
                date_str=datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),
                lieu_paiement=lieu_paiement,
                rendu=rendu
            )

            if filename:
                message = f"Commande enregistrée N° {commande_id}"
                if rendu > 0:
                    message += f"\nRENDU à rendre au client : {rendu:,.0f} Ar"
                self.show_message("Succès", message)
                self.afficher_apercu_image(filename, commande_id)
            else:
                self.show_message("Erreur", "Erreur lors de la génération de l'image")

            self.reset_commande(None)

        except Exception as e:
            self.show_message("Erreur", str(e))

    def afficher_apercu_image(self, chemin_image, commande_id):
        from kivy.uix.image import Image as KivyImage

        content = BoxLayout(orientation='vertical', spacing=12, padding=15)
        _bg(content, BG_DARK)

        content.add_widget(Label(
            text=f"Facture N° {commande_id}[/b]",
            markup=True,
            font_size=13,
            color=TEXT_WHITE,
            size_hint=(1, None),
            height=40,
            halign="center"
        ))

        info_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=100, spacing=5)
        info_box.add_widget(Label(
            text=f"{os.path.basename(chemin_image)}",
            font_size=10,
            color=ACCENT,
            halign="center"
        ))
        content.add_widget(info_box)

        btn_box = BoxLayout(orientation='vertical', spacing=8, size_hint=(1, None))
        btn_box.height = 170

        btn_enregistrer = Button(
            text="ENREGISTRER SUR TELEPHONE",
            size_hint=(1, None), height=38,
            font_size=12, bold=True,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_enregistrer, ACCENT_GREEN, radius=6)
        btn_enregistrer.bind(on_release=lambda x: self.enregistrer_sur_telephone(chemin_image))


        btn_fermer = Button(
            text="FERMER",
            size_hint=(1, None), height=38,
            font_size=11,
            background_normal="",
            background_color=(0, 0, 0, 0),
            color=TEXT_WHITE
        )
        _bg(btn_fermer, ACCENT_RED, radius=6)

        btn_box.add_widget(btn_enregistrer)
        btn_box.add_widget(btn_fermer)
        content.add_widget(btn_box)

        popup = Popup(
            title="Facture prête",
            content=content,
            size_hint=(0.9, 0.65),
            background_color=BG_CARD
        )
        btn_fermer.bind(on_release=popup.dismiss)
        popup.open()

    def enregistrer_sur_telephone(self, chemin_image):
        try:
            if ANDROID_AVAILABLE:
                import shutil
                import time

                possible_paths = [
                    os.path.join(os.environ.get('EXTERNAL_STORAGE', '/storage/emulated/0'), 'Pictures', 'Factures'),
                    os.path.join('/storage/emulated/0', 'Pictures', 'Factures'),
                    os.path.join('/sdcard', 'Pictures', 'Factures'),
                    PythonActivity.mActivity.getExternalFilesDir(None).getAbsolutePath() + '/Factures'
                ]

                pictures_dir = None
                for path in possible_paths:
                    try:
                        if path and os.path.exists(os.path.dirname(path)):
                            pictures_dir = path
                            break
                    except:
                        continue

                if not pictures_dir:
                    pictures_dir = os.path.join(os.path.dirname(chemin_image), 'Factures_saved')

                if not os.path.exists(pictures_dir):
                    os.makedirs(pictures_dir)

                nom_fichier = os.path.basename(chemin_image)
                destination = os.path.join(pictures_dir, nom_fichier)
                shutil.copy2(chemin_image, destination)

                try:
                    intent = Intent()
                    intent.setAction(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE)
                    intent.setData(Uri.fromFile(File(destination)))
                    PythonActivity.mActivity.sendBroadcast(intent)
                except:
                    pass

                self.show_message("Succès", f"Facture enregistrée dans:\n{pictures_dir}")
            else:
                self.show_message("Info", f"Image enregistrée: {chemin_image}")
        except Exception as e:
            self.show_message("Info", f"Image disponible à:\n{chemin_image}")

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES UTILITAIRES
    # ═══════════════════════════════════════════════════════════

    def _valider_commande(self):
        if not self.produits_commandes:
            self.show_message("Erreur", "Aucun produit dans la commande")
            return False
        if self.client_spinner.text == "Choisir un client":
            self.show_message("Erreur", "Veuillez sélectionner un client")
            return False
        return True

    def _get_montant_verse(self):
        montant_text = re.sub(r'[^0-9.]', '', self.montant_verse.text or "0")
        montant = float(montant_text) if montant_text else 0
        return montant

    def on_enter(self):
        self.date_commande.text = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self.initialiser_donnees()

    def initialiser_donnees(self):
        try:
            init_database()
            self.charger_produits()
            self.charger_clients()
        except Exception as e:
            print(f"Erreur init: {e}")

    def charger_clients(self):
        try:
            clients_data = get_all_clients()
            self.clients_disponibles = []
            lst = []

            for c in clients_data:
                if len(c) >= 5:
                    if isinstance(c[0], int) and c[0] is not None:
                        nom_client = str(c[1]) if c[1] else "Sans nom"
                        client_dict = {
                            'nom': nom_client,
                            'adresse': str(c[2]) if len(c) > 2 and c[2] else "",
                            'contact': str(c[3]) if len(c) > 3 and c[3] else "",
                            'responsable': str(c[4]) if len(c) > 4 and c[4] else ""
                        }
                    else:
                        nom_client = str(c[0]) if c[0] else "Sans nom"
                        client_dict = {
                            'nom': nom_client,
                            'adresse': str(c[2]) if len(c) > 2 and c[2] else "",
                            'contact': str(c[3]) if len(c) > 3 and c[3] else "",
                            'responsable': str(c[4]) if len(c) > 4 and c[4] else ""
                        }

                    self.clients_disponibles.append(client_dict)
                    lst.append(nom_client)

            if self.client_spinner:
                self.client_spinner.values = lst

        except Exception as e:
            print(f"Erreur chargement clients: {e}")

    def charger_produits(self):
        try:
            produits_data = get_all_produits()
            self.produits_disponibles = []
            lst = []

            for p in produits_data:
                if len(p) >= 3:
                    if isinstance(p[0], int) and p[0] is not None:
                        nom_produit = str(p[1]) if p[1] else "Sans nom"
                        prix_vente = str(p[3]) if len(p) > 3 and p[3] else "0"
                    else:
                        nom_produit = str(p[0]) if p[0] else "Sans nom"
                        prix_vente = str(p[2]) if len(p) > 2 and p[2] else "0"

                    self.produits_disponibles.append({
                        'nom': nom_produit,
                        'prix_vente': prix_vente
                    })
                    lst.append(nom_produit)

            if self.produit_spinner:
                self.produit_spinner.values = lst

        except Exception as e:
            print(f"Erreur chargement produits: {e}")

    def on_client_select(self, spinner, text):
        if text != "Choisir un client" and self.client_details:
            for c in self.clients_disponibles:
                if c['nom'] == text:
                    self.client_details.text = (
                        f"[b]Adresse:[/b] {c['adresse']}\n"
                        f"[b]Contact:[/b] {c['contact']} | "
                        f"[b]Responsable:[/b] {c['responsable']}"
                    )
                    self.client_details.markup = True
                    break
        elif self.client_details:
            self.client_details.text = ""

    def on_produit_select(self, spinner, text):
        if text != "Choisir un produit" and text:
            for p in self.produits_disponibles:
                if p['nom'] == text:
                    prix = str(p['prix_vente'])
                    self.prix_vente_client.text = prix
                    break
            else:
                self.prix_vente_client.text = ""

    def on_quantite_change(self, instance, value):
        if value and not value.isdigit():
            nv = re.sub(r'[^0-9]', '', value) or "1"
            self.quantite.text = nv

    def actualiser_tableau_commande(self):
        if not self.table_commande:
            return
        enfants = list(self.table_commande.children)
        nb = len(self.HEADERS_COMMANDE)
        for e in (enfants[:-nb] if len(enfants) > nb else []):
            self.table_commande.remove_widget(e)

        self.total_commande = 0
        for idx, p in enumerate(self.produits_commandes):
            rc = ROW_ODD if idx % 2 == 0 else ROW_EVEN

            self.table_commande.add_widget(
                make_cell(p['nom'], self.COL_WIDTHS_COMMANDE[0], rc, bold=False, font_size=12)
            )
            self.table_commande.add_widget(
                make_cell(f"{p['prix_unitaire']:,.0f}", self.COL_WIDTHS_COMMANDE[1], rc, bold=False, font_size=12)
            )
            self.table_commande.add_widget(
                make_cell(str(p['quantite']), self.COL_WIDTHS_COMMANDE[2], rc, bold=False, font_size=12)
            )
            self.table_commande.add_widget(
                make_cell(f"{p['total']:,.0f}", self.COL_WIDTHS_COMMANDE[3], rc, bold=False, font_size=12)
            )

            actions_layout = BoxLayout(spacing=5, size_hint=(None, None),
                                        size=(self.COL_WIDTHS_COMMANDE[4], self.ROW_H))
            _bg(actions_layout, rc)

            btn_edit = Button(
                text="Modifier", font_size=16, bold=True,
                size_hint=(0.5, 1), background_normal="",
                background_color=(0.08, 0.45, 0.82, 1), color=TEXT_WHITE
            )
            btn_edit.bind(on_release=lambda btn, i=idx: self.editer_produit_commande(i))

            btn_delete = Button(
                text="Supprimer", font_size=16, bold=True,
                size_hint=(0.5, 1), background_normal="",
                background_color=(0.82, 0.08, 0.08, 1), color=TEXT_WHITE
            )
            btn_delete.bind(on_release=lambda btn, i=idx: self.supprimer_produit_commande(i))

            actions_layout.add_widget(btn_edit)
            actions_layout.add_widget(btn_delete)
            self.table_commande.add_widget(actions_layout)

            self.total_commande += p['total']

        if self.lbl_total:
            self.lbl_total.text = f"{self.total_commande:,.0f} Ar"
        if self.lbl_count_commande:
            self.lbl_count_commande.text = (
                f"Produits commandés  -  {len(self.produits_commandes)} article(s)"
            )
        self.calculer_reste_et_rendu()

    def reset_commande(self, instance):
        self.produits_commandes = []
        self.total_commande = 0
        self.produit_selectionne_index = None
        self.produit_title.text = "[b]Ajouter un produit[/b]"

        if self.table_commande:
            enfants = list(self.table_commande.children)
            nb = len(self.HEADERS_COMMANDE)
            for e in (enfants[:-nb] if len(enfants) > nb else []):
                self.table_commande.remove_widget(e)

        self.lbl_total.text = '0'
        self.lbl_count_commande.text = 'Produits commandés  -  0 article(s)'

        self.client_spinner.text = 'Choisir un client'
        self.produit_spinner.text = 'Choisir un produit'
        self.prix_vente_client.text = ''
        self.quantite.text = '1'
        self.montant_verse.text = '0'
        self.reste_payer.text = '0'
        self.rendu_client.text = '0'
        self.mode_paiement.text = 'Espèce'
        self.numero_cheque.text = ''
        self.depot_sortie.text = ''
        self.lieu_paiement.text = ''
        self.date_commande.text = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        self.cheque_row.opacity = 0
        self.cheque_row.height = 0
        self.cheque_row.size_hint_y = None

        self.rendu_row.height = 0
        self.rendu_row.size_hint_y = None
        self.rendu_row.opacity = 0

        if self.client_details:
            self.client_details.text = ""

    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        _bg(content, BG_DARK)
        content.add_widget(Label(text=message, color=TEXT_WHITE))
        btn = Button(text="OK", size_hint=(1, None), height=35,
                     background_normal="", background_color=ACCENT)
        popup = Popup(title=title, content=content, size_hint=(0.78, 0.32))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def on_mode_paiement_change(self, spinner, text):
        if text == "Chèque":
            self.cheque_row.opacity = 1
            self.cheque_row.height = 40
            self.cheque_row.size_hint_y = None
            self.numero_cheque.disabled = False
            # Cacher le rendu (pas de rendu pour chèque)
            self.rendu_row.height = 0
            self.rendu_row.size_hint_y = None
            self.rendu_row.opacity = 0
        elif text == "Mvola":
            self.cheque_row.opacity = 0
            self.cheque_row.height = 0
            self.cheque_row.size_hint_y = None
            self.numero_cheque.disabled = True
            self.numero_cheque.text = ""
            # Cacher le rendu (pas de rendu pour Mvola)
            self.rendu_row.height = 0
            self.rendu_row.size_hint_y = None
            self.rendu_row.opacity = 0
        else:  # Espèce
            self.cheque_row.opacity = 0
            self.cheque_row.height = 0
            self.cheque_row.size_hint_y = None
            self.numero_cheque.disabled = True
            self.numero_cheque.text = ""
            # Le rendu sera géré par calculer_reste_et_rendu
            self.calculer_reste_et_rendu()
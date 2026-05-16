# pdf_generator.py

import os
import datetime

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    print("Warning: fpdf2 not available")


class FacturePDF(FPDF):

    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(13, 71, 161)
        self.cell(0, 6, "E & N ENTREPRISE", ln=True)

        self.set_font("Helvetica", "", 8)
        self.set_text_color(0, 0, 0)

        self.cell(0, 4, "Materiaux de Construction", ln=True)
        self.cell(0, 4, "Vente en gros et detail", ln=True)
        self.cell(0, 4, "Contact : 034 41 463 65", ln=True)

        self.ln(3)

    def footer(self):
        self.set_y(-10)
        self.set_font("Helvetica", "", 7)
        self.cell(0, 5, "-" * 37, align="C")


def generer_pdf_facture(
        commande_id,
        client_nom,
        client_info,
        produits,
        total,
        avance,
        reste,
        mode_paiement,
        numero_cheque,
        date_str):

    if not FPDF_AVAILABLE:
        return None

    try:

        factures_dir = "factures"

        if not os.path.exists(factures_dir):
            os.makedirs(factures_dir)

        nom_fichier = (
            f"facture_{commande_id}_"
            f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        filename = os.path.join(factures_dir, nom_fichier)

        chemin_absolu = os.path.abspath(filename)

        pdf = FacturePDF(
            orientation="P",
            unit="mm",
            format=(297, 80)
        )

        pdf.set_auto_page_break(auto=True, margin=8)

        pdf.add_page()

        # =========================
        # FACTURE + DATE
        # =========================

        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(13, 71, 161)

        pdf.cell(0, 6, f"FACTURE N° {commande_id}", ln=True, align="R")

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(0, 0, 0)

        pdf.cell(0, 5, f"Date : {date_str}", ln=True, align="R")

        pdf.ln(2)

        # =========================
        # CLIENT
        # =========================

        pdf.set_fill_color(238, 242, 255)

        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(0, 6, f"Client : {client_nom}", ln=True, fill=True)

        pdf.set_font("Helvetica", "", 8)

        adresse = client_info.get("adresse", "")
        contact = client_info.get("contact", "")
        nif = client_info.get("nif", "")
        stat = client_info.get("stat", "")

        if adresse:
            pdf.cell(0, 5, f"Adresse : {adresse}", ln=True)

        if contact:
            pdf.cell(0, 5, f"Contact : {contact}", ln=True)

        if nif or stat:
            pdf.cell(0, 5, f"NIF : {nif} | STAT : {stat}", ln=True)

        pdf.ln(3)

        # =========================
        # TABLEAU PRODUITS
        # =========================

        pdf.set_font("Helvetica", "B", 8)

        pdf.set_fill_color(13, 71, 161)
        pdf.set_text_color(255, 255, 255)

        pdf.cell(30, 7, "Designation", border=1, fill=True)
        pdf.cell(10, 7, "Qte", border=1, align="C", fill=True)
        pdf.cell(15, 7, "Prix", border=1, align="R", fill=True)
        pdf.cell(20, 7, "Montant", border=1, align="R", fill=True)

        pdf.ln()

        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(0, 0, 0)

        for p in produits:

            nom = str(p.get("nom", ""))

            if len(nom) > 22:
                nom = nom[:20] + "..."

            quantite = str(p.get("quantite", ""))

            prix = f"{float(p.get('prix_unitaire', 0)):,.0f}"

            montant = f"{float(p.get('total', 0)):,.0f}"

            pdf.cell(30, 6, nom, border=1)

            pdf.cell(10, 6, quantite, border=1, align="C")

            pdf.cell(15, 6, prix, border=1, align="R")

            pdf.cell(20, 6, montant, border=1, align="R")

            pdf.ln()

        pdf.ln(3)

        # =========================
        # TOTAUX
        # =========================

        pdf.set_font("Helvetica", "B", 9)

        pdf.cell(0, 6, f"TOTAL : {total:,.0f} Ar", ln=True, align="R")

        pdf.cell(
            0,
            6,
            f"MONTANT VERSE : {avance:,.0f} Ar",
            ln=True,
            align="R"
        )

        if mode_paiement == "Chèque" and numero_cheque:

            texte_paiement = (
                f"MODE DE PAIEMENT : "
                f"{mode_paiement} - N° {numero_cheque}"
            )

        else:
            texte_paiement = f"MODE DE PAIEMENT : {mode_paiement}"

        pdf.cell(0, 6, texte_paiement, ln=True, align="R")

        if reste > 0:
            pdf.set_text_color(183, 28, 28)
        else:
            pdf.set_text_color(27, 94, 32)

        pdf.cell(
            0,
            6,
            f"RESTE A PAYER : {reste:,.0f} Ar",
            ln=True,
            align="R"
        )

        pdf.set_text_color(0, 0, 0)

        pdf.ln(10)

        # =========================
        # SIGNATURE
        # =========================

        pdf.set_font("Helvetica", "", 8)

        pdf.cell(0, 6, "Cachet / Signature", align="R")

        # =========================
        # SAUVEGARDE
        # =========================

        pdf.output(chemin_absolu)

        return chemin_absolu

    except Exception as e:
        print(f"Erreur PDF : {e}")
        return None

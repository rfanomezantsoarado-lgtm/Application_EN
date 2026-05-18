# pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime
import sqlite3

# Enregistrer une police qui supporte l'unicode (pour les caractères accentués)
try:
    # Pour Windows
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
except:
    try:
        # Pour Linux
        pdfmetrics.registerFont(TTFont('Arial', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    except:
        # Fallback - utilisation de la police par défaut
        pass

def generer_pdf_facture(commande_id, client_nom, client_info, produits, total, avance, reste, mode_paiement, numero_cheque="", date_str=""):
    """
    Génère une facture PDF au format NB80
    NB80 = 80mm de largeur (environ 226 points dans ReportLab)
    """
    try:
        # Format NB80 (80mm de large, hauteur variable)
        NB80_WIDTH = 80 * mm  # 80 millimètres = environ 226.77 points
        NB80_HEIGHT = 297 * mm  # Hauteur A4 en portrait, mais on va ajuster dynamiquement
        
        # Créer le dossier factures s'il n'existe pas
        if not os.path.exists("factures"):
            os.makedirs("factures")
        
        # Nom du fichier
        filename = f"factures/facture_{commande_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Créer le canvas
        c = canvas.Canvas(filename, pagesize=(NB80_WIDTH, NB80_HEIGHT))
        
        # Marge de 10% sur les côtés (10% de 80mm = 8mm)
        margin = 8 * mm  # 8mm de marge
        width = NB80_WIDTH - (2 * margin)  # Largeur utile
        
        # Position de départ Y (en haut de la page, avec marge supérieure)
        y = NB80_HEIGHT - margin
        
        # Définir la police par défaut
        try:
            c.setFont('Arial', 9)
        except:
            c.setFont('Helvetica', 9)
        
        # ==================== EN-TÊTE ====================
        # Informations de l'entreprise (à gauche, marge 10%)
        c.setFont('Arial-Bold', 11)
        c.drawString(margin, y - 10, "VOTRE ENTREPRISE")
        c.setFont('Arial', 8)
        c.drawString(margin, y - 20, "Adresse: 123 Rue Principale")
        c.drawString(margin, y - 28, "Ville: Antananarivo 101")
        c.drawString(margin, y - 36, "Tél: +261 34 00 000 00")
        c.drawString(margin, y - 44, "Email: contact@entreprise.mg")
        c.drawString(margin, y - 52, "NIF: 0001234567")
        c.drawString(margin, y - 60, "STAT: 0001234567")
        
        # Informations du client (à droite, avec marge)
        client_x = NB80_WIDTH - margin - (width / 2)  # Moitié droite
        
        c.setFont('Arial-Bold', 9)
        c.drawString(client_x, y - 10, "FACTURE AU CLIENT")
        c.setFont('Arial', 8)
        
        # Afficher les infos client
        y_offset = 20
        c.drawString(client_x, y - y_offset, f"Client: {client_nom}")
        y_offset += 8
        
        if client_info.get('adresse'):
            c.drawString(client_x, y - y_offset, f"Adresse: {client_info['adresse']}")
            y_offset += 8
        
        if client_info.get('nif'):
            c.drawString(client_x, y - y_offset, f"NIF: {client_info['nif']}")
            y_offset += 8
        
        if client_info.get('stat'):
            c.drawString(client_x, y - y_offset, f"STAT: {client_info['stat']}")
            y_offset += 8
        
        if client_info.get('contact'):
            c.drawString(client_x, y - y_offset, f"Contact: {client_info['contact']}")
        
        # ==================== INFOS FACTURE ====================
        y -= 70
        
        # Ligne de séparation
        c.line(margin, y, NB80_WIDTH - margin, y)
        y -= 10
        
        # Numéro de facture et date
        c.setFont('Arial-Bold', 9)
        c.drawString(margin, y, f"FACTURE N°: {commande_id}")
        c.setFont('Arial', 8)
        c.drawRightString(NB80_WIDTH - margin, y, f"Date: {date_str if date_str else datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        y -= 15
        
        # Date de livraison (par défaut aujourd'hui + 3 jours)
        livraison_date = (datetime.now().date())
        c.drawString(margin, y, f"Date de livraison: {livraison_date.strftime('%d/%m/%Y')}")
        
        y -= 20
        
        # Ligne de séparation
        c.line(margin, y, NB80_WIDTH - margin, y)
        y -= 10
        
        # ==================== TABLEAU DES PRODUITS ====================
        # En-têtes du tableau
        c.setFont('Arial-Bold', 8)
        col_widths = [width * 0.35, width * 0.2, width * 0.2, width * 0.25]  # Désignation, PU, Qté, Montant
        
        x_positions = [margin]
        for i in range(3):
            x_positions.append(x_positions[-1] + col_widths[i])
        
        # Dessiner les en-têtes
        headers = ["Désignation", "P.U.", "Qté", "Montant"]
        for i, header in enumerate(headers):
            c.drawString(x_positions[i] + 2, y - 5, header)
        
        y -= 15
        c.line(margin, y, NB80_WIDTH - margin, y)
        y -= 5
        
        # Corps du tableau
        c.setFont('Arial', 7)
        line_height = 12
        
        for produit in produits:
            # Vérifier si on a besoin d'une nouvelle page
            if y < 50:
                c.showPage()
                c.setPageSize((NB80_WIDTH, NB80_HEIGHT))
                y = NB80_HEIGHT - margin
                # Réinitialiser le contexte
                try:
                    c.setFont('Arial', 7)
                except:
                    c.setFont('Helvetica', 7)
            
            # Désignation (avec gestion du texte long)
            designation = produit['nom'][:25]
            c.drawString(x_positions[0] + 2, y - line_height, designation)
            
            # Prix unitaire
            prix_unitaire = f"{produit['prix_unitaire']:,.0f}"
            c.drawRightString(x_positions[1] + col_widths[1] - 2, y - line_height, prix_unitaire)
            
            # Quantité
            c.drawRightString(x_positions[2] + col_widths[2] - 2, y - line_height, str(produit['quantite']))
            
            # Montant
            montant = f"{produit['total']:,.0f}"
            c.drawRightString(x_positions[3] + col_widths[3] - 2, y - line_height, montant)
            
            y -= line_height
        
        y -= 5
        c.line(margin, y, NB80_WIDTH - margin, y)
        y -= 10
        
        # ==================== TOTAUX ====================
        # Aligner à droite
        total_label_x = NB80_WIDTH - margin - 60
        
        c.setFont('Arial-Bold', 9)
        c.drawString(total_label_x, y, "TOTAL:")
        c.setFont('Arial', 9)
        c.drawRightString(NB80_WIDTH - margin, y, f"{total:,.0f} Ar")
        
        y -= 15
        
        c.setFont('Arial-Bold', 8)
        c.drawString(total_label_x, y, "Avance:")
        c.setFont('Arial', 8)
        c.drawRightString(NB80_WIDTH - margin, y, f"{avance:,.0f} Ar")
        
        y -= 12
        
        c.setFont('Arial-Bold', 8)
        c.drawString(total_label_x, y, "RESTE À PAYER:")
        c.setFont('Arial-Bold', 9)
        c.setFillColorRGB(0.82, 0.08, 0.08)  # Rouge
        c.drawRightString(NB80_WIDTH - margin, y, f"{reste:,.0f} Ar")
        c.setFillColorRGB(0, 0, 0)  # Retour au noir
        
        y -= 15
        
        # Mode de paiement
        c.setFont('Arial', 8)
        c.drawString(margin, y, f"Mode de paiement: {mode_paiement}")
        if mode_paiement == "Chèque" and numero_cheque:
            y -= 10
            c.drawString(margin, y, f"N° Chèque: {numero_cheque}")
        
        y -= 20
        
        # Ligne de séparation
        c.line(margin, y, NB80_WIDTH - margin, y)
        y -= 15
        
        # ==================== ESPACE SIGNATURE ====================
        c.setFont('Arial', 7)
        c.drawString(margin, y, "Signature du client:")
        
        # Ligne pour signature
        ligne_signature_y = y - 5
        c.line(margin + 40, ligne_signature_y, NB80_WIDTH - margin, ligne_signature_y)
        
        y -= 30
        
        # ==================== PIED DE PAGE ====================
        c.setFont('Arial', 6)
        c.setFillColorRGB(0.5, 0.5, 0.5)  # Gris
        c.drawString(margin, y, "Merci de votre confiance")
        c.drawCentredString(NB80_WIDTH / 2, y, "www.votreentreprise.mg")
        c.drawRightString(NB80_WIDTH - margin, y, f"Édité le {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # ==================== SAUVEGARDE ====================
        c.save()
        
        return filename
        
    except Exception as e:
        print(f"Erreur lors de la génération du PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

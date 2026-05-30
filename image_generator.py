# image_generator.py - Version finale avec séparation visuelle claire (bas de page uniquement)
from PIL import Image, ImageDraw, ImageFont
import os
import sys
from datetime import datetime

# Configuration des polices multiplateforme
def get_font(size_pt, bold=False):
    """Charge une police de manière robuste sur PC et Android"""
    size_px = int(size_pt * 96 / 72)

    font_names = []
    if bold:
        font_names = [
            "arialbd.ttf", "Arial-Bold.ttf", "DroidSans-Bold.ttf",
            "NotoSans-Bold.ttf", "Roboto-Bold.ttf", "DejaVuSans-Bold.ttf",
        ]
    else:
        font_names = [
            "arial.ttf", "Arial.ttf", "DroidSans.ttf",
            "NotoSans.ttf", "Roboto-Regular.ttf", "DejaVuSans.ttf",
        ]

    for font_name in font_names:
        try:
            if os.path.exists(font_name):
                return ImageFont.truetype(font_name, size_px)
            system_fonts = [
                "/system/fonts/", "/usr/share/fonts/",
                "C:/Windows/Fonts/", "/Library/Fonts/",
            ]
            for sys_dir in system_fonts:
                full_path = os.path.join(sys_dir, font_name)
                if os.path.exists(full_path):
                    return ImageFont.truetype(full_path, size_px)
        except:
            continue

    return ImageFont.load_default()

# Constantes pour 300 DPI
DPI = 300
MM_TO_PX = DPI / 25.4

# TAILLES DE POLICE
TAILLE_TEXTE_NORMAL = 26    # 26pt
TAILLE_TEXTE_GRAND = 30     # 30pt
TAILLE_TEXTE_PETIT = 22     # 22pt
TAILLE_SIGNATURE = 24       # 24pt pour la signature

# Espacement entre libellé et valeur pour le bas de page uniquement
ESPACE_LIBELLE_VALEUR_BAS = 8   # 8px d'espace pour séparation claire

def mm_to_px(mm):
    """Convertit les millimètres en pixels à 300 DPI"""
    return int(mm * MM_TO_PX)

def generer_en_tete(draw, img, width, padding, y):
    """Génère l'en-tête avec logo et texte"""

    MARGE_LOGO_GAUCHE_MM = 10

    logo = None
    logo_width = 0
    logo_y_position = y  # Position Y du logo
    try:
        logo_path = "images/logo.png"
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            logo_size = mm_to_px(35)
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            if logo.mode != 'RGB':
                logo = logo.convert('RGB')

            marge_gauche_logo = mm_to_px(MARGE_LOGO_GAUCHE_MM)
            logo_x = padding + marge_gauche_logo
            img.paste(logo, (logo_x, y))
            logo_width = logo.width + marge_gauche_logo + 5
    except Exception as e:
        print(f"Erreur chargement logo: {e}")
        logo_width = 0

    # Sous-titre
    font_soustitre = get_font(TAILLE_TEXTE_NORMAL, bold=True)

    if logo and logo_width > 0:
        logo_actual_width = logo.width
        marge_gauche_logo = mm_to_px(10)
        logo_center_x = padding + marge_gauche_logo + (logo_actual_width // 2)
        bbox_soustitre = draw.textbbox((0, 0), "Vente en gros et détail", font=font_soustitre)
        soustitre_width = bbox_soustitre[2] - bbox_soustitre[0]
        soustitre_x = logo_center_x - (soustitre_width // 2)
        draw.text((soustitre_x-mm_to_px(4), y + logo.height + mm_to_px(2)), "Matériaux de construction \n \n  Vente en gros et détail", font=font_soustitre, fill='#000000')

    # Contact
    logo_bottom = y + (logo.height if logo else mm_to_px(20))
    font_contact = get_font(TAILLE_TEXTE_NORMAL, bold=True)

    contact_text = "Contact : 034 41 463 65"
    bbox_contact = draw.textbbox((0, 0), contact_text, font=font_contact)
    contact_width = bbox_contact[2] - bbox_contact[0]

    if logo and logo_width > 0:
        marge_gauche_logo = mm_to_px(10)
        logo_actual_width = logo.width
        logo_center_x = padding + marge_gauche_logo + (logo_actual_width // 2)
    else:
        logo_center_x = padding + mm_to_px(10)

    contact_x = logo_center_x - (contact_width // 2)
    contact_y = logo_bottom + mm_to_px(15)

    draw.text((contact_x, contact_y), contact_text, font=font_contact, fill='#000000')

    return logo_width, y  # Retourne la position Y du logo (son haut)

def dessiner_rectangle_arrondi(draw, xy, rayon, fill=None, outline='#000000', width=3):
    """Dessine un rectangle avec des coins arrondis"""
    x1, y1, x2, y2 = xy
    rayon_px = mm_to_px(4)

    draw.arc([x1, y1, x1 + 2*rayon_px, y1 + 2*rayon_px], 180, 270, fill=outline, width=width)
    draw.arc([x2 - 2*rayon_px, y1, x2, y1 + 2*rayon_px], 270, 360, fill=outline, width=width)
    draw.arc([x1, y2 - 2*rayon_px, x1 + 2*rayon_px, y2], 90, 180, fill=outline, width=width)
    draw.arc([x2 - 2*rayon_px, y2 - 2*rayon_px, x2, y2], 0, 90, fill=outline, width=width)

    draw.line([(x1 + rayon_px, y1), (x2 - rayon_px, y1)], fill=outline, width=width)
    draw.line([(x1 + rayon_px, y2), (x2 - rayon_px, y2)], fill=outline, width=width)
    draw.line([(x1, y1 + rayon_px), (x1, y2 - rayon_px)], fill=outline, width=width)
    draw.line([(x2, y1 + rayon_px), (x2, y2 - rayon_px)], fill=outline, width=width)

def generer_infos_client_rectangle(draw, width, client_nom, client_info, y_position_logo_top):
    """Génère un rectangle avec les informations client - aligné avec le haut du logo"""

    # Position horizontale à 6cm (60mm) du bord gauche
    position_horizontale_mm = 60
    rect_x = mm_to_px(position_horizontale_mm)

    # Dimensions du rectangle
    rect_width = mm_to_px(55)   # Largeur
    rect_height = mm_to_px(35)  # Hauteur réduite (enlevé stat)

    # Position verticale identique à la position HAUT du logo
    rect_y = y_position_logo_top

    # Dessiner le rectangle
    dessiner_rectangle_arrondi(draw,
                              [rect_x, rect_y, rect_x + rect_width, rect_y + rect_height],
                              rayon=mm_to_px(4),
                              outline='#000000',
                              width=3)

    # Polices
    font_label = get_font(TAILLE_TEXTE_NORMAL, bold=True)
    font_value = get_font(TAILLE_TEXTE_NORMAL, bold=False)

    margin = mm_to_px(4)
    inner_x = rect_x + margin
    y = rect_y + margin
    line_height = mm_to_px(7)  # Interligne réduit

    # Client - pas d'espacement supplémentaire
    label_text = "Client :"
    value_text = client_nom
    bbox_label = draw.textbbox((0, 0), label_text, font=font_label)
    label_width = bbox_label[2] - bbox_label[0]
    draw.text((inner_x, y), label_text, font=font_label, fill='#000000')
    draw.text((inner_x + label_width, y), value_text, font=font_value, fill='#000000')
    y += line_height

    # Adresse - pas d'espacement supplémentaire
    adresse = client_info.get('adresse', '')
    label_text = "Adresse :"
    value_text = adresse
    bbox_label = draw.textbbox((0, 0), label_text, font=font_label)
    label_width = bbox_label[2] - bbox_label[0]
    draw.text((inner_x, y), label_text, font=font_label, fill='#000000')
    draw.text((inner_x + label_width, y), value_text, font=font_value, fill='#000000')
    y += line_height

    # Contact - pas d'espacement supplémentaire
    contact = client_info.get('contact', '')
    label_text = "Contact :"
    value_text = contact
    bbox_label = draw.textbbox((0, 0), label_text, font=font_label)
    label_width = bbox_label[2] - bbox_label[0]
    draw.text((inner_x, y), label_text, font=font_label, fill='#000000')
    draw.text((inner_x + label_width, y), value_text, font=font_value, fill='#000000')
    y += line_height

    # Responsable - pas d'espacement supplémentaire
    responsable = client_info.get('responsable', '')
    label_text = "Responsable :"
    value_text = responsable
    bbox_label = draw.textbbox((0, 0), label_text, font=font_label)
    label_width = bbox_label[2] - bbox_label[0]
    draw.text((inner_x, y), label_text, font=font_label, fill='#000000')
    draw.text((inner_x + label_width, y), value_text, font=font_value, fill='#000000')

    return rect_y + rect_height

def generer_date(draw, width, y_rectangle_bottom, date_str):
    """Génère la date en dessous du rectangle client"""

    font_date = get_font(TAILLE_TEXTE_NORMAL, bold=True)

    # Aligner la date sous le rectangle client (à 6cm)
    position_horizontale_mm = 60
    rect_width = mm_to_px(55)
    rect_x = mm_to_px(position_horizontale_mm)

    bbox = draw.textbbox((0, 0), f"Date : {date_str}", font=font_date)
    text_width = bbox[2] - bbox[0]

    date_x = rect_x + (rect_width - text_width) // 2
    date_y = y_rectangle_bottom + mm_to_px(5)  # Réduit de 8 à 5

    draw.text((date_x, date_y), f"Date : {date_str}", font=font_date, fill='#000000')

    return date_y + mm_to_px(8)  # Réduit de 15 à 8

def generer_depot_sortie(draw, width, y_date_bottom, depot_sortie):
    """Génère le dépôt de sortie en dessous de la date"""

    font_depot = get_font(TAILLE_TEXTE_NORMAL, bold=True)
    font_value = get_font(TAILLE_TEXTE_NORMAL, bold=False)

    # Position horizontale à 6cm (60mm) du bord gauche
    position_horizontale_mm = 60
    rect_width = mm_to_px(55)
    rect_x = mm_to_px(position_horizontale_mm)

    label_text = "Dépôt de sortie :"
    value_text = depot_sortie if depot_sortie else "Non spécifié"

    bbox_label = draw.textbbox((0, 0), label_text, font=font_depot)
    label_width = bbox_label[2] - bbox_label[0]

    depot_x = rect_x
    depot_y = y_date_bottom  # Pas d'espace supplémentaire

    draw.text((depot_x, depot_y), label_text, font=font_depot, fill='#000000')
    draw.text((depot_x + label_width + mm_to_px(5), depot_y), value_text, font=font_value, fill='#333333')

    return depot_y + mm_to_px(8)  # Réduit de 15 à 8

def generer_tableau_bon_livraison(draw, width, y_start, produits, num_facture):
    """Génère le tableau BON DE LIVRAISON"""

    y = y_start
    marge_gauche_droite = mm_to_px(10)

    largeur_disponible = width - (marge_gauche_droite * 2)

    col_widths = {
        'designation': int(largeur_disponible * 0.35),
        'quantite': int(largeur_disponible * 0.15),
        'prix_unitaire': int(largeur_disponible * 0.20),
        'montant': int(largeur_disponible * 0.30)
    }

    somme_widths = sum(col_widths.values())
    difference = largeur_disponible - somme_widths
    if difference != 0:
        col_widths['designation'] += difference

    table_width = sum(col_widths.values())
    table_x = marge_gauche_droite

    header_height = mm_to_px(18)
    row_height = mm_to_px(16)

    font_header = get_font(TAILLE_TEXTE_GRAND, bold=True)
    font_normal = get_font(TAILLE_TEXTE_NORMAL, bold=True)

    # Titre centré - PLUS D'ESPACE AVANT (y_start directement)
    titre_y = y
    bbox_titre = draw.textbbox((0, 0), f"BON DE LIVRAISON N° {num_facture}", font=font_header)
    titre_width = bbox_titre[2] - bbox_titre[0]
    titre_x = table_x + (table_width - titre_width) // 2

    draw.text((titre_x, titre_y), f"BON DE LIVRAISON N° {num_facture}", font=font_header, fill='#000000')
    y += mm_to_px(6)  # Réduit de 8 à 6

    # En-tête du tableau
    header_y = y
    draw.rectangle([(table_x, header_y), (table_x + table_width, header_y + header_height)],
                   outline='#000000', fill=None, width=3)

    x_pos = table_x
    for i, (col_name, col_width) in enumerate(col_widths.items()):
        if i < len(col_widths) - 1:
            x_pos += col_width
            draw.line([(x_pos, header_y), (x_pos, header_y + header_height)], fill='#000000', width=2)

    x_offset = table_x

    # Désignation
    bbox_design = draw.textbbox((0, 0), "Désignation", font=font_header)
    design_height = bbox_design[3] - bbox_design[1]
    text_y = header_y + (header_height - design_height) // 2
    draw.text((x_offset + mm_to_px(5), text_y), "Désignation", font=font_header, fill='#000000')
    x_offset += col_widths['designation']

    # Qté
    bbox_qte = draw.textbbox((0, 0), "Qté", font=font_header)
    qte_height = bbox_qte[3] - bbox_qte[1]
    qte_width = bbox_qte[2] - bbox_qte[0]
    text_y = header_y + (header_height - qte_height) // 2
    text_x = x_offset + (col_widths['quantite'] - qte_width) // 2
    draw.text((text_x, text_y), "Qté", font=font_header, fill='#000000')
    x_offset += col_widths['quantite']

    # Prix U
    bbox_prix = draw.textbbox((0, 0), "Prix U", font=font_header)
    prix_height = bbox_prix[3] - bbox_prix[1]
    prix_width = bbox_prix[2] - bbox_prix[0]
    text_y = header_y + (header_height - prix_height) // 2
    text_x = x_offset + (col_widths['prix_unitaire'] - prix_width) // 2
    draw.text((text_x, text_y), "Prix U", font=font_header, fill='#000000')
    x_offset += col_widths['prix_unitaire']

    # Montant (Ar)
    bbox_montant = draw.textbbox((0, 0), "Montant (Ar)", font=font_header)
    montant_height = bbox_montant[3] - bbox_montant[1]
    montant_width = bbox_montant[2] - bbox_montant[0]
    text_y = header_y + (header_height - montant_height) // 2
    text_x = x_offset + (col_widths['montant'] - montant_width) // 2
    draw.text((text_x, text_y), "Montant (Ar)", font=font_header, fill='#000000')

    y += header_height

    # Lignes des produits
    row_count = max(len(produits), 5)

    for i in range(row_count):
        row_y = y + (i * row_height)
        row_fill = '#ffffff' if i % 2 == 0 else '#ffffff'

        draw.rectangle([(table_x, row_y), (table_x + table_width, row_y + row_height)],
                       fill=row_fill, outline='#000000', width=2)

        x_pos = table_x
        for j, (col_name, col_width) in enumerate(col_widths.items()):
            if j < len(col_widths) - 1:
                x_pos += col_width
                draw.line([(x_pos, row_y), (x_pos, row_y + row_height)], fill='#000000', width=2)

        if i < len(produits):
            p = produits[i]
            x_offset = table_x

            # Désignation
            designation = p['nom']
            bbox_design = draw.textbbox((0, 0), designation, font=font_normal)
            design_height = bbox_design[3] - bbox_design[1]
            text_y = row_y + (row_height - design_height) // 2
            draw.text((x_offset + mm_to_px(5), text_y), designation, font=font_normal, fill='#000000')
            x_offset += col_widths['designation']

            # Quantité
            qte_str = str(p['quantite'])
            bbox_qte = draw.textbbox((0, 0), qte_str, font=font_normal)
            qte_height = bbox_qte[3] - bbox_qte[1]
            qte_width = bbox_qte[2] - bbox_qte[0]
            text_y = row_y + (row_height - qte_height) // 2
            text_x = x_offset + (col_widths['quantite'] - qte_width) // 2
            draw.text((text_x, text_y), qte_str, font=font_normal, fill='#000000')
            x_offset += col_widths['quantite']

            # Prix Unitaire
            prix_str = f"{p['prix_unitaire']:,.0f}"
            bbox_prix = draw.textbbox((0, 0), prix_str, font=font_normal)
            prix_height = bbox_prix[3] - bbox_prix[1]
            prix_width = bbox_prix[2] - bbox_prix[0]
            text_y = row_y + (row_height - prix_height) // 2
            text_x = x_offset + col_widths['prix_unitaire'] - prix_width - mm_to_px(5)
            draw.text((text_x, text_y), prix_str, font=font_normal, fill='#000000')
            x_offset += col_widths['prix_unitaire']

            # Montant
            montant_str = f"{p['total']:,.0f}"
            bbox_montant = draw.textbbox((0, 0), montant_str, font=font_normal)
            montant_height = bbox_montant[3] - bbox_montant[1]
            montant_width = bbox_montant[2] - bbox_montant[0]
            text_y = row_y + (row_height - montant_height) // 2
            text_x = x_offset + col_widths['montant'] - montant_width - mm_to_px(5)
            draw.text((text_x, text_y), montant_str, font=font_normal, fill='#000000')

    bottom_y = y + (row_count * row_height)
    draw.line([(table_x, bottom_y), (table_x + table_width, bottom_y)], fill='#000000', width=3)
    draw.line([(table_x, header_y), (table_x, bottom_y)], fill='#000000', width=3)
    draw.line([(table_x + table_width, header_y), (table_x + table_width, bottom_y)], fill='#000000', width=3)

    return bottom_y + mm_to_px(5)

def generer_bas_facture(draw, width, y_start, total, avance, reste,
                        mode_paiement, lieu_paiement, numero_cheque="", rendu=0):
    """Génère le bas de facture avec montants alignés à droite, lieu de paiement et rendu"""

    y = y_start
    marge_gauche_droite = mm_to_px(10)

    font_normal = get_font(TAILLE_TEXTE_NORMAL, bold=True)
    font_bold = get_font(TAILLE_TEXTE_GRAND, bold=True)
    font_small = get_font(TAILLE_TEXTE_PETIT, bold=False)

    line_height = mm_to_px(10)  # Interligne réduit

    # MONTANTS alignés à droite avec ESPACE FIXE
    marge_droite_px = mm_to_px(10)
    right_x = width - marge_droite_px

    # Largeur FIXE pour tous les libellés (pour alignement parfait)
    LABEL_WIDTH = mm_to_px(35)  # Tous les libellés ont la même largeur

    # Montant Total (à droite)
    label_text = "Montant Total :"
    value_text = f"{total:,.0f} Ar" if total else "0 Ar"
    draw.text((right_x - LABEL_WIDTH, y), label_text, font=font_bold, fill='#000000', anchor='rt')
    draw.text((right_x, y), value_text, font=font_bold, fill='#DC3545', anchor='rt')

     # Mode de paiement (à gauche avec valeur en dessous)
    label_text = "Mode de paiement :"
    value_text = mode_paiement if mode_paiement else "Non spécifié"
    draw.text((mm_to_px(10), y), label_text, font=font_bold, fill='#000000')
    # Valeur en dessous du libellé
    draw.text((mm_to_px(10)+15, y + mm_to_px(5)), value_text, font=font_normal, fill='#4169E1')
    y += line_height

    # Montant payé (à droite)
    label_text = "Montant payé :"
    value_text = f"{avance:,.0f} Ar" if avance else "0 Ar"
    draw.text((right_x - LABEL_WIDTH, y), label_text, font=font_bold, fill='#000000', anchor='rt')
    draw.text((right_x, y), value_text, font=font_bold, fill='#26874E', anchor='rt')

     # Lieu de paiement (à gauche avec valeur en dessous)
    label_text = "Lieu de paiement :"
    value_text = lieu_paiement if lieu_paiement else "Non spécifié"
    draw.text((mm_to_px(10), y), label_text, font=font_bold, fill='#000000')
    # Valeur en dessous du libellé
    draw.text((mm_to_px(10)+15, y + mm_to_px(5)), value_text, font=font_normal, fill='#808000')
    y += line_height

    # RENDU (si > 0) - AFFICHÉ À DROITE COMME LES AUTRES MONTANTS
    if rendu > 0:
        label_text = "RENDU :"
        value_text = f"{rendu:,.0f} Ar"
        draw.text((right_x - LABEL_WIDTH, y), label_text, font=font_bold, fill='#000000', anchor='rt')
        draw.text((right_x, y), value_text, font=font_bold, fill='#000000', anchor='rt')
        y += line_height

    # Reste à payer (à droite)
    reste_color = '#000000' if (reste and reste > 0) else '#000000'
    label_text = "Reste à payer :"
    value_text = f"{reste:,.0f} Ar" if reste else "0 Ar"
    draw.text((right_x - LABEL_WIDTH, y), label_text, font=font_bold, fill='#000000', anchor='rt')
    draw.text((right_x, y), value_text, font=font_bold, fill='#DE3163', anchor='rt')
    y += line_height


    # Numéro de chèque (si mode chèque)
    if numero_cheque:
        label_text = "N° Chèque :"
        value_text = numero_cheque
        draw.text((mm_to_px(10), y), label_text, font=font_normal, fill='#333333')
        draw.text((mm_to_px(10) + mm_to_px(35), y), value_text, font=font_small, fill='#333333')
        y += line_height

    # Position Y après les montants
    y_final = y

    # ===== CACHET / SIGNATURE =====
    # Position à droite avec marge de 2cm (20mm) du bord droit en bas de reste à payer
    marge_sig_droite_mm = 15
    sig_width = mm_to_px(40)
    sig_x = width - mm_to_px(marge_sig_droite_mm) - sig_width
    y_sig = y_final

    # Texte "Cachet / Signature"
    font_sig = get_font(TAILLE_SIGNATURE, bold=True)
    draw.text((sig_x + sig_width // 2, y_sig), "Cachet / Signature",
              font=font_sig, fill='#000000', anchor='mt')

    # Texte "Merci de votre confiance !" centré en bas
    font_merci = get_font(TAILLE_TEXTE_GRAND, bold=True)
    draw.text((width // 2, y_sig + mm_to_px(20)), "Merci de votre confiance !",
              font=font_merci, fill='#000000', anchor='mt')

    return y_sig + mm_to_px(35)

def generer_facture_proforma(client_nom, client_info, produits,
                            date_str, mode_paiement, depot_sortie,
                            total, avance, reste, commande_id,
                            numero_cheque="", lieu_paiement="", rendu=0):
    """Génère la facture proforma complète (300 DPI)"""

    annee = datetime.now().strftime("%Y")
    mois = datetime.now().strftime("%m")
    if not os.path.exists("factures"):
        os.makedirs("factures")
    filename = f"factures/facture n°_{commande_id} du {mois} {annee}.jpg"

    width = mm_to_px(120)
    height = mm_to_px(310)
    padding = mm_to_px(5)

    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # Marge haute de 70px
    y_position = mm_to_px(20) + 130

    # En-tête avec logo et récupération de la position HAUT du logo
    logo_width, logo_top_y = generer_en_tete(draw, img, width, padding, y_position)

    # Rectangle client avec la position HAUT du logo comme référence
    client_y = generer_infos_client_rectangle(draw, width, client_nom, client_info, logo_top_y)

    # Date (sous le rectangle client)
    date_y = generer_date(draw, width, client_y, date_str)

    # Dépôt de sortie (en dessous de la date) - espace réduit
    depot_y = generer_depot_sortie(draw, width, date_y, depot_sortie)

    # Tableau - espace réduit
    tableau_y = generer_tableau_bon_livraison(draw, width, depot_y, produits, commande_id)

    # Bas de page avec lieu de paiement et rendu
    generer_bas_facture(draw, width, tableau_y, total, avance, reste,
                       mode_paiement, lieu_paiement, numero_cheque, rendu)

    img.save(filename, "JPEG", quality=95, dpi=(DPI, DPI))
    print(f"Facture générée avec succès : {filename} (300 DPI)")

    return filename
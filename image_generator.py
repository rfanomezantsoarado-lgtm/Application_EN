# image_generator.py - Version corrigée avec polices 12pt
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

# Configuration des polices (ajustez les chemins selon votre système)
FONT_REGULAR = "arial.ttf"  # Chemin vers une police régulière
FONT_BOLD = "arialbd.ttf"   # Chemin vers une police gras

# Constantes pour 300 DPI
DPI = 300
MM_TO_PX = DPI / 25.4

# Facteur d'agrandissement des polices (ajustez cette valeur)
FACTEUR_POLICE = 1.5  # 1.5 = 50% plus grand, 2 = 2x plus grand

# CONVERSION 12pt = 4.233mm
PT_12_EN_MM = 4.233

def mm_to_pt(mm):
    """Convertit les mm en points avec facteur d'agrandissement"""
    conversion_standard = mm * 2.83465
    return int(conversion_standard * FACTEUR_POLICE)

def mm_to_px(mm):
    """Convertit les millimètres en pixels à 300 DPI"""
    return int(mm * MM_TO_PX)

def generer_en_tete(draw, img, width, padding, y):
    """Génère l'en-tête avec logo et texte comme sur l'image"""

    # Charger le logo
    MARGE_LOGO_GAUCHE_MM = 10  # Ajustez cette valeur (5, 10, 15 mm selon besoin)

    logo = None
    logo_width = 0
    try:
        logo_path = "images/logo.png"
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            # Redimensionner le logo
            logo_size = mm_to_px(30)
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            # Convertir le logo en RGB si nécessaire
            if logo.mode != 'RGB':
                logo = logo.convert('RGB')

            # Marge à gauche configurable
            marge_gauche_logo = mm_to_px(MARGE_LOGO_GAUCHE_MM)
            logo_x = padding + marge_gauche_logo

            # Coller le logo
            img.paste(logo, (logo_x, y))
            logo_width = logo.width + marge_gauche_logo + 5
    except Exception as e:
        print(f"Erreur chargement logo: {e}")
        logo_width = 0

    # Sous-titre "Vente en gros et détail" en bas du logo - TAILLE 12pt
    try:
        font_soustitre = ImageFont.truetype(FONT_REGULAR, mm_to_pt(PT_12_EN_MM)) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_soustitre = ImageFont.load_default()

    # Position du sous-titre centré sous le logo
    if logo and logo_width > 0:
        logo_actual_width = logo.width
        marge_gauche_logo = mm_to_px(10)  # Même valeur que plus haut
        logo_center_x = padding + marge_gauche_logo + (logo_actual_width // 2)
        bbox_soustitre = draw.textbbox((0, 0), "Vente en gros et détail", font=font_soustitre)
        soustitre_width = bbox_soustitre[2] - bbox_soustitre[0]
        soustitre_x = logo_center_x - (soustitre_width // 2)
        draw.text((soustitre_x, y + logo.height + mm_to_px(1)), "Vente en gros et détail", font=font_soustitre, fill='#000000')
    
    # Contact - centré par rapport au logo - TAILLE 12pt
    logo_bottom = y + (logo.height if logo else mm_to_px(20))

    try:
        font_contact = ImageFont.truetype(FONT_REGULAR, mm_to_pt(PT_12_EN_MM)) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_contact = ImageFont.load_default()

    # Position du contact centrée horizontalement par rapport au logo
    contact_text = "Contact : 034 41 463 65"
    bbox_contact = draw.textbbox((0, 0), contact_text, font=font_contact)
    contact_width = bbox_contact[2] - bbox_contact[0]

    # Calculer le centre du logo (avec la marge)
    if logo and logo_width > 0:
        marge_gauche_logo = mm_to_px(10)  # Même valeur que pour le positionnement du logo
        logo_actual_width = logo.width
        logo_center_x = padding + marge_gauche_logo + (logo_actual_width // 2)
    else:
        logo_center_x = padding + mm_to_px(10)

    contact_x = logo_center_x - (contact_width // 2)
    contact_y = logo_bottom + mm_to_px(5)

    draw.text((contact_x, contact_y), contact_text, font=font_contact, fill='#000000')

    return logo_width

def dessiner_rectangle_arrondi(draw, xy, rayon, fill=None, outline='#000000', width=3):
    """Dessine un rectangle avec des coins arrondis (sans remplissage) avec contour épais"""
    x1, y1, x2, y2 = xy
    rayon_px = mm_to_px(3)

    # Coins arrondis (4 arcs de cercle)
    # Coin haut-gauche
    draw.arc([x1, y1, x1 + 2*rayon_px, y1 + 2*rayon_px], 180, 270, fill=outline, width=width)
    # Coin haut-droit
    draw.arc([x2 - 2*rayon_px, y1, x2, y1 + 2*rayon_px], 270, 360, fill=outline, width=width)
    # Coin bas-gauche
    draw.arc([x1, y2 - 2*rayon_px, x1 + 2*rayon_px, y2], 90, 180, fill=outline, width=width)
    # Coin bas-droit
    draw.arc([x2 - 2*rayon_px, y2 - 2*rayon_px, x2, y2], 0, 90, fill=outline, width=width)

    # Lignes droites (sans rectangle)
    # Ligne horizontale du haut
    draw.line([(x1 + rayon_px, y1), (x2 - rayon_px, y1)], fill=outline, width=width)
    # Ligne horizontale du bas
    draw.line([(x1 + rayon_px, y2), (x2 - rayon_px, y2)], fill=outline, width=width)
    # Ligne verticale gauche
    draw.line([(x1, y1 + rayon_px), (x1, y2 - rayon_px)], fill=outline, width=width)
    # Ligne verticale droite
    draw.line([(x2, y1 + rayon_px), (x2, y2 - rayon_px)], fill=outline, width=width)

def generer_infos_client_rectangle(draw, width, padding, y_start, client_nom, client_info):
    """Génère un rectangle avec les informations client aligné verticalement avec l'en-tête"""

    # Calcul des dimensions du rectangle - LARGEUR AUGMENTÉE
    rect_width = mm_to_px(60)   # Augmenté de 45 à 60 (plus large)
    rect_height = mm_to_px(28)  # Hauteur inchangée

    # Position horizontale : légèrement décalée pour compenser la largeur
    rect_x = mm_to_px(50)  # Décalé de 55 à 50 pour garder l'équilibre

    # Position verticale : utiliser le même y_start que l'en-tête
    rect_y = 110

    # Dessiner le rectangle arrondi avec contour PLUS ÉPAIS
    dessiner_rectangle_arrondi(draw,
                              [rect_x, rect_y, rect_x + rect_width, rect_y + rect_height],
                              rayon=mm_to_px(3),
                              outline='#000000',
                              width=3)

    # Polices - TOUTES EN 12pt (4.233mm)
    try:
        font_label = ImageFont.truetype(FONT_REGULAR, mm_to_pt(PT_12_EN_MM)) if FONT_REGULAR else ImageFont.load_default()
        font_value = ImageFont.truetype(FONT_REGULAR, mm_to_pt(PT_12_EN_MM)) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_label = ImageFont.load_default()
        font_value = ImageFont.load_default()

    # Position à l'intérieur du rectangle (marge réduite)
    margin = mm_to_px(3)
    inner_x = rect_x + margin
    y = rect_y + margin
    line_height = mm_to_px(6)  # Augmenté de 5 à 6mm pour 12pt

    # Largeur pour la colonne des labels - légèrement augmentée
    label_width = mm_to_px(28)

    # Client
    draw.text((inner_x, y), "Client :", font=font_label, fill='#000000')
    draw.text((inner_x + label_width, y), client_nom, font=font_value, fill='#000000')
    y += line_height

    # Stat
    stat = client_info.get('stat', '')
    draw.text((inner_x, y), "Stat :", font=font_label, fill='#000000')
    draw.text((inner_x + label_width, y), stat, font=font_value, fill='#000000')
    y += line_height

    # Adresse
    adresse = client_info.get('adresse', '')
    draw.text((inner_x, y), "Adresse :", font=font_label, fill='#000000')
    draw.text((inner_x + label_width, y), adresse, font=font_value, fill='#000000')
    y += line_height

    # Contact
    contact = client_info.get('contact', '')
    draw.text((inner_x, y), "Contact :", font=font_label, fill='#000000')
    draw.text((inner_x + label_width, y), contact, font=font_value, fill='#000000')
    y += line_height

    # Responsable - AVEC PLUS D'ESPACE
    responsable = client_info.get('responsable', '')
    draw.text((inner_x, y), "Responsable :", font=font_label, fill='#000000')
    draw.text((inner_x + mm_to_px(35), y), responsable, font=font_value, fill='#000000')

    return rect_y + rect_height

def generer_date(draw, width, padding, y_rectangle_bottom, date_str):
    """Génère la date en dessous du rectangle (à l'extérieur)"""

    # TAILLE 12pt
    try:
        font_date = ImageFont.truetype(FONT_REGULAR, mm_to_pt(PT_12_EN_MM)) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_date = ImageFont.load_default()

    # Dimensions du rectangle
    rect_width = mm_to_px(60)
    rect_x = width - padding - rect_width

    # Calculer la position centrée horizontalement par rapport au rectangle
    bbox = draw.textbbox((0, 0), f"Date : {date_str}", font=font_date)
    text_width = bbox[2] - bbox[0]

    # Centrer le texte horizontalement dans le rectangle
    date_x = rect_x + (rect_width - text_width) // 2

    # Position verticale : en dessous du rectangle (marge 3mm)
    date_y = y_rectangle_bottom + mm_to_px(3)

    draw.text((date_x, date_y), f"Date : {date_str}", font=font_date, fill='#000000')

    # Retourner la nouvelle position Y (après la date + marge)
    return date_y + mm_to_px(7)

def generer_tableau_bon_livraison(draw, width, padding, y_start, produits, num_facture, annee):
    """Génère le tableau BON DE LIVRAISON avec espace avant de 1cm"""

    # Espace 1cm = 10mm
    espace_1cm = mm_to_px(5)

    # Ajouter l'espace de 1cm avant le tableau
    y = y_start + espace_1cm

    # Marge gauche et droite de 1cm (10mm)
    marge_gauche_droite = mm_to_px(10)  # 1cm = 10mm

    # === AJUSTEMENT DES LARGEURS DES COLONNES ===
    largeur_disponible = width - (marge_gauche_droite * 2)

    # Redéfinir les largeurs des colonnes
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

    # Hauteur des lignes - AUGMENTÉE pour 12pt
    header_height = mm_to_px(12)  # 12mm
    row_height = mm_to_px(12)     # 12mm

    # Charger les polices - TOUTES EN 12pt
    try:
        font_header = ImageFont.truetype(FONT_BOLD, mm_to_pt(PT_12_EN_MM)) if FONT_BOLD else ImageFont.load_default()
        font_normal = ImageFont.truetype(FONT_REGULAR, mm_to_pt(PT_12_EN_MM)) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_header = ImageFont.load_default()
        font_normal = ImageFont.load_default()

    # === TITRE "BON DE LIVRAISON N°" centré ===
    titre_y = y
    num_bon = f"BL-{num_facture}"

    bbox_titre = draw.textbbox((0, 0), f"BON DE LIVRAISON N° {num_bon}", font=font_header)
    titre_width = bbox_titre[2] - bbox_titre[0]
    titre_x = table_x + (table_width - titre_width) // 2

    draw.text((titre_x, titre_y), f"BON DE LIVRAISON N° {num_bon}", font=font_header, fill='#000000')
    y += mm_to_px(10)

    # === EN-TÊTE DU TABLEAU ===
    header_y = y

    draw.rectangle(
        [(table_x, header_y), (table_x + table_width, header_y + header_height)],
        outline='#000000',
        fill=None,
        width=3
    )

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
    draw.text((x_offset + mm_to_px(3), text_y), "Désignation", font=font_header, fill='#000000')
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

    # === LIGNES DES PRODUITS ===
    row_count = max(len(produits), 5)

    for i in range(row_count):
        row_y = y + (i * row_height)

        if i % 2 == 0:
            row_fill = '#ffffff'
        else:
            row_fill = '#f5f5f5'

        draw.rectangle(
            [(table_x, row_y), (table_x + table_width, row_y + row_height)],
            fill=row_fill,
            outline='#000000',
            width=2
        )

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
            draw.text((x_offset + mm_to_px(3), text_y), designation, font=font_normal, fill='#333333')
            x_offset += col_widths['designation']

            # Quantité
            qte_str = str(p['quantite'])
            bbox_qte = draw.textbbox((0, 0), qte_str, font=font_normal)
            qte_height = bbox_qte[3] - bbox_qte[1]
            qte_width = bbox_qte[2] - bbox_qte[0]
            text_y = row_y + (row_height - qte_height) // 2
            text_x = x_offset + (col_widths['quantite'] - qte_width) // 2
            draw.text((text_x, text_y), qte_str, font=font_normal, fill='#333333')
            x_offset += col_widths['quantite']

            # Prix Unitaire
            prix_str = f"{p['prix_unitaire']:,.0f}"
            bbox_prix = draw.textbbox((0, 0), prix_str, font=font_normal)
            prix_height = bbox_prix[3] - bbox_prix[1]
            prix_width = bbox_prix[2] - bbox_prix[0]
            text_y = row_y + (row_height - prix_height) // 2
            text_x = x_offset + col_widths['prix_unitaire'] - prix_width - mm_to_px(3)
            draw.text((text_x, text_y), prix_str, font=font_normal, fill='#333333')
            x_offset += col_widths['prix_unitaire']

            # Montant
            montant_str = f"{p['total']:,.0f}"
            bbox_montant = draw.textbbox((0, 0), montant_str, font=font_normal)
            montant_height = bbox_montant[3] - bbox_montant[1]
            montant_width = bbox_montant[2] - bbox_montant[0]
            text_y = row_y + (row_height - montant_height) // 2
            text_x = x_offset + col_widths['montant'] - montant_width - mm_to_px(3)
            draw.text((text_x, text_y), montant_str, font=font_normal, fill='#333333')

    bottom_y = y + (row_count * row_height)
    draw.line(
        [(table_x, bottom_y), (table_x + table_width, bottom_y)],
        fill='#000000',
        width=3
    )

    draw.line([(table_x, header_y), (table_x, bottom_y)], fill='#000000', width=3)
    draw.line([(table_x + table_width, header_y), (table_x + table_width, bottom_y)], fill='#000000', width=3)

    return bottom_y + mm_to_px(7)

def generer_bas_facture_avec_pointilles(draw, width, padding, y_start, total, avance, reste,
                                        mode_paiement, depot_sortie, numero_cheque=""):
    """Génère le bas de facture avec pointillés pour la fin"""

    espace_1cm = mm_to_px(10)
    y = y_start + espace_1cm

    marge_gauche_droite = mm_to_px(10)

    # TOUTES LES POLICES EN 12pt
    try:
        font_normal = ImageFont.truetype(FONT_REGULAR, mm_to_pt(PT_12_EN_MM))
        font_bold = ImageFont.truetype(FONT_BOLD, mm_to_pt(PT_12_EN_MM))
        font_small = ImageFont.truetype(FONT_REGULAR, mm_to_pt(PT_12_EN_MM))
    except:
        font_normal = font_bold = font_small = ImageFont.load_default()

    # Ligne de séparation
    draw.line([(marge_gauche_droite, y - mm_to_px(2)), (width - marge_gauche_droite, y - mm_to_px(2))], fill='#dddddd', width=1)

    # === GAUCHE ===
    left_x = marge_gauche_droite
    line_height = mm_to_px(8)

    draw.text((left_x, y), f"Mode de paiement : {mode_paiement}", font=font_normal, fill='#333333')
    y += line_height

    if numero_cheque and mode_paiement == "Chèque":
        draw.text((left_x + mm_to_px(7), y), f"N° Chèque : {numero_cheque}", font=font_small, fill='#666666')
        y += line_height

    draw.text((left_x, y), f"Dépôt de sortie de stock : ", font=font_normal, fill='#333333')
    y += line_height
    draw.text((left_x + mm_to_px(5), y), f"{depot_sortie}", font=font_normal, fill='#333333')

    # === DROITE ===
    right_x = width - marge_gauche_droite
    total_y = y_start + espace_1cm + mm_to_px(2)

    espace_droite = mm_to_px(45)

    draw.text((right_x - espace_droite, total_y), "Montant Total :", font=font_bold, fill='#333333')
    draw.text((right_x - mm_to_px(3), total_y), f"{total:,.0f} Ar", font=font_bold, fill='#1a237e', anchor='rt')
    total_y += line_height

    draw.text((right_x - espace_droite, total_y), "Montant payé :", font=font_normal, fill='#333333')
    draw.text((right_x - mm_to_px(3), total_y), f"{avance:,.0f} Ar", font=font_normal, fill='#2e7d32', anchor='rt')
    total_y += line_height

    reste_color = '#d32f2f' if reste > 0 else '#2e7d32'
    draw.text((right_x - espace_droite, total_y), "Reste à payer :", font=font_bold, fill='#333333')
    draw.text((right_x - mm_to_px(3), total_y), f"{reste:,.0f} Ar", font=font_bold, fill=reste_color, anchor='rt')

    y_apres = max(y + line_height, total_y + 4)

    # === TIRÉS DE FIN ===
    y_sig = y_apres + mm_to_px(5)
    y_fin = y_sig + mm_to_px(30)

    for i in range(marge_gauche_droite, width - marge_gauche_droite, mm_to_px(3)):
        draw.line([(i, y_fin), (i + mm_to_px(2), y_fin)], fill='#999999', width=2)

    # === CACHET/SIGNATURE ===
    sig_width = mm_to_px(80)
    sig_x = width - marge_gauche_droite - sig_width

    draw.text((sig_x + (sig_width // 2) + 40, y_sig + mm_to_px(2)), "Cachet / Signature",
              font=font_small, fill='#000000', anchor='mt')

    centre_x = marge_gauche_droite + ((width - (marge_gauche_droite * 2)) // 2)
    draw.text((centre_x, y_fin - mm_to_px(5)), "Merci de votre confiance !",
              font=font_small, fill='#000000', anchor='mt')

    return y_fin + mm_to_px(10)

def generer_facture_proforma(client_nom, client_info, produits,
                            date_str, mode_paiement, depot_sortie,
                            total, avance, reste, commande_id,
                            numero_cheque=""):
    """Génère la facture proforma complète (300 DPI) et retourne le chemin du fichier"""

    annee = datetime.now().strftime("%Y")
    mois = datetime.now().strftime("%m")
    if not os.path.exists("factures"):
        os.makedirs("factures")
    filename = f"factures/facture n°_{commande_id} du {mois} {annee}.jpg"
    num_facture = f"{commande_id}/{annee}"

    width = mm_to_px(120)
    height = mm_to_px(225)
    padding = mm_to_px(5)

    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    y_position = mm_to_px(5)

    generer_en_tete(draw, img, width, padding, y_position)
    y_position += mm_to_px(27)

    client_y = generer_infos_client_rectangle(draw, width, padding, y_position, client_nom, client_info)

    date_y = generer_date(draw, width, padding, client_y, date_str)

    tableau_y = generer_tableau_bon_livraison(draw, width, padding, date_y, produits, commande_id, annee)

    generer_bas_facture_avec_pointilles(draw, width, padding, tableau_y, total, avance, reste,
                                       mode_paiement, depot_sortie, numero_cheque)

    img.save(filename, "JPEG", quality=95, dpi=(DPI, DPI))
    print(f"Facture générée avec succès : {filename} (300 DPI)")

    return filename

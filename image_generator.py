# facture_complete.py - Code complet pour générer la facture proforma (300 DPI)
from PIL import Image, ImageDraw, ImageFont
import os

# Configuration des polices (ajustez les chemins selon votre système)
FONT_REGULAR = "arial.ttf"  # Chemin vers une police régulière
FONT_BOLD = "arialbd.ttf"   # Chemin vers une police gras

# Constantes pour 300 DPI
DPI = 300
MM_TO_PX = DPI / 25.4  # 300 / 25.4 = 11.811 pixels par mm

def mm_to_px(mm):
    """Convertit les millimètres en pixels à 300 DPI"""
    return int(mm * MM_TO_PX)

def generer_en_tete(draw, img, width, padding, y):
    """Génère l'en-tête avec logo et texte comme sur l'image"""
    
    # Charger le logo
    logo = None
    logo_width = 0
    try:
        logo_path = "images/logo.png"
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            # Redimensionner le logo (4cm x 4cm = 40mm x 40mm)
            logo_size = mm_to_px(40)  # 40mm = 472 pixels à 300 DPI
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            img.paste(logo, (padding, y))
            logo_width = logo.width + 10
    except:
        logo_width = 0
    
    # Position du texte à côté du logo
    text_x = padding + logo_width
    
    # Sous-titre "Vente en gros et détail" en bas du logo
    try:
        font_soustitre = ImageFont.truetype(FONT_REGULAR, mm_to_px(3)) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_soustitre = ImageFont.load_default()
    
    # Position du sous-titre centré sous le logo
    if logo_width > 0:
        logo_actual_width = logo.width if logo else 0
        logo_center_x = padding + (logo_actual_width // 2)
        bbox_soustitre = draw.textbbox((0, 0), "Vente en gros et détail", font=font_soustitre)
        soustitre_width = bbox_soustitre[2] - bbox_soustitre[0]
        soustitre_x = logo_center_x - (soustitre_width // 2)
        draw.text((soustitre_x, y + logo.height + mm_to_px(1)), "Vente en gros et détail", font=font_soustitre, fill='#666666')
    
    # Contact - centré par rapport au logo
    logo_bottom = y + (logo.height if logo else mm_to_px(20))
    
    try:
        font_contact = ImageFont.truetype(FONT_REGULAR, mm_to_px(3)) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_contact = ImageFont.load_default()
    
    # Position du contact centrée horizontalement par rapport au logo
    contact_text = "Contact : 034 41 463 65"
    bbox_contact = draw.textbbox((0, 0), contact_text, font=font_contact)
    contact_width = bbox_contact[2] - bbox_contact[0]
    
    # Calculer le centre du logo
    if logo_width > 0:
        logo_actual_width = logo.width if logo else 0
        logo_center_x = padding + (logo_actual_width // 2)
    else:
        logo_center_x = padding + mm_to_px(10)
    
    contact_x = logo_center_x - (contact_width // 2)
    
    draw.text((contact_x, logo_bottom + mm_to_px(1)), contact_text, font=font_contact, fill='#888888')
    
    return logo_width

def dessiner_rectangle_arrondi(draw, xy, rayon, fill=None, outline='#000000', width=2):
    """Dessine un rectangle avec des coins arrondis (sans remplissage)"""
    x1, y1, x2, y2 = xy
    
    # Dessiner les 4 coins arrondis (uniquement les contours)
    draw.arc([x1, y1, x1 + 2*rayon, y1 + 2*rayon], 180, 270, fill=outline, width=width)
    draw.arc([x2 - 2*rayon, y1, x2, y1 + 2*rayon], 270, 360, fill=outline, width=width)
    draw.arc([x1, y2 - 2*rayon, x1 + 2*rayon, y2], 90, 180, fill=outline, width=width)
    draw.arc([x2 - 2*rayon, y2 - 2*rayon, x2, y2], 0, 90, fill=outline, width=width)
    draw.rectangle([x1 + rayon, y1, x2 - rayon, y2], outline=outline, width=width)
    draw.rectangle([x1, y1 + rayon, x2, y2 - rayon], outline=outline, width=width)

def generer_infos_client_rectangle(draw, width, padding, y_start, client_nom, client_info):
    """Génère un rectangle avec les informations client en haut à droite (bordure noire, sans remplissage)"""
    
    # Dimensions du rectangle (largeur 100mm)
    rect_width = mm_to_px(100)  # 100mm = 1181 pixels à 300 DPI
    rect_height = mm_to_px(40)  # 40mm = 472 pixels à 300 DPI
    rect_x = width - padding - rect_width
    rect_y = y_start
    rayon = mm_to_px(3)  # Rayon de 3mm
    
    # Dessiner le rectangle arrondi (sans remplissage, bordure noire)
    dessiner_rectangle_arrondi(
        draw, 
        (rect_x, rect_y, rect_x + rect_width, rect_y + rect_height), 
        rayon, 
        fill=None, 
        outline='#000000', 
        width=2
    )
    
    # Charger les polices (taille 12 points = 4mm à 300 DPI)
    font_size = mm_to_px(4)  # 4mm ≈ 12 points
    try:
        if FONT_REGULAR and os.path.exists(FONT_REGULAR):
            font_label = ImageFont.truetype(FONT_REGULAR, font_size)
            font_value = ImageFont.truetype(FONT_BOLD, font_size)
        else:
            font_label = ImageFont.load_default()
            font_value = ImageFont.load_default()
    except:
        font_label = ImageFont.load_default()
        font_value = ImageFont.load_default()
    
    # Position à l'intérieur du rectangle (avec marge de 3mm)
    margin = mm_to_px(3)
    inner_x = rect_x + margin
    y = rect_y + margin
    line_height = mm_to_px(7)  # Hauteur de ligne 7mm
    
    # Client (supporte UTF-8)
    draw.text((inner_x, y), "Client :", font=font_label, fill='#666666')
    draw.text((inner_x + mm_to_px(20), y), client_nom, font=font_value, fill='#1a237e')
    y += line_height
    
    # Stat
    stat = client_info.get('stat', '')
    draw.text((inner_x, y), "Stat :", font=font_label, fill='#666666')
    draw.text((inner_x + mm_to_px(20), y), stat, font=font_value, fill='#1a237e')
    y += line_height
    
    # Adresse
    adresse = client_info.get('adresse', '')
    draw.text((inner_x, y), "Adresse :", font=font_label, fill='#666666')
    draw.text((inner_x + mm_to_px(20), y), adresse, font=font_value, fill='#1a237e')
    y += line_height
    
    # Contact
    contact = client_info.get('contact', '')
    draw.text((inner_x, y), "Contact :", font=font_label, fill='#666666')
    draw.text((inner_x + mm_to_px(20), y), contact, font=font_value, fill='#1a237e')
    y += line_height
    
    # Responsable
    responsable = client_info.get('responsable', '')
    draw.text((inner_x, y), "Responsable :", font=font_label, fill='#666666')
    draw.text((inner_x + mm_to_px(20), y), responsable, font=font_value, fill='#1a237e')
    
    return rect_y + rect_height

def generer_date(draw, width, padding, y_rectangle_bottom, date_str):
    """Génère la date en dessous du rectangle (à l'extérieur)"""
    
    font_size = mm_to_px(4)  # 4mm ≈ 12 points
    try:
        if FONT_REGULAR and os.path.exists(FONT_REGULAR):
            font_date = ImageFont.truetype(FONT_REGULAR, font_size)
        else:
            font_date = ImageFont.load_default()
    except:
        font_date = ImageFont.load_default()
    
    # Dimensions du rectangle
    rect_width = mm_to_px(100)
    rect_x = width - padding - rect_width
    
    # Calculer la position centrée horizontalement par rapport au rectangle
    bbox = draw.textbbox((0, 0), f"Date : {date_str}", font=font_date)
    text_width = bbox[2] - bbox[0]
    
    # Centrer le texte horizontalement dans le rectangle
    date_x = rect_x + (rect_width - text_width) // 2
    
    # Position verticale : en dessous du rectangle (marge 3mm)
    date_y = y_rectangle_bottom + mm_to_px(3)
    
    draw.text((date_x, date_y), f"Date : {date_str}", font=font_date, fill='#666666')
    
    # Retourner la nouvelle position Y (après la date + marge)
    return date_y + mm_to_px(7)

def generer_tableau_bon_livraison(draw, width, padding, y_start, produits, num_facture, annee):
    """Génère le tableau BON DE LIVRAISON avec espace avant de 1cm"""
    
    # Espace 1cm = 10mm
    espace_1cm = mm_to_px(10)
    
    # Ajouter l'espace de 1cm avant le tableau
    y = y_start + espace_1cm
    
    # Dimensions du tableau (en pixels à 300 DPI)
    col_widths = {
        'designation': mm_to_px(100),  # 100mm
        'quantite': mm_to_px(27),      # 27mm
        'prix_unitaire': mm_to_px(40), # 40mm
        'montant': mm_to_px(43)        # 43mm
    }
    
    # Calculer la largeur totale du tableau
    table_width = sum(col_widths.values())
    table_x = (width - table_width) // 2  # Centrer le tableau
    
    # Hauteur des lignes
    header_height = mm_to_px(12)  # 12mm
    row_height = mm_to_px(10)     # 10mm
    
    # Charger les polices
    font_size = mm_to_px(4)  # 4mm ≈ 12 points
    try:
        if FONT_REGULAR and os.path.exists(FONT_REGULAR):
            font_header = ImageFont.truetype(FONT_BOLD, font_size)
            font_normal = ImageFont.truetype(FONT_REGULAR, font_size)
        else:
            font_header = ImageFont.load_default()
            font_normal = ImageFont.load_default()
    except:
        font_header = ImageFont.load_default()
        font_normal = ImageFont.load_default()
    
    # === TITRE "BON DE LIVRAISON N°" centré ===
    titre_y = y
    num_bon = f"BL-{annee}-{num_facture}"
    
    # Calculer la largeur du titre pour le centrer
    bbox_titre = draw.textbbox((0, 0), f"BON DE LIVRAISON N° {num_bon}", font=font_header)
    titre_width = bbox_titre[2] - bbox_titre[0]
    titre_x = table_x + (table_width - titre_width) // 2
    
    draw.text((titre_x, titre_y), f"BON DE LIVRAISON N° {num_bon}", font=font_header, fill='#000000')
    y += mm_to_px(8)  # Espace après le titre
    
    # === EN-TÊTE DU TABLEAU avec fond bleu ===
    header_y = y
    draw.rectangle(
        [(table_x, header_y), (table_x + table_width, header_y + header_height)],
        outline='#1a237e'
    )
    
    # Texte des colonnes
    x_offset = table_x
    draw.text((x_offset + mm_to_px(3), header_y + mm_to_px(3)), "Désignation", font=font_header, fill='white')
    x_offset += col_widths['designation']
    
    draw.text((x_offset + mm_to_px(3), header_y + mm_to_px(3)), "Quantité", font=font_header, fill='white')
    x_offset += col_widths['quantite']
    
    draw.text((x_offset + mm_to_px(3), header_y + mm_to_px(3)), "Prix Unitaire", font=font_header, fill='white')
    x_offset += col_widths['prix_unitaire']
    
    draw.text((x_offset + mm_to_px(3), header_y + mm_to_px(3)), "Montant (Ar)", font=font_header, fill='white')
    
    y += header_height
    
    # === LIGNES DES PRODUITS ===
    row_count = max(len(produits), 5)  # Minimum 5 lignes
    
    for i in range(row_count):
        row_y = y + (i * row_height)
        
        # Alternance des couleurs de lignes
        if i % 2 == 0:
            row_fill = '#ffffff'
        else:
            row_fill = '#f5f5f5'
        
        # Dessiner la ligne
        draw.rectangle(
            [(table_x, row_y), (table_x + table_width, row_y + row_height)],
            fill=row_fill,
            outline='#dddddd'
        )
        
        # Remplir avec les données si disponibles
        if i < len(produits):
            p = produits[i]
            x_offset = table_x
            
            # Désignation (supporte UTF-8)
            max_chars = mm_to_px(100) // font_size * 2
            designation = p['nom'][:max_chars] + "..." if len(p['nom']) > max_chars else p['nom']
            draw.text((x_offset + mm_to_px(3), row_y + mm_to_px(2)), designation, font=font_normal, fill='#333333')
            x_offset += col_widths['designation']
            
            # Quantité
            draw.text((x_offset + mm_to_px(3), row_y + mm_to_px(2)), str(p['quantite']), font=font_normal, fill='#333333')
            x_offset += col_widths['quantite']
            
            # Prix Unitaire
            draw.text((x_offset + mm_to_px(3), row_y + mm_to_px(2)), f"{p['prix_unitaire']:,.0f}", font=font_normal, fill='#333333')
            x_offset += col_widths['prix_unitaire']
            
            # Montant
            draw.text((x_offset + mm_to_px(3), row_y + mm_to_px(2)), f"{p['total']:,.0f}", font=font_normal, fill='#333333')
    
    # Ligne de bordure en bas du tableau
    bottom_y = y + (row_count * row_height)
    draw.line(
        [(table_x, bottom_y), (table_x + table_width, bottom_y)],
        fill='#000000',
        width=3
    )
    
    return bottom_y + mm_to_px(7)

def generer_bas_facture_avec_pointilles(draw, width, padding, y_start, total, avance, reste, 
                                        mode_paiement, depot_sortie, numero_cheque=""):
    """Génère le bas de facture avec pointillés pour la fin"""
    
    espace_1cm = mm_to_px(10)
    y = y_start + espace_1cm
    
    font_size = mm_to_px(4)  # 4mm ≈ 12 points
    font_small_size = mm_to_px(3)  # 3mm ≈ 9 points
    
    try:
        font_normal = ImageFont.truetype(FONT_REGULAR, font_size)
        font_bold = ImageFont.truetype(FONT_BOLD, font_size)
        font_small = ImageFont.truetype(FONT_REGULAR, font_small_size)
    except:
        font_normal = font_bold = font_small = ImageFont.load_default()
    
    # Ligne de séparation
    draw.line([(padding, y - mm_to_px(3)), (width - padding, y - mm_to_px(3))], fill='#dddddd', width=1)
    
    # === GAUCHE ===
    left_x = padding
    line_height = mm_to_px(8)
    
    draw.text((left_x, y), f"Mode de paiement : {mode_paiement}", font=font_normal, fill='#333333')
    y += line_height
    
    if numero_cheque and mode_paiement == "Chèque":
        draw.text((left_x + mm_to_px(7), y), f"N° Chèque : {numero_cheque}", font=font_small, fill='#666666')
        y += line_height
    
    draw.text((left_x, y), f"Dépôt de sortie de stock : {depot_sortie}", font=font_normal, fill='#333333')
    
    # === DROITE ===
    right_x = width - padding
    total_y = y_start + espace_1cm + mm_to_px(2)
    
    draw.text((right_x - mm_to_px(50), total_y), "Montant Total :", font=font_bold, fill='#333333')
    draw.text((right_x - mm_to_px(3), total_y), f"{total:,.0f} Ar", font=font_bold, fill='#1a237e', anchor='rt')
    total_y += line_height
    
    draw.text((right_x - mm_to_px(50), total_y), "Montant payé :", font=font_normal, fill='#333333')
    draw.text((right_x - mm_to_px(3), total_y), f"{avance:,.0f} Ar", font=font_normal, fill='#2e7d32', anchor='rt')
    total_y += line_height
    
    reste_color = '#d32f2f' if reste > 0 else '#2e7d32'
    draw.text((right_x - mm_to_px(50), total_y), "Reste à payer :", font=font_bold, fill='#333333')
    draw.text((right_x - mm_to_px(3), total_y), f"{reste:,.0f} Ar", font=font_bold, fill=reste_color, anchor='rt')
    
    y_apres = max(y + line_height, total_y + line_height)
    
    # === CACHET/SIGNATURE à droite ===
    y_sig = y_apres + mm_to_px(7)
    sig_width = mm_to_px(83)  # 83mm
    sig_x = width - padding - sig_width
    
    # Ligne pour signature
    draw.text((sig_x + (sig_width // 2), y_sig + mm_to_px(2)), "Cachet / Signature", font=font_small, fill='#666666', anchor='mt')
    
    # === TIRÉS DE FIN ===
    y_fin = y_sig + mm_to_px(13)
    
    # Texte "Merci de votre confiance!" en dessus du tiré
    draw.text((width//2, y_fin - mm_to_px(5)), "Merci de votre confiance !", 
              font=font_small, fill='#666666', anchor='mt')
    
    # Ligne pointillée avec des tirets
    for i in range(padding, width - padding, mm_to_px(3)):
        draw.line([(i, y_fin), (i + mm_to_px(2), y_fin)], fill='#999999', width=2)
    
    return y_fin + mm_to_px(10)

def generer_facture_proforma(client_nom, client_info, produits, 
                            date_str, mode_paiement, depot_sortie, 
                            total, avance, reste, commande_id, 
                            numero_cheque=""):
    """Génère la facture proforma complète (300 DPI)"""
    from datetime import datetime
    
    # Générer automatiquement le nom du fichier
    annee = datetime.now().strftime("%Y")
    filename = f"facture_{commande_id}_{annee}.jpg"
    num_facture = f"{commande_id}/{annee}"
    """Génère la facture proforma complète (300 DPI)"""
    
    # Dimensions de l'image (80mm de largeur à 300 DPI)
    width = mm_to_px(80)   # 80mm = 945 pixels à 300 DPI
    height = mm_to_px(297) # 297mm (A4) = 3508 pixels à 300 DPI
    padding = mm_to_px(5)  # 5mm = 59 pixels
    
    # Créer l'image blanche
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Générer chaque section
    y_position = mm_to_px(5)  # Marge 5mm
    
    # En-tête
    generer_en_tete(draw, img, width, padding, y_position)
    y_position += mm_to_px(27)  # Espace après l'en-tête
    
    # Informations client rectangle
    client_y = generer_infos_client_rectangle(draw, width, padding, y_position, client_nom, client_info)
    
    # Date (en dessous du rectangle, à l'extérieur)
    date_y = generer_date(draw, width, padding, client_y, date_str)
    
    # Tableau (commence après la date)
    tableau_y = generer_tableau_bon_livraison(draw, width, padding, date_y, produits, num_facture, annee)
    
    # Bas de page
    generer_bas_facture_avec_pointilles(draw, width, padding, tableau_y, total, avance, reste, 
                                       mode_paiement, depot_sortie, numero_cheque)
    
    # Sauvegarder avec haute qualité
    img.save(filename, "JPEG", quality=95, dpi=(DPI, DPI))
    print(f"Facture générée avec succès : {filename} (300 DPI)")
    
    return img

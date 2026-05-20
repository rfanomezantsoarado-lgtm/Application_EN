# facture_complete.py - Code complet pour générer la facture proforma
from PIL import Image, ImageDraw, ImageFont
import os

# Configuration des polices (ajustez les chemins selon votre système)
FONT_REGULAR = "arial.ttf"  # Chemin vers une police régulière
FONT_BOLD = "arialbd.ttf"   # Chemin vers une police gras

def generer_en_tete(draw, img, width, padding, y):
    """Génère l'en-tête avec logo et texte comme sur l'image"""
    
    # Charger le logo
    logo = None
    logo_width = 0
    try:
        logo_path = "images/logo.png"
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            # Redimensionner le logo (hauteur 60px)
            logo.thumbnail((60, 60), Image.Resampling.LANCZOS)
            img.paste(logo, (padding, y))
            logo_width = logo.width + 10
    except:
        logo_width = 0
    
    # Position du texte à côté du logo
    text_x = padding + logo_width
    
    # Texte "MATÉRIAUX DE CONSTRUCTION" directement (sans ENTREPRISE)
    try:
        font_materiaux = ImageFont.truetype(FONT_BOLD, 14) if FONT_BOLD else ImageFont.load_default()
    except:
        font_materiaux = ImageFont.load_default()
    
    draw.text((text_x, y + 5), "MATÉRIAUX DE CONSTRUCTION", 
              font=font_materiaux, fill='#1a237e')
    
    # Sous-titre "Vente en gros et détail" en dessous
    try:
        font_soustitre = ImageFont.truetype(FONT_REGULAR, 10) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_soustitre = ImageFont.load_default()
    
    draw.text((text_x, y + 25), "Vente en gros et détail", font=font_soustitre, fill='#666666')
    
    # Contact - centré par rapport au logo
    logo_bottom = y + 60  # Le logo fait 60px de hauteur
    
    try:
        font_contact = ImageFont.truetype(FONT_REGULAR, 9) if FONT_REGULAR else ImageFont.load_default()
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
        logo_center_x = padding + 30  # Valeur par défaut si pas de logo
    
    contact_x = logo_center_x - (contact_width // 2)
    
    draw.text((contact_x, logo_bottom - 15), contact_text, font=font_contact, fill='#888888')
    
    return logo_width

def dessiner_rectangle_arrondi(draw, xy, rayon, fill, outline=None, width=1):
    """Dessine un rectangle avec des coins arrondis"""
    x1, y1, x2, y2 = xy
    if outline is None:
        outline = fill
    
    # Dessiner les 4 coins arrondis
    draw.rectangle([x1 + rayon, y1, x2 - rayon, y2], fill=fill, outline=outline)
    draw.rectangle([x1, y1 + rayon, x2, y2 - rayon], fill=fill, outline=outline)
    
    # Dessiner les cercles aux coins
    draw.pieslice([x1, y1, x1 + 2*rayon, y1 + 2*rayon], 180, 270, fill=fill, outline=outline)
    draw.pieslice([x2 - 2*rayon, y1, x2, y1 + 2*rayon], 270, 360, fill=fill, outline=outline)
    draw.pieslice([x1, y2 - 2*rayon, x1 + 2*rayon, y2], 90, 180, fill=fill, outline=outline)
    draw.pieslice([x2 - 2*rayon, y2 - 2*rayon, x2, y2], 0, 90, fill=fill, outline=outline)

def generer_infos_client_rectangle(draw, width, padding, y_start, client_nom, client_info):
    """Génère un rectangle arrondi avec les informations client en haut à droite"""
    
    # Dimensions du rectangle
    rect_width = 300
    rect_height = 120
    rect_x = width - padding - rect_width
    rect_y = y_start
    rayon = 10
    
    # Dessiner le rectangle arrondi
    dessiner_rectangle_arrondi(
        draw, 
        (rect_x, rect_y, rect_x + rect_width, rect_y + rect_height), 
        rayon, 
        fill='#f5f5f5', 
        outline='#cccccc', 
        width=1
    )
    
    # Charger les polices
    try:
        if FONT_REGULAR and os.path.exists(FONT_REGULAR):
            font_label = ImageFont.truetype(FONT_REGULAR, 10)
            font_value = ImageFont.truetype(FONT_BOLD, 11)
        else:
            font_label = ImageFont.load_default()
            font_value = ImageFont.load_default()
    except:
        font_label = ImageFont.load_default()
        font_value = ImageFont.load_default()
    
    # Position à l'intérieur du rectangle (avec marge)
    margin = 10
    inner_x = rect_x + margin
    y = rect_y + margin
    line_height = 22
    
    # Client
    draw.text((inner_x, y), "Client :", font=font_label, fill='#666666')
    draw.text((inner_x + 60, y), client_nom, font=font_value, fill='#1a237e')
    y += line_height
    
    # Stat
    stat = client_info.get('stat', '')
    draw.text((inner_x, y), "Stat :", font=font_label, fill='#666666')
    draw.text((inner_x + 60, y), stat, font=font_value, fill='#1a237e')
    y += line_height
    
    # Adresse
    adresse = client_info.get('adresse', '')
    draw.text((inner_x, y), "Adresse :", font=font_label, fill='#666666')
    draw.text((inner_x + 60, y), adresse, font=font_value, fill='#1a237e')
    y += line_height
    
    # Contact
    contact = client_info.get('contact', '')
    draw.text((inner_x, y), "Contact :", font=font_label, fill='#666666')
    draw.text((inner_x + 60, y), contact, font=font_value, fill='#1a237e')
    y += line_height
    
    # Responsable
    responsable = client_info.get('responsable', '')
    draw.text((inner_x, y), "Responsable :", font=font_label, fill='#666666')
    draw.text((inner_x + 60, y), responsable, font=font_value, fill='#1a237e')
    
    return rect_y + rect_height

def generer_date(draw, width, padding, y_date, date_str):
    """Génère la date centrée en bas du rectangle client"""
    
    try:
        if FONT_REGULAR and os.path.exists(FONT_REGULAR):
            font_date = ImageFont.truetype(FONT_REGULAR, 10)
        else:
            font_date = ImageFont.load_default()
    except:
        font_date = ImageFont.load_default()
    
    # Dimensions du rectangle (doivent correspondre à celles dans generer_infos_client_rectangle)
    rect_width = 300
    rect_height = 120
    rect_x = width - padding - rect_width
    
    # Calculer la position centrée en bas du rectangle (à l'intérieur)
    bbox = draw.textbbox((0, 0), f"Date : {date_str}", font=font_date)
    text_width = bbox[2] - bbox[0]
    
    # Centrer le texte horizontalement dans le rectangle
    date_x = rect_x + (rect_width - text_width) // 2
    
    # Position verticale (à l'intérieur du rectangle, en bas)
    date_y = y_date - 18  # y_date est le bas du rectangle, on remonte de 18px
    
    draw.text((date_x, date_y), f"Date : {date_str}", font=font_date, fill='#666666')

def generer_tableau_bon_livraison(draw, width, padding, y_start, produits):
    """Génère le tableau BON DE LIVRAISON avec espace avant de 1cm"""
    
    # Conversion 1cm ≈ 38 pixels (à 96 DPI)
    espace_1cm = 38
    
    # Ajouter l'espace de 1cm avant le tableau
    y = y_start + espace_1cm
    
    # Dimensions du tableau
    col_widths = {
        'designation': 300,
        'quantite': 80,
        'prix_unitaire': 120,
        'montant': 130
    }
    
    # Calculer la largeur totale du tableau
    table_width = sum(col_widths.values())
    table_x = (width - table_width) // 2  # Centrer le tableau
    
    # Hauteur des lignes
    header_height = 35
    row_height = 30
    
    # Charger les polices
    try:
        if FONT_REGULAR and os.path.exists(FONT_REGULAR):
            font_header = ImageFont.truetype(FONT_BOLD, 12)
            font_normal = ImageFont.truetype(FONT_REGULAR, 11)
        else:
            font_header = ImageFont.load_default()
            font_normal = ImageFont.load_default()
    except:
        font_header = ImageFont.load_default()
        font_normal = ImageFont.load_default()
    
    # === TITRE "BON DE LIVRAISON N°" ===
    titre_y = y
    num_bon = "BL-2024-001"
    draw.text((table_x, titre_y), f"BON DE LIVRAISON N° {num_bon}", font=font_header, fill='#000000')
    y += 25
    
    # === EN-TÊTE DU TABLEAU avec fond bleu ===
    header_y = y
    draw.rectangle(
        [(table_x, header_y), (table_x + table_width, header_y + header_height)],
        fill='#1a237e',
        outline='#1a237e'
    )
    
    # Texte des colonnes
    x_offset = table_x
    draw.text((x_offset + 10, header_y + 10), "Désignation", font=font_header, fill='white')
    x_offset += col_widths['designation']
    
    draw.text((x_offset + 10, header_y + 10), "Quantité", font=font_header, fill='white')
    x_offset += col_widths['quantite']
    
    draw.text((x_offset + 10, header_y + 10), "Prix Unitaire", font=font_header, fill='white')
    x_offset += col_widths['prix_unitaire']
    
    draw.text((x_offset + 10, header_y + 10), "Montant (Ar)", font=font_header, fill='white')
    
    y += header_height
    
    # === LIGNES DES PRODUITS ===
    row_count = max(len(produits), 5)  # Minimum 5 lignes comme sur l'image
    
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
            
            # Désignation
            designation = p['nom'][:35] + "..." if len(p['nom']) > 35 else p['nom']
            draw.text((x_offset + 10, row_y + 8), designation, font=font_normal, fill='#333333')
            x_offset += col_widths['designation']
            
            # Quantité
            draw.text((x_offset + 10, row_y + 8), str(p['quantite']), font=font_normal, fill='#333333')
            x_offset += col_widths['quantite']
            
            # Prix Unitaire
            draw.text((x_offset + 10, row_y + 8), f"{p['prix_unitaire']:,.0f}", font=font_normal, fill='#333333')
            x_offset += col_widths['prix_unitaire']
            
            # Montant
            draw.text((x_offset + 10, row_y + 8), f"{p['total']:,.0f}", font=font_normal, fill='#333333')
    
    # Ligne de bordure en bas du tableau
    bottom_y = y + (row_count * row_height)
    draw.line(
        [(table_x, bottom_y), (table_x + table_width, bottom_y)],
        fill='#000000',
        width=2
    )
    
    return bottom_y + 20

def generer_bas_facture_avec_pointilles(draw, width, padding, y_start, total, avance, reste, 
                                        mode_paiement, depot_sortie, numero_cheque=""):
    """Génère le bas de facture avec pointillés pour la fin"""
    
    espace_1cm = 38
    y = y_start + espace_1cm
    
    try:
        font_normal = ImageFont.truetype(FONT_REGULAR, 11)
        font_bold = ImageFont.truetype(FONT_BOLD, 12)
        font_small = ImageFont.truetype(FONT_REGULAR, 10)
    except:
        font_normal = font_bold = font_small = ImageFont.load_default()
    
    # Ligne de séparation
    draw.line([(padding, y - 10), (width - padding, y - 10)], fill='#dddddd', width=1)
    
    # === GAUCHE ===
    left_x = padding
    line_height = 25
    
    draw.text((left_x, y), f"Mode de paiement : {mode_paiement}", font=font_normal, fill='#333333')
    y += line_height
    
    if numero_cheque and mode_paiement == "Chèque":
        draw.text((left_x + 20, y), f"N° Chèque : {numero_cheque}", font=font_small, fill='#666666')
        y += line_height
    
    draw.text((left_x, y), f"Dépôt de sortie de stock : {depot_sortie}", font=font_normal, fill='#333333')
    
    # === DROITE ===
    right_x = width - padding
    total_y = y_start + espace_1cm + 5
    
    draw.text((right_x - 150, total_y), "Montant Total :", font=font_bold, fill='#333333')
    draw.text((right_x - 10, total_y), f"{total:,.0f} Ar", font=font_bold, fill='#1a237e', anchor='rt')
    total_y += line_height
    
    draw.text((right_x - 150, total_y), "Montant payé :", font=font_normal, fill='#333333')
    draw.text((right_x - 10, total_y), f"{avance:,.0f} Ar", font=font_normal, fill='#2e7d32', anchor='rt')
    total_y += line_height
    
    reste_color = '#d32f2f' if reste > 0 else '#2e7d32'
    draw.text((right_x - 150, total_y), "Reste à payer :", font=font_bold, fill='#333333')
    draw.text((right_x - 10, total_y), f"{reste:,.0f} Ar", font=font_bold, fill=reste_color, anchor='rt')
    
    y_apres = max(y + line_height, total_y + line_height)
    
    # === CACHET/SIGNATURE à droite ===
    y_sig = y_apres + 20
    sig_x = width - padding - 200
    
    draw.line([(sig_x, y_sig), (width - padding, y_sig)], fill='#000000', width=1)
    draw.text((sig_x + 100, y_sig + 5), "Cachet / Signature", font=font_small, fill='#666666', anchor='mt')
    
    # === TIRÉS DE FIN ===
    y_fin = y_sig + 40
    
    # Ligne pointillée avec des tirets
    for i in range(padding, width - padding, 10):
        draw.line([(i, y_fin), (i + 5, y_fin)], fill='#999999', width=2)
    
    # Pied de page
    draw.text((width//2, y_fin + 15), "Merci de votre confiance !", 
              font=font_small, fill='#999999', anchor='mt')
    
    return y_fin + 30

def generer_facture_proforma(filename, client_nom, client_info, produits, 
                            date_str, mode_paiement, depot_sortie, 
                            total, avance, reste, numero_cheque=""):
    """Génère la facture proforma complète"""
    
    # Dimensions de l'image (A4 en pixels à 96 DPI: 794x1123)
    width = 800
    height = 1100
    padding = 30
    
    # Créer l'image blanche
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Générer chaque section
    y_position = 30
    
    # En-tête
    generer_en_tete(draw, img, width, padding, y_position)
    y_position += 70
    
    # Informations client rectangle
    client_y = generer_infos_client_rectangle(draw, width, padding, y_position, client_nom, client_info)
    
    # Date (centrée en bas du rectangle)
    generer_date(draw, width, padding, client_y, date_str)
    
    # Tableau
    tableau_y = generer_tableau_bon_livraison(draw, width, padding, client_y + 10, produits)
    
    # Bas de page
    generer_bas_facture_avec_pointilles(draw, width, padding, tableau_y, total, avance, reste, 
                                       mode_paiement, depot_sortie, numero_cheque)
    
    # Sauvegarder avec haute qualité
    img.save(filename, "JPEG", quality=95)
    print(f"Facture générée avec succès : {filename}")
    
    return img

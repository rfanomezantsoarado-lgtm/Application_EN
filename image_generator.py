# image_generator.py - Version corrigée
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime

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
            logo_size = mm_to_px(30)  # 40mm = 472 pixels à 300 DPI
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            # Convertir le logo en RGB si nécessaire
            if logo.mode != 'RGB':
                logo = logo.convert('RGB')
            # Coller le logo sur l'image principale
            img.paste(logo, (padding, y))
            logo_width = logo.width + 5
    except Exception as e:
        print(f"Erreur chargement logo: {e}")
        logo_width = 0

    # Sous-titre "Vente en gros et détail" en bas du logo
    try:
        font_soustitre = ImageFont.truetype(FONT_REGULAR, mm_to_px(3)) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_soustitre = ImageFont.load_default()

    # Position du sous-titre centré sous le logo
    if logo and logo_width > 0:
        logo_actual_width = logo.width
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
    if logo and logo_width > 0:
        logo_actual_width = logo.width
        logo_center_x = padding + (logo_actual_width // 2)
    else:
        logo_center_x = padding + mm_to_px(10)

    contact_x = logo_center_x - (contact_width // 2)
    contact_y = logo_bottom + mm_to_px(5)

    draw.text((contact_x, contact_y), contact_text, font=font_contact, fill='#888888')

    return logo_width

def dessiner_rectangle_arrondi(draw, xy, rayon, fill=None, outline='#000000', width=2):
    """Dessine un rectangle avec des coins arrondis (sans remplissage)"""
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

    # Calcul des dimensions du rectangle
    rect_width = mm_to_px(50)   # Largeur du rectangle (8.5cm)
    rect_height = mm_to_px(25)  # Hauteur du rectangle (5.5cm)

    # Position horizontale : à 5cm du bord gauche
    rect_x = mm_to_px(60)  # 5cm depuis la gauche

    # Position verticale : utiliser le même y_start que l'en-tête
    rect_y = 110

    # Dessiner le rectangle arrondi (uniquement le contour)
    dessiner_rectangle_arrondi(draw,
                              [rect_x, rect_y, rect_x + rect_width, rect_y + rect_height],
                              rayon=mm_to_px(3),
                              outline='#000000',
                              width=2)

    # Polices - TAILLES CORRIGÉES (plus petites)
    font_label_size = mm_to_px(2)   # 3.5mm pour les labels (Client:, Stat:, etc.)
    font_value_size = mm_to_px(2)   # 3.5mm pour les valeurs (même taille)

    try:
        font_label = ImageFont.truetype(FONT_REGULAR, font_label_size) if FONT_REGULAR else ImageFont.load_default()
        font_value = ImageFont.truetype(FONT_REGULAR, font_value_size) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_label = ImageFont.load_default()
        font_value = ImageFont.load_default()

    # Position à l'intérieur du rectangle (marge réduite)
    margin = mm_to_px(2)
    inner_x = rect_x + margin
    y = rect_y + margin
    line_height = mm_to_px(5)

    # Largeur pour la colonne des labels
    label_width = mm_to_px(10)  # Largeur réservée pour les labels (1.8cm)

    # Client
    draw.text((inner_x, y), "Client :", font=font_label, fill='#666666')
    draw.text((inner_x + label_width, y), client_nom, font=font_value, fill='#000000')
    y += line_height

    # Stat
    stat = client_info.get('stat', '')
    draw.text((inner_x, y), "Stat :", font=font_label, fill='#666666')
    draw.text((inner_x + label_width, y), stat, font=font_value, fill='#000000')
    y += line_height

    # Adresse
    adresse = client_info.get('adresse', '')
    draw.text((inner_x, y), "Adresse :", font=font_label, fill='#666666')
    draw.text((inner_x + label_width, y), adresse, font=font_value, fill='#000000')
    y += line_height

    # Contact
    contact = client_info.get('contact', '')
    draw.text((inner_x, y), "Contact :", font=font_label, fill='#666666')
    draw.text((inner_x + label_width, y), contact, font=font_value, fill='#000000')
    y += line_height

    # Responsable
    responsable = client_info.get('responsable', '')
    draw.text((inner_x, y), "Responsable :", font=font_label, fill='#666666')
    draw.text((inner_x + mm_to_px(15), y), responsable, font=font_value, fill='#000000')

    return rect_y + rect_height

def generer_date(draw, width, padding, y_rectangle_bottom, date_str):
    """Génère la date en dessous du rectangle (à l'extérieur)"""

    font_size = mm_to_px(3)  # 4mm ≈ 12 points
    try:
        font_date = ImageFont.truetype(FONT_REGULAR, font_size) if FONT_REGULAR else ImageFont.load_default()
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

    draw.text((date_x, date_y), f"Date : {date_str}", font=font_date, fill='#666666')

    # Retourner la nouvelle position Y (après la date + marge)
    return date_y + mm_to_px(7)

def generer_tableau_bon_livraison(draw, width, padding, y_start, produits, num_facture, annee):
    """Génère le tableau BON DE LIVRAISON avec espace avant de 1cm"""

    # Espace 1cm = 10mm
    espace_1cm = mm_to_px(5)

    # Ajouter l'espace de 1cm avant le tableau
    y = y_start + espace_1cm

    # Dimensions du tableau (en pixels à 300 DPI)
    col_widths = {
        'designation': mm_to_px(40),  # 100mm
        'quantite': mm_to_px(15),      # 27mm
        'prix_unitaire': mm_to_px(30), # 40mm
        'montant': mm_to_px(30)        # 43mm
    }

    # Calculer la largeur totale du tableau
    table_width = sum(col_widths.values())
    table_x = (width - table_width) // 2  # Centrer le tableau

    # Hauteur des lignes
    header_height = mm_to_px(10)  # 12mm
    row_height = mm_to_px(10)     # 10mm

    # Charger les polices
    font_size = mm_to_px(4)  # 4mm ≈ 12 points
    try:
        font_header = ImageFont.truetype(FONT_REGULAR, font_size) if FONT_REGULAR else ImageFont.load_default()
        font_normal = ImageFont.truetype(FONT_REGULAR, font_size) if FONT_REGULAR else ImageFont.load_default()
    except:
        font_header = ImageFont.load_default()
        font_normal = ImageFont.load_default()


    # === TITRE "BON DE LIVRAISON N°" centré ===
    titre_y = y
    num_bon = f"BL-{num_facture}"

    # Calculer la largeur du titre pour le centrer
    bbox_titre = draw.textbbox((0, 0), f"BON DE LIVRAISON N° {num_bon}", font=font_header)
    titre_width = bbox_titre[2] - bbox_titre[0]
    titre_x = table_x + (table_width - titre_width) // 2

    draw.text((titre_x, titre_y), f"BON DE LIVRAISON N° {num_bon}", font=font_header, fill='#000000')
    y += mm_to_px(8)  # Espace après le titre

    # === EN-TÊTE DU TABLEAU (sans couleur de fond, bordure noire) ===
    header_y = y

    # Dessiner le rectangle de l'en-tête (contour noir)
    draw.rectangle(
        [(table_x, header_y), (table_x + table_width, header_y + header_height)],
        outline='#000000',  # Bordure noire
        fill=None,  # Pas de remplissage
        width=2
    )

    # Dessiner les séparateurs verticaux dans l'en-tête
    x_pos = table_x
    for i, (col_name, col_width) in enumerate(col_widths.items()):
        if i < len(col_widths) - 1:  # Pas de trait après la dernière colonne
            x_pos += col_width
            draw.line([(x_pos, header_y), (x_pos, header_y + header_height)], fill='#000000', width=1)

    # Texte des colonnes (en noir)
    x_offset = table_x
    draw.text((x_offset + mm_to_px(3), header_y + mm_to_px(3)), "Désignation", font=font_header, fill='#000000')
    x_offset += col_widths['designation']

    draw.text((x_offset + mm_to_px(3), header_y + mm_to_px(3)), "Qté", font=font_header, fill='#000000')
    x_offset += col_widths['quantite']

    draw.text((x_offset + mm_to_px(3), header_y + mm_to_px(3)), "Prix U", font=font_header, fill='#000000')
    x_offset += col_widths['prix_unitaire']

    draw.text((x_offset + mm_to_px(3), header_y + mm_to_px(3)), "Montant (Ar)", font=font_header, fill='#000000')

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

        # Dessiner la ligne avec bordure
        draw.rectangle(
            [(table_x, row_y), (table_x + table_width, row_y + row_height)],
            fill=row_fill,
            outline='#dddddd'
        )

        # Dessiner les séparateurs verticaux
        x_pos = table_x
        for j, (col_name, col_width) in enumerate(col_widths.items()):
            if j < len(col_widths) - 1:  # Pas de trait après la dernière colonne
                x_pos += col_width
                draw.line([(x_pos, row_y), (x_pos, row_y + row_height)], fill='#dddddd', width=1)

        # Remplir avec les données si disponibles
        if i < len(produits):
            p = produits[i]
            x_offset = table_x

            # Désignation
            designation = p['nom']
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
        width=2
    )

    # Ligne de bordure à gauche et à droite du tableau
    draw.line([(table_x, header_y), (table_x, bottom_y)], fill='#000000', width=2)
    draw.line([(table_x + table_width, header_y), (table_x + table_width, bottom_y)], fill='#000000', width=2)

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
    draw.line([(padding, y - mm_to_px(2)), (width - padding, y - mm_to_px(2))], fill='#dddddd', width=1)

    # === GAUCHE ===
    left_x = padding
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

    y_apres = max(y + line_height, total_y + 4)

    # === TIRÉS DE FIN ===
    y_sig = y_apres + mm_to_px(5)
    y_fin = y_sig + mm_to_px(30)

    # Ligne pointillée avec des tirets
    for i in range(padding, width - padding, mm_to_px(3)):
        draw.line([(i, y_fin), (i + mm_to_px(2), y_fin)], fill='#999999', width=2)

    # === CACHET/SIGNATURE à droite ===

    sig_width = mm_to_px(80)  # 83mm
    sig_x = width - padding - sig_width

    # Ligne pour signature
    draw.text((sig_x + (sig_width // 2)+40, y_sig + mm_to_px(2)), "Cachet / Signature", font=font_small, fill='#666666', anchor='mt')



    # Texte "Merci de votre confiance!" en dessus du tiré
    draw.text((width//2, y_fin - mm_to_px(5)), "Merci de votre confiance !",
              font=font_small, fill='#666666', anchor='mt')



    return y_fin + mm_to_px(10)

def generer_facture_proforma(client_nom, client_info, produits,
                            date_str, mode_paiement, depot_sortie,
                            total, avance, reste, commande_id,
                            numero_cheque=""):
    """Génère la facture proforma complète (300 DPI) et retourne le chemin du fichier"""

    # Générer automatiquement le nom du fichier
    annee = datetime.now().strftime("%Y")
    mois = datetime.now().strftime("%m")
    filename = f"facture n°_{commande_id} du {mois} {annee}.jpg"
    num_facture = f"{commande_id}/{annee}"

    # Dimensions de l'image (80mm de largeur à 300 DPI)
    width = mm_to_px(120)   # 80mm = 945 pixels à 300 DPI
    height = mm_to_px(200) # 297mm (A4) = 3508 pixels à 300 DPI
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
    tableau_y = generer_tableau_bon_livraison(draw, width, padding, date_y, produits, commande_id, annee)

    # Bas de page
    generer_bas_facture_avec_pointilles(draw, width, padding, tableau_y, total, avance, reste,
                                       mode_paiement, depot_sortie, numero_cheque)

    # Sauvegarder avec haute qualité
    img.save(filename, "JPEG", quality=95, dpi=(DPI, DPI))
    print(f"Facture générée avec succès : {filename} (300 DPI)")

    # Retourner le chemin du fichier (string) et non l'objet Image
    return filename

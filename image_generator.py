# image_generator.py
from PIL import Image, ImageDraw, ImageFont
import os
import datetime
from kivy.utils import platform

# Chemins des polices
if platform == 'android':
    FONT_REGULAR = '/system/fonts/Roboto-Regular.ttf'
    FONT_BOLD = '/system/fonts/Roboto-Bold.ttf'
else:
    # Chemins communs pour d'autres plateformes
    font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        'C:\\Windows\\Fonts\\arial.ttf',
        'C:\\Windows\\Fonts\\segoeui.ttf'
    ]
    FONT_REGULAR = next((p for p in font_paths if os.path.exists(p)), None)
    FONT_BOLD = FONT_REGULAR

def generer_image_facture(commande_id, client_nom, client_info, produits, total, avance, reste, 
                          date_str, mode_paiement, depot_sortie, numero_cheque=""):
    """Génère une facture au format image JPEG"""
    
    # Dimensions pour format NB80 (80mm de large = environ 300px)
    width = 500  # Largeur pour un bon affichage sur mobile
    padding = 15
    line_height = 20
    header_height = 120
    footer_height = 100
    
    # Fonction pour calculer la hauteur nécessaire
    def calculate_height():
        y = header_height + 50  # Espace pour en-tête
        
        # Infos client
        y += 80
        
        # Dépôt de sortie
        y += 30
        
        # Tableau des produits
        y += 30  # En-tête tableau
        for p in produits:
            lines = max(1, (len(p['nom']) // 20) + 1)
            y += line_height * lines
        
        # Totaux
        y += 80
        
        # Mode de paiement
        y += 40
        
        # Pied de page
        y += footer_height
        
        return y + 50
    
    height = calculate_height()
    
    # Créer l'image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Charger les polices
    try:
        if FONT_REGULAR and os.path.exists(FONT_REGULAR):
            font_title = ImageFont.truetype(FONT_REGULAR, 16)
            font_bold = ImageFont.truetype(FONT_BOLD, 14)
            font_normal = ImageFont.truetype(FONT_REGULAR, 11)
            font_small = ImageFont.truetype(FONT_REGULAR, 9)
        else:
            font_title = ImageFont.load_default()
            font_bold = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()
    except:
        font_title = ImageFont.load_default()
        font_bold = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    y = 10
    
    # En-tête
    draw.rectangle([(0, 0), (width, header_height)], fill='#1a237e')
    draw.text((width//2, y), "FACTURE", font=font_title, fill='white', anchor='mt')
    y += 25
    draw.text((width//2, y), f"N° {commande_id}", font=font_normal, fill='white', anchor='mt')
    y += 20
    draw.text((width//2, y), date_str, font=font_small, fill='#cccccc', anchor='mt')
    y += 30
    
    # Informations du client
    draw.rectangle([(padding, y), (width - padding, y + 60)], outline='#ddd', fill='#f5f5f5')
    draw.text((padding + 5, y + 5), "CLIENT", font=font_bold, fill='#333')
    draw.text((padding + 5, y + 22), f"Nom: {client_nom}", font=font_normal, fill='#333')
    draw.text((padding + 5, y + 38), f"Adresse: {client_info.get('adresse', '')}", font=font_small, fill='#666')
    draw.text((padding + 5, y + 52), f"NIF/STAT: {client_info.get('nif', '')} / {client_info.get('stat', '')}", font=font_small, fill='#666')
    y += 70
    
    # Dépôt de sortie
    draw.rectangle([(padding, y), (width - padding, y + 25)], fill='#e3f2fd')
    draw.text((padding + 5, y + 5), f"DÉPÔT DE SORTIE: {depot_sortie}", font=font_bold, fill='#1565c0')
    y += 35
    
    # En-tête du tableau
    draw.rectangle([(padding, y), (width - padding, y + 22)], fill='#1565c0')
    col_widths = [180, 80, 60, 100]
    draw.text((padding + 5, y + 4), "Désignation", font=font_bold, fill='white')
    draw.text((padding + col_widths[0] + 5, y + 4), "P.U", font=font_bold, fill='white')
    draw.text((padding + col_widths[0] + col_widths[1] + 5, y + 4), "Qte", font=font_bold, fill='white')
    draw.text((padding + col_widths[0] + col_widths[1] + col_widths[2] + 5, y + 4), "Montant", font=font_bold, fill='white')
    y += 22
    
    # Lignes des produits
    row_bg = '#ffffff'
    for idx, p in enumerate(produits):
        row_bg = '#f9f9f9' if idx % 2 == 0 else '#ffffff'
        draw.rectangle([(padding, y), (width - padding, y + line_height)], fill=row_bg)
        
        # Gérer le texte sur plusieurs lignes si nécessaire
        nom = p['nom']
        if len(nom) > 20:
            nom = nom[:18] + "..."
        
        draw.text((padding + 5, y + 3), nom, font=font_normal, fill='#333')
        draw.text((padding + col_widths[0] + 5, y + 3), f"{p['prix_unitaire']:,.0f}", font=font_normal, fill='#333')
        draw.text((padding + col_widths[0] + col_widths[1] + 5, y + 3), str(p['quantite']), font=font_normal, fill='#333')
        draw.text((padding + col_widths[0] + col_widths[1] + col_widths[2] + 5, y + 3), f"{p['total']:,.0f}", font=font_normal, fill='#333')
        y += line_height
    
    # Ligne de séparation
    draw.line([(padding, y), (width - padding, y)], fill='#ccc', width=1)
    y += 5
    
    # Totaux
    total_y = y + 30
    draw.text((width - padding - 150, total_y), "TOTAL:", font=font_bold, fill='#333')
    draw.text((width - padding - 10, total_y), f"{total:,.0f} Ar", font=font_bold, fill='#2e7d32', anchor='ra')
    
    draw.text((width - padding - 150, total_y + 22), "Payé:", font=font_normal, fill='#555')
    draw.text((width - padding - 10, total_y + 22), f"{avance:,.0f} Ar", font=font_normal, fill='#1976d2', anchor='ra')
    
    reste_color = '#d32f2f' if reste > 0 else '#2e7d32'
    draw.text((width - padding - 150, total_y + 44), "Reste:", font=font_bold, fill='#555')
    draw.text((width - padding - 10, total_y + 44), f"{reste:,.0f} Ar", font=font_bold, fill=reste_color, anchor='ra')
    
    y += 90
    
    # Mode de paiement
    draw.rectangle([(padding, y), (width - padding, y + 40)], outline='#ddd', fill='#fff8e1')
    mode_text = f"MODE DE PAIEMENT: {mode_paiement}"
    if mode_paiement == "Chèque" and numero_cheque:
        mode_text += f" - N° {numero_cheque}"
    draw.text((width//2, y + 10), mode_text, font=font_bold, fill='#e65100', anchor='mt')
    
    if reste > 0:
        draw.text((width//2, y + 28), "RESTE À PAYER", font=font_small, fill='#d32f2f', anchor='mt')
    
    y += 50
    
    # Pied de page
    footer_y = height - 50
    draw.line([(padding, footer_y - 20), (width - padding, footer_y - 20)], fill='#ccc', width=1)
    draw.text((width//2, footer_y - 10), "Merci de votre confiance !", font=font_small, fill='#999', anchor='mt')
    
    # Sauvegarder l'image
    if not os.path.exists("factures_images"):
        os.makedirs("factures_images")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"factures_images/facture_{commande_id}_{timestamp}.jpg"
    img.save(filename, "JPEG", quality=95)
    
    return filename

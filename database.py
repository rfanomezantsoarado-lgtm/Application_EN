# database.py
import sqlite3
import os
import shutil
from datetime import datetime
import platform

import os
import shutil
from datetime import datetime
from kivy.app import App
from kivy.utils import platform

def get_db_path():
    """Retourne le chemin absolu de la base de données"""
    if platform == 'android':
        from android.storage import app_storage_path
        db_path = os.path.join(app_storage_path(), 'gestion_clients.db')
    else:
        db_path = 'gestion_clients.db'

    print(f"Base de données : {db_path}")
    return db_path

def get_db_connection():
    """Établit et retourne une connexion à la base de données"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialise la base de données avec toutes les tables nécessaires"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Table clients
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                adresse TEXT,
                contact TEXT,
                responsable TEXT
            )
        ''')

        # Table produits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL UNIQUE,
                prix_achat REAL DEFAULT 0,
                prix_vente REAL DEFAULT 0,
                stock INTEGER DEFAULT 0
            )
        ''')

        # Table commandes avec la colonne lieu_paiement
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commandes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_nom TEXT NOT NULL,
                total REAL DEFAULT 0,
                avance REAL DEFAULT 0,
                reste REAL DEFAULT 0,
                mode_paiement TEXT DEFAULT 'Espèce',
                numero_cheque TEXT DEFAULT '',
                date TEXT NOT NULL,
                produits TEXT NOT NULL,
                depot_sortie TEXT DEFAULT 'Dépôt principal',
                lieu_paiement TEXT DEFAULT ''
            )
        ''')

        conn.commit()
        conn.close()
        print("Base de données initialisée avec succès")
        return True

    except Exception as e:
        print(f"Erreur initialisation base: {e}")
        import traceback
        traceback.print_exc()
        return False

# ===================================================
# CLIENTS
# ===================================================

def ajouter_client_db(nom, adresse, contact, responsable):
    """Ajoute un nouveau client dans la base"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (nom, adresse, contact, responsable)
            VALUES (?, ?, ?, ?)
        ''', (nom, adresse, contact, responsable))
        conn.commit()
        client_id = cursor.lastrowid
        conn.close()
        print(f"Client '{nom}' ajouté avec l'ID {client_id}")
        return client_id
    except sqlite3.IntegrityError:
        print(f"Erreur: Le client '{nom}' existe déjà")
        return None
    except Exception as e:
        print(f"Erreur ajout client: {e}")
        return None

def get_all_clients():
    """Récupère tous les clients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nom, adresse, contact, responsable FROM clients ORDER BY nom')
        clients = cursor.fetchall()
        conn.close()
        print(f"Nombre de clients récupérés: {len(clients)}")
        return clients
    except Exception as e:
        print(f"Erreur get_all_clients: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_client_by_id(client_id):
    """Récupère un client par son ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nom, adresse, contact, responsable FROM clients WHERE id = ?', (client_id,))
        client = cursor.fetchone()
        conn.close()
        return client
    except Exception as e:
        print(f"Erreur get_client_by_id: {e}")
        return None

def supprimer_client_db(client_id):
    """Supprime un client par son ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur suppression client: {e}")
        return False

def modifier_client_db(client_id, nom, adresse, contact, responsable):
    """Modifie les informations d'un client"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clients 
            SET nom = ?, adresse = ?, contact = ?, responsable = ?
            WHERE id = ?
        ''', (nom, adresse, contact, responsable, client_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur modification client: {e}")
        return False

def get_clients_count():
    """Retourne le nombre total de clients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM clients')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        print(f"Erreur get_clients_count: {e}")
        return 0

# ===================================================
# PRODUITS
# ===================================================

def ajouter_produit_db(nom, prix_achat, prix_vente):
    """Ajoute un nouveau produit"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO produits (nom, prix_achat, prix_vente)
            VALUES (?, ?, ?)
        ''', (nom, float(prix_achat), float(prix_vente)))
        conn.commit()
        produit_id = cursor.lastrowid
        conn.close()
        print(f"Produit '{nom}' ajouté avec l'ID {produit_id}")
        return produit_id
    except sqlite3.IntegrityError:
        print(f"Erreur: Le produit '{nom}' existe déjà")
        return None
    except Exception as e:
        print(f"Erreur ajout produit: {e}")
        return None

def get_all_produits():
    """Récupère tous les produits"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nom, prix_achat, prix_vente FROM produits ORDER BY nom')
        produits = cursor.fetchall()
        conn.close()
        print(f"Nombre de produits récupérés: {len(produits)}")
        return produits
    except Exception as e:
        print(f"Erreur get_all_produits: {e}")
        import traceback
        traceback.print_exc()
        return []

def supprimer_produit_db(produit_id):
    """Supprime un produit par son ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produits WHERE id = ?', (produit_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur suppression produit: {e}")
        return False

def modifier_produit_db(produit_id, nom, prix_achat, prix_vente):
    """Modifie les informations d'un produit"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE produits 
            SET nom = ?, prix_achat = ?, prix_vente = ?
            WHERE id = ?
        ''', (nom, float(prix_achat), float(prix_vente), produit_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur modification produit: {e}")
        return False

# ===================================================
# COMMANDES
# ===================================================

def ajouter_commande_db(client_nom, produits, total, avance, reste, mode_paiement, numero_cheque, date, depot_sortie="Dépôt principal", lieu_paiement=""):
    """Ajoute une nouvelle commande avec dépôt de sortie et lieu de paiement"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()

        produits_json = json.dumps(produits, ensure_ascii=False)

        cursor.execute('''
            INSERT INTO commandes (client_nom, total, avance, reste, mode_paiement, numero_cheque, date, produits, depot_sortie, lieu_paiement)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_nom, total, avance, reste, mode_paiement, numero_cheque, date, produits_json, depot_sortie, lieu_paiement))

        conn.commit()
        commande_id = cursor.lastrowid
        conn.close()
        print(f"Commande N° {commande_id} ajoutée avec dépôt: {depot_sortie}, lieu: {lieu_paiement}")
        return commande_id
    except Exception as e:
        print(f"Erreur ajout commande: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_all_commandes():
    """Récupère toutes les commandes avec dépôt de sortie et lieu de paiement"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, client_nom, total, avance, reste, mode_paiement, numero_cheque, date, produits, depot_sortie, lieu_paiement 
            FROM commandes ORDER BY id DESC
        ''')
        commandes = cursor.fetchall()
        conn.close()
        return commandes
    except Exception as e:
        print(f"Erreur get_all_commandes: {e}")
        return []

def get_commande_by_id(commande_id):
    """Récupère une commande par son ID avec les produits, dépôt de sortie et lieu de paiement"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, client_nom, total, avance, reste, mode_paiement, numero_cheque, date, produits, depot_sortie, lieu_paiement 
            FROM commandes WHERE id = ?
        ''', (commande_id,))
        row = cursor.fetchone()

        if row:
            commande = {
                'id': row[0],
                'client_nom': row[1],
                'total': row[2],
                'avance': row[3],
                'reste': row[4],
                'mode_paiement': row[5],
                'numero_cheque': row[6] if row[6] else '',
                'date': row[7],
                'produits': json.loads(row[8]) if row[8] else [],
                'depot_sortie': row[9] if row[9] else "Dépôt principal",
                'lieu_paiement': row[10] if len(row) > 10 and row[10] else ''
            }
        else:
            commande = None

        conn.close()
        return commande
    except Exception as e:
        print(f"Erreur get_commande_by_id: {e}")
        return None

def get_commandes_client(client_nom):
    """Récupère toutes les commandes d'un client"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, client_nom, total, avance, reste, date, depot_sortie, lieu_paiement 
            FROM commandes WHERE client_nom = ? ORDER BY id DESC
        ''', (client_nom,))

        commandes = cursor.fetchall()
        conn.close()
        return commandes
    except Exception as e:
        print(f"Erreur get_commandes_client: {e}")
        return []

def payer_reste_db(commande_id, montant, nouveau_reste):
    """Met à jour le reste à payer d'une commande"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT avance FROM commandes WHERE id = ?', (commande_id,))
        row = cursor.fetchone()
        if row:
            nouvelle_avance = row[0] + montant
            cursor.execute('''
                UPDATE commandes 
                SET avance = ?, reste = ?
                WHERE id = ?
            ''', (nouvelle_avance, nouveau_reste, commande_id))
            conn.commit()

        conn.close()
        return True
    except Exception as e:
        print(f"Erreur payer_reste_db: {e}")
        return False

def get_commandes_with_depot():
    """Récupère toutes les commandes avec leur dépôt de sortie et lieu de paiement"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, client_nom, total, avance, reste, mode_paiement, date, depot_sortie, lieu_paiement 
            FROM commandes ORDER BY id DESC
        ''')

        commandes = cursor.fetchall()
        conn.close()
        return commandes
    except Exception as e:
        print(f"Erreur get_commandes_with_depot: {e}")
        return []



import os
import shutil
from datetime import datetime
import platform

def get_backup_dir():
    """Retourne le dossier de sauvegarde adapté à la plateforme"""
    system = platform.system()

    if system == 'Windows':
        # Sur Windows : utilisez le Bureau ou Documents
        backup_dir = os.path.join(os.path.expanduser("~"), "Desktop", "ENApp_Backups")
    elif system == 'Darwin':  # macOS
        backup_dir = os.path.join(os.path.expanduser("~"), "Desktop", "ENApp_Backups")
    else:  # Linux / Android
        backup_dir = "/sdcard/Pictures/BDD"

    # Créer le dossier s'il n'existe pas
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    return backup_dir

def sauvegarder_base_donnees():
    """Sauvegarde la base de données (adapté PC et Android)"""
    try:
        backup_dir = get_backup_dir()

        # Date pour le nom du fichier
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"factures_backup_{date_str}.db"
        backup_path = os.path.join(backup_dir, backup_name)

        # Trouver la base source
        source_db = None
        chemins_possibles = [
            "gestion_clients.db",  # Répertoire courant
            os.path.join(os.getcwd(), "gestion_clients.db"),
            os.path.join(os.path.dirname(__file__), "gestion_clients.db"),
        ]

        for path in chemins_possibles:
            if os.path.exists(path):
                source_db = path
                break

        if source_db:
            shutil.copy2(source_db, backup_path)
            print(f"Sauvegarde créée : {backup_path}")
            print(f"Taille : {os.path.getsize(backup_path):,} octets")
            return backup_path
        else:
            print("Base de données source non trouvée")
            print(f"Recherchée dans : {chemins_possibles}")
            return None

    except Exception as e:
        print(f"Erreur sauvegarde : {e}")
        import traceback
        traceback.print_exc()
        return None

def restaurer_derniere_sauvegarde():
    """Restaure la dernière sauvegarde (adapté PC et Android)"""
    try:
        backup_dir = get_backup_dir()

        if not os.path.exists(backup_dir):
            print("Dossier de sauvegarde inexistant")
            return False

        # Trouver la dernière sauvegarde
        backups = [f for f in os.listdir(backup_dir) if f.startswith("factures_backup_") and f.endswith(".db")]
        if not backups:
            print("Aucune sauvegarde trouvée")
            return False

        # Trier par date (du plus récent au plus ancien)
        backups.sort(reverse=True)
        derniere_sauvegarde = os.path.join(backup_dir, backups[0])

        # Faire une copie de sécurité de la base actuelle avant restauration
        if os.path.exists("gestion_clients.db"):
            temp_backup = f"factures_avant_restauration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2("gestion_clients.db", temp_backup)
            print(f"Base actuelle sauvegardée dans : {temp_backup}")

        # Restaurer
        shutil.copy2(derniere_sauvegarde, "gestion_clients.db")
        print(f"Restauration réussie depuis : {derniere_sauvegarde}")
        print(f"Taille restaurée : {os.path.getsize('gestion_clients.db'):,} octets")
        return True

    except Exception as e:
        print(f"Erreur restauration : {e}")
        return False

def lister_sauvegardes():
    """Liste toutes les sauvegardes disponibles (adapté PC et Android)"""
    try:
        backup_dir = get_backup_dir()

        if not os.path.exists(backup_dir):
            return []

        backups = [f for f in os.listdir(backup_dir) if f.startswith("factures_backup_") and f.endswith(".db")]
        backups.sort(reverse=True)

        resultats = []
        for backup in backups:
            chemin = os.path.join(backup_dir, backup)
            taille = os.path.getsize(chemin)
            date_modif = datetime.fromtimestamp(os.path.getmtime(chemin)).strftime("%d/%m/%Y %H:%M:%S")
            resultats.append({
                'nom': backup,
                'chemin': chemin,
                'taille': taille,
                'date': date_modif
            })

        return resultats

    except Exception as e:
        print(f"Erreur liste sauvegardes : {e}")
        return []


"""
def sauvegarder_base_donnees():
    #Sauvegarde la base de données vers /sdcard/Pictures/BDD/
    try:
        # Dossier de sauvegarde
        backup_dir = "/sdcard/Pictures/BDD"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Date pour le nom du fichier
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"factures_backup_{date_str}.db"
        backup_path = os.path.join(backup_dir, backup_name)

        # Copier la base actuelle
        if os.path.exists("factures.db"):
            shutil.copy2("factures.db", backup_path)
            print(f"Sauvegarde créée : {backup_path}")
            return backup_path
        else:
            print("Base de données source non trouvée")
            return None

    except Exception as e:
        print(f"Erreur sauvegarde : {e}")
        return None

def restaurer_derniere_sauvegarde():
    #Restaure la dernière sauvegarde depuis /sdcard/Pictures/BDD/
    try:
        backup_dir = "/sdcard/Pictures/BDD"
        if not os.path.exists(backup_dir):
            print("Dossier de sauvegarde inexistant")
            return False

        # Trouver la dernière sauvegarde
        backups = [f for f in os.listdir(backup_dir) if f.startswith("factures_backup_") and f.endswith(".db")]
        if not backups:
            print("Aucune sauvegarde trouvée")
            return False

        # Trier par date (du plus récent au plus ancien)
        backups.sort(reverse=True)
        derniere_sauvegarde = os.path.join(backup_dir, backups[0])

        # Faire une copie de sécurité de la base actuelle avant restauration
        if os.path.exists("factures.db"):
            temp_backup = f"factures_avant_restauration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2("factures.db", temp_backup)
            print(f"Base actuelle sauvegardée dans : {temp_backup}")

        # Restaurer
        shutil.copy2(derniere_sauvegarde, "factures.db")
        print(f"Restauration réussie depuis : {derniere_sauvegarde}")
        return True

    except Exception as e:
        print(f"Erreur restauration : {e}")
        return False

def lister_sauvegardes():
    #Liste toutes les sauvegardes disponibles
    try:
        backup_dir = "/sdcard/ENbackup"
        if not os.path.exists(backup_dir):
            return []

        backups = [f for f in os.listdir(backup_dir) if f.startswith("factures_backup_") and f.endswith(".db")]
        backups.sort(reverse=True)

        resultats = []
        for backup in backups:
            chemin = os.path.join(backup_dir, backup)
            taille = os.path.getsize(chemin)
            date_modif = datetime.fromtimestamp(os.path.getmtime(chemin)).strftime("%d/%m/%Y %H:%M:%S")
            resultats.append({
                'nom': backup,
                'chemin': chemin,
                'taille': taille,
                'date': date_modif
            })

        return resultats

    except Exception as e:
        print(f"Erreur liste sauvegardes : {e}")
        return []
"""
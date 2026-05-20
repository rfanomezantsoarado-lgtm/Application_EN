# database.py
import sqlite3
import os
from kivy.app import App
from kivy.utils import platform

def get_db_path():
    """Retourne le chemin absolu de la base de données"""
    if platform == 'android':
        # Sur Android, utiliser le répertoire de l'application
        from android.storage import app_storage_path
        db_path = os.path.join(app_storage_path(), 'gestion_clients.db')
    else:
        # Sur PC, utiliser le répertoire courant
        db_path = 'gestion_clients.db'
    
    print(f"Base de données : {db_path}")
    return db_path

def get_db_connection():
    """Établit et retourne une connexion à la base de données"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
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
                stat TEXT,
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
        
        # Vérifier si la colonne depot_sortie existe dans la table commandes
        cursor.execute("PRAGMA table_info(commandes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Table commandes avec vérification de l'existence des colonnes
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
                produits TEXT NOT NULL
            )
        ''')
        
        # Ajouter la colonne depot_sortie si elle n'existe pas
        if 'depot_sortie' not in columns:
            try:
                cursor.execute('ALTER TABLE commandes ADD COLUMN depot_sortie TEXT DEFAULT "Dépôt principal"')
                print("Colonne depot_sortie ajoutée avec succès")
            except Exception as e:
                print(f"Erreur lors de l'ajout de depot_sortie: {e}")
        
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

def ajouter_client_db(nom, adresse, stat, contact, responsable):
    """Ajoute un nouveau client dans la base"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clients (nom, adresse, stat, contact, responsable)
            VALUES (?, ?, ?, ?, ?)
        ''', (nom, adresse, stat, contact, responsable))
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
        cursor.execute('SELECT id, nom, adresse, stat, contact, responsable FROM clients ORDER BY nom')
        clients = cursor.fetchall()
        conn.close()
        print(f"Nombre de clients récupérés: {len(clients)}")
        return clients
    except Exception as e:
        print(f"Erreur get_all_clients: {e}")
        import traceback
        traceback.print_exc()
        return []

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

def modifier_client_db(client_id, nom, adresse, stat, contact, responsable):
    """Modifie les informations d'un client"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clients 
            SET nom = ?, adresse = ?, stat = ?, contact = ?, responsable = ?
            WHERE id = ?
        ''', (nom, adresse, stat, contact, responsable, client_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur modification client: {e}")
        return False

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

def ajouter_commande_db(client_nom, produits, total, avance, reste, mode_paiement, numero_cheque, date, depot_sortie="Dépôt principal"):
    """Ajoute une nouvelle commande avec dépôt de sortie"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convertir la liste des produits en JSON
        produits_json = json.dumps(produits, ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO commandes (client_nom, total, avance, reste, mode_paiement, numero_cheque, date, produits, depot_sortie)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (client_nom, total, avance, reste, mode_paiement, numero_cheque, date, produits_json, depot_sortie))
        
        conn.commit()
        commande_id = cursor.lastrowid
        conn.close()
        print(f"Commande N° {commande_id} ajoutée avec dépôt: {depot_sortie}")
        return commande_id
    except Exception as e:
        print(f"Erreur ajout commande: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_all_commandes():
    """Récupère toutes les commandes avec dépôt de sortie"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier si la colonne depot_sortie existe
        cursor.execute("PRAGMA table_info(commandes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'depot_sortie' in columns:
            cursor.execute('SELECT id, client_nom, total, avance, reste, mode_paiement, date, produits, depot_sortie FROM commandes ORDER BY id DESC')
        else:
            cursor.execute('SELECT id, client_nom, total, avance, reste, mode_paiement, date, produits FROM commandes ORDER BY id DESC')
        
        commandes = cursor.fetchall()
        conn.close()
        return commandes
    except Exception as e:
        print(f"Erreur get_all_commandes: {e}")
        return []

def get_commande_by_id(commande_id):
    """Récupère une commande par son ID avec les produits et le dépôt de sortie"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier si la colonne depot_sortie existe
        cursor.execute("PRAGMA table_info(commandes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'depot_sortie' in columns:
            cursor.execute('SELECT id, client_nom, total, avance, reste, mode_paiement, numero_cheque, date, produits, depot_sortie FROM commandes WHERE id = ?', (commande_id,))
            row = cursor.fetchone()
            
            if row:
                commande = {
                    'id': row[0],
                    'client_nom': row[1],
                    'total': row[2],
                    'avance': row[3],
                    'reste': row[4],
                    'mode_paiement': row[5],
                    'numero_cheque': row[6] if len(row) > 6 else '',
                    'date': row[7] if len(row) > 7 else '',
                    'produits': json.loads(row[8]) if len(row) > 8 and row[8] else [],
                    'depot_sortie': row[9] if len(row) > 9 and row[9] else "Dépôt principal"
                }
            else:
                commande = None
        else:
            cursor.execute('SELECT id, client_nom, total, avance, reste, mode_paiement, numero_cheque, date, produits FROM commandes WHERE id = ?', (commande_id,))
            row = cursor.fetchone()
            
            if row:
                commande = {
                    'id': row[0],
                    'client_nom': row[1],
                    'total': row[2],
                    'avance': row[3],
                    'reste': row[4],
                    'mode_paiement': row[5],
                    'numero_cheque': row[6] if len(row) > 6 else '',
                    'date': row[7] if len(row) > 7 else '',
                    'produits': json.loads(row[8]) if len(row) > 8 and row[8] else [],
                    'depot_sortie': "Dépôt principal"
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
        
        # Vérifier si la colonne depot_sortie existe
        cursor.execute("PRAGMA table_info(commandes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'depot_sortie' in columns:
            cursor.execute('SELECT id, client_nom, total, avance, reste, date, depot_sortie FROM commandes WHERE client_nom = ? ORDER BY id DESC', (client_nom,))
        else:
            cursor.execute('SELECT id, client_nom, total, avance, reste, date FROM commandes WHERE client_nom = ? ORDER BY id DESC', (client_nom,))
        
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
        
        # Récupérer l'avance actuelle
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
    """Récupère toutes les commandes avec leur dépôt de sortie (fonction utilitaire)"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier si la colonne depot_sortie existe
        cursor.execute("PRAGMA table_info(commandes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'depot_sortie' in columns:
            cursor.execute('SELECT id, client_nom, total, avance, reste, mode_paiement, date, depot_sortie FROM commandes ORDER BY id DESC')
        else:
            cursor.execute('SELECT id, client_nom, total, avance, reste, mode_paiement, date FROM commandes ORDER BY id DESC')
        
        commandes = cursor.fetchall()
        conn.close()
        return commandes
    except Exception as e:
        print(f"Erreur get_commandes_with_depot: {e}")
        return []

def mise_a_jour_base_depot_sortie():
    """Fonction utilitaire pour mettre à jour la base existante avec la colonne depot_sortie"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(commandes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'depot_sortie' not in columns:
            cursor.execute('ALTER TABLE commandes ADD COLUMN depot_sortie TEXT DEFAULT "Dépôt principal"')
            conn.commit()
            print("Colonne depot_sortie ajoutée avec succès")
        else:
            print("La colonne depot_sortie existe déjà")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur mise à jour base: {e}")
        return False

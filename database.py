# database.py
import sqlite3
import os
import shutil
from datetime import datetime
import platform

# ===================================================
# GESTION DU CHEMIN DE BASE DE DONNEES
# ===================================================

def get_db_path():
    """Retourne le chemin absolu de la base de données"""
    if platform == 'android':
        # Priorité au dossier Pictures pour Android NB80
        pictures_dir = "/sdcard/Pictures/BDD"

        # Créer le dossier s'il n'existe pas
        if not os.path.exists(pictures_dir):
            try:
                os.makedirs(pictures_dir)
                print(f"Dossier créé : {pictures_dir}")
            except Exception as e:
                print(f"Erreur création dossier Pictures: {e}")
                # Fallback vers app_storage_path
                from android.storage import app_storage_path
                pictures_dir = app_storage_path()

        db_path = os.path.join(pictures_dir, 'gestion_clients.db')

        # Vérifier si la base existe déjà à l'ancien emplacement
        from android.storage import app_storage_path
        old_db_path = os.path.join(app_storage_path(), 'gestion_clients.db')
        if os.path.exists(old_db_path) and not os.path.exists(db_path):
            try:
                # Copier l'ancienne base vers le nouvel emplacement
                shutil.copy2(old_db_path, db_path)
                print(f"Base existante copiée de {old_db_path} vers {db_path}")
            except Exception as e:
                print(f"Erreur copie base existante: {e}")
    else:
        # Pour PC/Mac/Linux
        db_path = 'gestion_clients.db'

    print(f"Base de données utilisée : {db_path}")
    return db_path

def migrate_database_if_needed():
    """Migre la base de données si nécessaire (ancien emplacement -> nouvel emplacement)"""
    if platform == 'android':
        from android.storage import app_storage_path
        old_path = os.path.join(app_storage_path(), 'gestion_clients.db')
        new_path = get_db_path()

        # Si l'ancienne base existe et pas la nouvelle, copier
        if os.path.exists(old_path) and not os.path.exists(new_path):
            try:
                # Créer le dossier destination si nécessaire
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                shutil.copy2(old_path, new_path)
                print(f"Migration réussie : {old_path} -> {new_path}")
                return True
            except Exception as e:
                print(f"Erreur migration : {e}")
                return False
    return False

def get_db_connection():
    """Établit et retourne une connexion à la base de données"""
    # Vérifier et migrer si nécessaire
    migrate_database_if_needed()

    db_path = get_db_path()

    # Créer le dossier parent s'il n'existe pas
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir)
            print(f"Dossier créé : {db_dir}")
        except Exception as e:
            print(f"Erreur création dossier: {e}")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print(f"Connexion établie : {db_path}")
        return conn
    except Exception as e:
        print(f"Erreur connexion DB : {e}")
        raise

def verify_database_location():
    """Vérifie et affiche l'emplacement réel de la base de données"""
    db_path = get_db_path()
    exists = os.path.exists(db_path)
    size = os.path.getsize(db_path) if exists else 0

    print(f"\nInformations base de données :")
    print(f"  - Chemin : {db_path}")
    print(f"  - Existe : {'Oui' if exists else 'Non'}")
    print(f"  - Taille : {size:,} octets" if exists else "  - Taille : N/A")

    if platform == 'android':
        # Vérifier les permissions d'écriture
        pictures_dir = "/sdcard/Pictures/BDD"
        if os.path.exists(pictures_dir):
            test_file = os.path.join(pictures_dir, "test_write.txt")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
                print("  - Permissions écriture : OK")
            except:
                print("  - Permissions écriture : ERR")

    return db_path, exists

# ===================================================
# INITIALISATION
# ===================================================

def init_database():
    """Initialise la base de données avec toutes les tables nécessaires"""
    try:
        # Vérifier l'emplacement
        verify_database_location()

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

        # Vérification finale
        db_path = get_db_path()
        if os.path.exists(db_path):
            print(f"Base créée avec succès : {db_path}")
            print(f"   Taille : {os.path.getsize(db_path):,} octets")

        return True

    except Exception as e:
        print(f"Erreur initialisation base: {e}")
        import traceback
        traceback.print_exc()
        return False

# ===================================================
# SAUVEGARDE CORRIGEE POUR ANDROID NB80
# ===================================================

def get_backup_dir():
    """Retourne le dossier de sauvegarde adapté à la plateforme avec recherche multi-emplacements"""
    if platform == 'android':
        # Liste des chemins possibles pour les sauvegardes
        possible_backup_paths = [
            os.path.join('/storage/emulated/0', 'Pictures', 'BDD_Backups'),
            os.path.join('/sdcard', 'Pictures', 'BDD_Backups'),
            os.path.join(os.environ.get('EXTERNAL_STORAGE', '/storage/emulated/0'), 'Pictures', 'BDD_Backups'),
            os.path.join('/storage/emulated/0', 'Download', 'BDD_Backups'),
            os.path.join('/sdcard', 'Download', 'BDD_Backups'),
        ]

        backup_dir = None
        for path in possible_backup_paths:
            try:
                if path:
                    # Créer le dossier s'il n'existe pas
                    if not os.path.exists(path):
                        os.makedirs(path, exist_ok=True)
                    # Tester l'écriture
                    test_file = os.path.join(path, "test_write.txt")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    backup_dir = path
                    print(f"Dossier sauvegarde utilisable : {backup_dir}")
                    break
            except Exception as e:
                print(f"Chemin sauvegarde non utilisable {path}: {e}")
                continue

        if not backup_dir:
            # Fallback vers le dossier de l'application
            try:
                from android.storage import app_storage_path
                backup_dir = os.path.join(app_storage_path(), 'Backups')
                os.makedirs(backup_dir, exist_ok=True)
                print(f"Fallback sauvegarde : {backup_dir}")
            except:
                backup_dir = "/sdcard/Pictures/BDD_Backups"
                os.makedirs(backup_dir, exist_ok=True)
    else:
        # Pour PC/Mac/Linux
        if platform.system() == 'Windows':
            backup_dir = os.path.join(os.path.expanduser("~"), "Desktop", "ENApp_Backups")
        else:
            backup_dir = os.path.join(os.path.expanduser("~"), "Documents", "ENApp_Backups")
        os.makedirs(backup_dir, exist_ok=True)

    print(f"Dossier sauvegarde : {backup_dir}")
    return backup_dir

def sauvegarder_base_donnees():
    """Sauvegarde la base de données avec recherche multi-emplacements"""
    try:
        backup_dir = get_backup_dir()

        # Date pour le nom du fichier
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"factures_backup_{date_str}.db"
        backup_path = os.path.join(backup_dir, backup_name)

        # Obtenir le chemin de la base source
        source_db = get_db_path()

        # Liste des emplacements possibles pour la source
        possible_sources = [source_db]

        # Ajouter les emplacements alternatifs
        if platform == 'android':
            possible_sources.extend([
                os.path.join('/storage/emulated/0', 'Pictures', 'BDD', 'gestion_clients.db'),
                os.path.join('/sdcard', 'Pictures', 'BDD', 'gestion_clients.db'),
                os.path.join('/storage/emulated/0', 'Pictures', 'gestion_clients.db'),
                os.path.join('/sdcard', 'Pictures', 'gestion_clients.db'),
            ])
            try:
                from android.storage import app_storage_path
                possible_sources.append(os.path.join(app_storage_path(), 'gestion_clients.db'))
            except:
                pass

        # Chercher la base source
        source_found = None
        for path in possible_sources:
            if path and os.path.exists(path):
                source_found = path
                print(f"Base source trouvée : {source_found}")
                break

        if source_found and os.path.exists(source_found):
            # Créer le dossier de sauvegarde si nécessaire
            os.makedirs(backup_dir, exist_ok=True)

            # Copier la base
            shutil.copy2(source_found, backup_path)

            # Vérifier la copie
            if os.path.exists(backup_path):
                taille = os.path.getsize(backup_path)
                print(f"Sauvegarde créée : {backup_path}")
                print(f"   Taille : {taille:,} octets")
                print(f"   Date : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

                # Sur Android, ajouter un fichier .nomedia
                if platform == 'android':
                    try:
                        nomedia_path = os.path.join(backup_dir, ".nomedia")
                        if not os.path.exists(nomedia_path):
                            with open(nomedia_path, 'w') as f:
                                f.write("")
                    except:
                        pass

                return backup_path
            else:
                print("Echec de création de la sauvegarde")
                return None
        else:
            print("Base de données source non trouvée")
            print("Recherche effectuée dans :")
            for path in possible_sources:
                if path:
                    print(f"  - {path}")
            return None

    except Exception as e:
        print(f"Erreur sauvegarde : {e}")
        import traceback
        traceback.print_exc()
        return None

def restaurer_derniere_sauvegarde():
    """Restaure la dernière sauvegarde avec recherche multi-emplacements"""
    try:
        backup_dir = get_backup_dir()

        if not os.path.exists(backup_dir):
            print("Dossier de sauvegarde inexistant")
            return False

        # Trouver toutes les sauvegardes
        backups = []
        try:
            for f in os.listdir(backup_dir):
                if f.startswith("factures_backup_") and f.endswith(".db"):
                    chemin = os.path.join(backup_dir, f)
                    backups.append((chemin, os.path.getmtime(chemin)))
        except Exception as e:
            print(f"Erreur lecture dossier: {e}")
            return False

        if not backups:
            print("Aucune sauvegarde trouvée")
            return False

        # Trier par date (plus récente d'abord)
        backups.sort(key=lambda x: x[1], reverse=True)
        derniere_sauvegarde = backups[0][0]

        # Obtenir le chemin de la base actuelle
        current_db = get_db_path()

        # Faire une copie de sécurité de la base actuelle avant restauration
        if os.path.exists(current_db):
            temp_backup = f"factures_avant_restauration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(current_db, temp_backup)
            print(f"Base actuelle sauvegardée dans : {temp_backup}")

        # Créer le dossier parent si nécessaire
        os.makedirs(os.path.dirname(current_db), exist_ok=True)

        # Restaurer
        shutil.copy2(derniere_sauvegarde, current_db)
        print(f"Restauration réussie depuis : {derniere_sauvegarde}")
        print(f"   Taille restaurée : {os.path.getsize(current_db):,} octets")
        return True

    except Exception as e:
        print(f"Erreur restauration : {e}")
        import traceback
        traceback.print_exc()
        return False

def lister_sauvegardes():
    """Liste toutes les sauvegardes disponibles avec leurs informations"""
    try:
        backup_dir = get_backup_dir()

        if not os.path.exists(backup_dir):
            return []

        backups = []
        try:
            for f in os.listdir(backup_dir):
                if f.startswith("factures_backup_") and f.endswith(".db"):
                    chemin = os.path.join(backup_dir, f)
                    try:
                        taille = os.path.getsize(chemin)
                        date_modif = datetime.fromtimestamp(os.path.getmtime(chemin)).strftime("%d/%m/%Y %H:%M:%S")
                        backups.append({
                            'nom': f,
                            'chemin': chemin,
                            'taille': taille,
                            'date': date_modif
                        })
                    except Exception as e:
                        print(f"Erreur lecture fichier {f}: {e}")
                        continue
        except Exception as e:
            print(f"Erreur lecture dossier: {e}")
            return []

        # Trier par date (plus récente d'abord)
        backups.sort(key=lambda x: x['date'], reverse=True)
        return backups

    except Exception as e:
        print(f"Erreur liste sauvegardes : {e}")
        return []

def supprimer_sauvegarde(chemin):
    """Supprime une sauvegarde spécifique"""
    try:
        if os.path.exists(chemin):
            os.remove(chemin)
            print(f"Sauvegarde supprimée : {chemin}")
            return True
        else:
            print(f"Sauvegarde introuvable : {chemin}")
            return False
    except Exception as e:
        print(f"Erreur suppression : {e}")
        return False

# ===================================================
# FONCTIONS UTILITAIRES
# ===================================================

def get_database_info():
    """Retourne des informations détaillées sur la base de données"""
    db_path = get_db_path()
    exists = os.path.exists(db_path)

    info = {
        'path': db_path,
        'exists': exists,
        'size': os.path.getsize(db_path) if exists else 0,
        'directory': os.path.dirname(db_path),
        'writable': False
    }

    if exists:
        # Vérifier si le fichier est accessible en écriture
        try:
            test_file = db_path + ".test"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            info['writable'] = True
        except:
            info['writable'] = False

    return info

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

def update_commande_lieu_paiement(commande_id, lieu_paiement):
    """Met à jour le lieu de paiement d'une commande"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE commandes 
            SET lieu_paiement = ?
            WHERE id = ?
        ''', (lieu_paiement, commande_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur update lieu_paiement: {e}")
        return False
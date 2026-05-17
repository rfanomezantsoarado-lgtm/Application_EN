# ===================================================
# IMPORTATION DES BIBLIOTHEQUES
# ===================================================

import os
import sqlite3
import json
from kivy.utils import platform
# ===================================================
# CONFIGURATION DU CHEMIN DE LA BASE DE DONNEES
# ===================================================

if platform == "android":

    try:
        from jnius import autoclass

        PythonActivity = autoclass(
            'org.kivy.android.PythonActivity'
        )

        context = PythonActivity.mActivity

        files_dir = context.getFilesDir()

        DB_PATH = os.path.join(
            files_dir.getAbsolutePath(),
            "gestion_clients.db"
        )

        print(f"Base Android : {DB_PATH}")

    except Exception as e:

        print(f"Erreur Android : {e}")

        DB_PATH = "gestion_clients.db"

else:

    DB_PATH = "gestion_clients.db"

    print(f"Base locale : {DB_PATH}")

# ===================================================
# FONCTION CONNEXION SQLITE
# ===================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)

    # Amélioration stabilité Android
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode=WAL")

    return conn


# ===================================================
# INITIALISATION BASE DE DONNEES
# ===================================================

def init_database():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            # =========================
            # TABLE CLIENTS
            # =========================

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    adresse TEXT,
                    nif TEXT,
                    stat TEXT,
                    contact TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # =========================
            # TABLE PRODUITS
            # =========================

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prix_achat TEXT,
                    prix_vente TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # =========================
            # TABLE COMMANDES
            # =========================

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commandes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_nom TEXT NOT NULL,
                    produits TEXT,
                    total REAL DEFAULT 0,
                    avance REAL DEFAULT 0,
                    reste REAL DEFAULT 0,
                    mode_paiement TEXT DEFAULT 'Espece',
                    numero_cheque TEXT,
                    date_commande TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

        # Migrations
        migrer_ajouter_colonne_numero_cheque()
        ajouter_colonne_mode_paiement()

        print("Base de données initialisée avec succès")

        return True

    except Exception as e:
        print(f"Erreur init_database : {e}")

        return False


# ===================================================
# MIGRATIONS
# ===================================================

def ajouter_colonne_mode_paiement():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(commandes)")
            columns = [col[1] for col in cursor.fetchall()]

            if "mode_paiement" not in columns:

                cursor.execute("""
                    ALTER TABLE commandes
                    ADD COLUMN mode_paiement TEXT DEFAULT 'Espece'
                """)

                conn.commit()

                print("Colonne mode_paiement ajoutée")

            cursor.execute("""
                UPDATE commandes
                SET mode_paiement = 'Espece'
                WHERE mode_paiement IS NULL
            """)

            conn.commit()

        return True

    except Exception as e:
        print(f"Erreur migration mode_paiement : {e}")

        return False


def migrer_ajouter_colonne_numero_cheque():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(commandes)")
            columns = [col[1] for col in cursor.fetchall()]

            if "numero_cheque" not in columns:

                cursor.execute("""
                    ALTER TABLE commandes
                    ADD COLUMN numero_cheque TEXT
                """)

                conn.commit()

                print("Colonne numero_cheque ajoutée")

        return True

    except Exception as e:
        print(f"Erreur migration numero_cheque : {e}")

        return False


# ===================================================
# CLIENTS
# ===================================================

def ajouter_client_db(nom, adresse, nif, stat, contact):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO clients (
                    nom,
                    adresse,
                    nif,
                    stat,
                    contact
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                nom,
                adresse,
                nif,
                stat,
                contact
            ))

            conn.commit()

            return cursor.lastrowid

    except Exception as e:
        print(f"Erreur ajout client : {e}")

        return None
        
def get_all_clients():
    """Récupère tous les clients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY nom")
        clients = cursor.fetchall()
        conn.close()
        
        # Debug
        print(f"SQL get_all_clients - Nombre: {len(clients)}")
        for client in clients:
            print(f"Client SQL: {client}")
            
        return clients
    except Exception as e:
        print(f"Erreur get_all_clients: {e}")
        return []
def supprimer_client_db(client_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM clients
                WHERE id = ?
            """, (client_id,))

            conn.commit()

        return True

    except Exception as e:
        print(f"Erreur suppression client : {e}")

        return False


def get_clients_count():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM clients")

            return cursor.fetchone()[0]

    except Exception as e:
        print(f"Erreur count clients : {e}")

        return 0


# ===================================================
# PRODUITS
# ===================================================

def ajouter_produit_db(nom, prix_achat, prix_vente):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO produits (
                    nom,
                    prix_achat,
                    prix_vente
                )
                VALUES (?, ?, ?)
            """, (
                nom,
                float(prix_achat),
                float(prix_vente)
            ))

            conn.commit()

            return cursor.lastrowid

    except Exception as e:
        print(f"Erreur ajout produit : {e}")

        return None
def modifier_produit_db(
    produit_id,
    nom,
    prix_achat,
    prix_vente
):
    try:
        with get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                UPDATE produits
                SET
                    nom = ?,
                    prix_achat = ?,
                    prix_vente = ?
                WHERE id = ?
            """, (
                nom,
                prix_achat,
                prix_vente,
                produit_id
            ))

            conn.commit()

        return True

    except Exception as e:
        print(f"Erreur modification produit : {e}")

        return False

def get_all_produits():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    nom,
                    prix_achat,
                    prix_vente
                FROM produits
                ORDER BY id DESC
            """)

            return cursor.fetchall()

    except Exception as e:
        print(f"Erreur récupération produits : {e}")

        return []


def supprimer_produit_db(produit_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM produits
                WHERE id = ?
            """, (produit_id,))

            conn.commit()

        return True

    except Exception as e:
        print(f"Erreur suppression produit : {e}")

        return False


def get_produits_count():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM produits")

            return cursor.fetchone()[0]

    except Exception as e:
        print(f"Erreur count produits : {e}")

        return 0


# ===================================================
# COMMANDES
# ===================================================

def ajouter_commande_db(
    client_nom=None,
    produits=None,
    total=0,
    avance=0,
    reste=0,
    mode_paiement="Espece",
    numero_cheque="",
    date=""
):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            produits_json = json.dumps(
                produits if produits else [],
                ensure_ascii=False
            )

            cursor.execute("""
                INSERT INTO commandes (
                    client_nom,
                    produits,
                    total,
                    avance,
                    reste,
                    mode_paiement,
                    numero_cheque,
                    date_commande
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                client_nom,
                produits_json,
                float(total),
                float(avance),
                float(reste),
                mode_paiement,
                numero_cheque,
                date
            ))

            conn.commit()

            return cursor.lastrowid

    except Exception as e:
        print(f"Erreur ajout commande : {e}")

        return None


def get_all_commandes():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    client_nom,
                    total,
                    avance,
                    reste,
                    mode_paiement,
                    numero_cheque,
                    date_commande
                FROM commandes
                ORDER BY id DESC
            """)

            return cursor.fetchall()

    except Exception as e:
        print(f"Erreur récupération commandes : {e}")

        return []


def get_commandes_client(client_nom):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    client_nom,
                    total,
                    avance,
                    reste,
                    mode_paiement,
                    numero_cheque,
                    date_commande
                FROM commandes
                WHERE client_nom = ?
                ORDER BY id DESC
            """, (client_nom,))

            return cursor.fetchall()

    except Exception as e:
        print(f"Erreur commandes client : {e}")

        return []


def get_commande_by_id(commande_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    client_nom,
                    produits,
                    total,
                    avance,
                    reste,
                    mode_paiement,
                    numero_cheque,
                    date_commande
                FROM commandes
                WHERE id = ?
            """, (commande_id,))

            commande = cursor.fetchone()

            if commande:

                produits = json.loads(
                    commande[2]
                ) if commande[2] else []

                return {
                    "id": commande[0],
                    "client_nom": commande[1],
                    "produits": produits,
                    "total": commande[3],
                    "avance": commande[4],
                    "reste": commande[5],
                    "mode_paiement": commande[6],
                    "numero_cheque": commande[7],
                    "date": commande[8]
                }

            return None

    except Exception as e:
        print(f"Erreur get commande : {e}")

        return None


def supprimer_commande_db(commande_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM commandes
                WHERE id = ?
            """, (commande_id,))

            conn.commit()

        return True

    except Exception as e:
        print(f"Erreur suppression commande : {e}")

        return False


def payer_reste_db(commande_id, montant_paye, nouveau_reste):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE commandes
                SET
                    avance = avance + ?,
                    reste = ?
                WHERE id = ?
            """, (
                float(montant_paye),
                float(nouveau_reste),
                commande_id
            ))

            conn.commit()

        return True

    except Exception as e:
        print(f"Erreur payer_reste_db : {e}")

        return False


def get_commandes_count():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM commandes
            """)

            return cursor.fetchone()[0]

    except Exception as e:
        print(f"Erreur count commandes : {e}")

        return 0


def get_commandes_count_by_client(client_nom):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*)
                FROM commandes
                WHERE client_nom = ?
            """, (client_nom,))

            return cursor.fetchone()[0]

    except Exception as e:
        print(f"Erreur count commandes client : {e}")

        return 0

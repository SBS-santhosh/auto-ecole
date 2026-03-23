# 🚗 AutoÉcole Pro

Application web de gestion complète pour une auto-école (BTS SIO 2).

## 🛠️ Stack Technique

- **Backend** : [Django 5.0](https://www.djangoproject.com/) (Python 3.10+)
- **Frontend** : [Bootstrap 5](https://getbootstrap.com/), [Crispy Forms](https://django-crispy-forms.readthedocs.io/)
- **Base de données** : [SQLite](https://www.sqlite.org/) (par défaut) ou [MySQL](https://www.mysql.com/)
- **Design** : Responsive, moderne, avec icônes FontAwesome.

## 🔑 Comptes de Démonstration

| Rôle | Utilisateur | Mot de Passe |
|------|-------------|--------------|
| **Administrateur** | `admin` | `admin123` |
| **Moniteur** | `m.dupont` | `moniteur123` |
| **Élève** | `l.petit` | `eleve123` |

---

## 📖 User Stories (Format Court)

### 🎓 Espace Élève
- **Inscription** : Créer un compte et gérer son profil (photo, tel).
- **Réservation** : Choisir et réserver des créneaux de conduite en ligne.
- **Suivi** : Consulter son nombre d'heures effectuées et son historique.
- **Paiements** : Suivre ses règlements et soldes.
- **Code** : S'entraîner avec des quiz interactifs sur le code de la route.

### 🏎️ Espace Moniteur
- **Planning** : Gérer son emploi du temps hebdomadaire.
- **Leçons** : Créer des créneaux disponibles et valider les leçons effectuées.
- **Évaluation** : Saisir des notes pédagogiques pour chaque élève.
- **Dossiers** : Consulter le suivi complet de ses élèves.

### ⚙️ Espace Administration
- **Utilisateurs** : Gestion complète (CRUD) des élèves et moniteurs.
- **Flotte** : Gérer le parc automobile (véhicules actifs/inactifs).
- **Leçons** : Superviser l'ensemble des créneaux et réservations.
- **Finances** : Suivre les revenus et enregistrer les paiements.
- **Stats & Export** : Tableau de bord global et export CSV des données.

---

## 📦 Dépendances

Le projet nécessite les bibliothèques suivantes :
- `django` : Framework web principal.
- `django-crispy-forms` : Pour des formulaires élégants.
- `crispy-bootstrap5` : Intégration Bootstrap 5 pour Crispy Forms.
- `pillow` : Gestion des images (photos de profil, etc.).

---

## 🚀 Installation & Lancement

Suivez ces étapes pour installer et exécuter le projet sur votre PC (Windows, macOS ou Linux).

### 1. Prérequis
- **Python 3.10** ou plus récent installé sur votre machine.
- **Git** (optionnel, pour cloner le projet).

### 2. Configuration de l'environnement
Il est fortement recommandé d'utiliser un environnement virtuel :

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur macOS/Linux :
source venv/bin/activate
# Sur Windows :
.\venv\Scripts\activate
```

### 3. Installation des dépendances
Une fois l'environnement activé, installez les packages nécessaires :

```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données
Appliquez les migrations pour créer la structure de la base de données SQLite :

```bash
python manage.py migrate
```

### 5. Données de démonstration (Seed)
Pour remplir la base de données avec des utilisateurs et des données de test :

```bash
python seed_data.py
```

### 6. Lancer le serveur
Démarrez le serveur de développement local :

```bash
python manage.py runserver
```

Accès local : [http://localhost:8000/](http://localhost:8000/)
# auto-ecole

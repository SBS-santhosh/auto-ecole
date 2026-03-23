"""
Script de peuplement de la base de données avec des données de démonstration.
Usage: python manage.py shell < seed_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'autoecole_pro.settings')
django.setup()

from django.contrib.auth.models import User
from ecole.models import Profile, Vehicle, Lesson, Booking, Payment, QuizQuestion
from django.utils import timezone
from datetime import timedelta
import random

print("🚗 Peuplement de la base AutoÉcole Pro...")

# ─── Créer le superuser admin ────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser('admin', 'admin@autoecole.fr', 'admin123')
    Profile.objects.create(user=admin_user, role='admin', telephone='01 00 00 00 00')
    print("✅ Admin créé (admin / admin123)")

# ─── Créer des moniteurs ─────────────────────────────────────────
moniteurs_data = [
    ('m.dupont', 'Marc', 'Dupont', 'marc.dupont@autoecole.fr', '06 12 34 56 78', 'P-2024-001'),
    ('s.martin', 'Sophie', 'Martin', 'sophie.martin@autoecole.fr', '06 23 45 67 89', 'P-2024-002'),
    ('j.bernard', 'Jean', 'Bernard', 'jean.bernard@autoecole.fr', '06 34 56 78 90', 'P-2024-003'),
]

moniteurs = []
for uname, first, last, email, tel, permis in moniteurs_data:
    user, created = User.objects.get_or_create(username=uname, defaults={
        'first_name': first, 'last_name': last, 'email': email
    })
    if created:
        user.set_password('moniteur123')
        user.save()
        Profile.objects.create(user=user, role='moniteur', telephone=tel, numero_permis=permis)
        print(f"  ✅ Moniteur {first} {last} créé ({uname} / moniteur123)")
    moniteurs.append(user)

# ─── Créer des élèves ────────────────────────────────────────────
eleves_data = [
    ('l.petit', 'Lucas', 'Petit', 'lucas.petit@email.fr', '06 11 22 33 44'),
    ('e.moreau', 'Emma', 'Moreau', 'emma.moreau@email.fr', '06 22 33 44 55'),
    ('a.laurent', 'Antoine', 'Laurent', 'antoine.laurent@email.fr', '06 33 44 55 66'),
    ('c.dubois', 'Camille', 'Dubois', 'camille.dubois@email.fr', '06 44 55 66 77'),
    ('m.leroy', 'Marie', 'Leroy', 'marie.leroy@email.fr', '06 55 66 77 88'),
]

eleves = []
for uname, first, last, email, tel in eleves_data:
    user, created = User.objects.get_or_create(username=uname, defaults={
        'first_name': first, 'last_name': last, 'email': email
    })
    if created:
        user.set_password('eleve123')
        user.save()
        Profile.objects.create(user=user, role='eleve', telephone=tel)
        print(f"  ✅ Élève {first} {last} créé ({uname} / eleve123)")
    eleves.append(user)

# ─── Créer des véhicules ─────────────────────────────────────────
vehicules_data = [
    ('AB-123-CD', 'Renault', 'Clio V', 2023),
    ('EF-456-GH', 'Peugeot', '208', 2022),
    ('IJ-789-KL', 'Citroën', 'C3', 2023),
    ('MN-012-OP', 'Renault', 'Captur', 2024),
]

vehicules = []
for immat, marque, modele, annee in vehicules_data:
    v, created = Vehicle.objects.get_or_create(immatriculation=immat, defaults={
        'marque': marque, 'modele': modele, 'annee': annee
    })
    if created:
        print(f"  ✅ Véhicule {marque} {modele} ({immat}) créé")
    vehicules.append(v)

# ─── Créer des leçons ────────────────────────────────────────────
now = timezone.now()
lecons_created = 0

# Leçons passées (effectuées)
for i in range(8):
    date = now - timedelta(days=random.randint(5, 30), hours=random.randint(0, 8))
    lecon, created = Lesson.objects.get_or_create(
        moniteur=random.choice(moniteurs),
        date_heure=date,
        defaults={
            'vehicule': random.choice(vehicules),
            'duree': random.choice([60, 90]),
            'statut': 'effectuee',
            'notes': random.choice([
                "Bon travail sur les créneaux.",
                "Amélioration sur les ronds-points.",
                "Bonne maîtrise du démarrage en côte.",
                "Attention aux angles morts.",
                None
            ])
        }
    )
    if created:
        lecons_created += 1
        # Créer une réservation associée
        Booking.objects.get_or_create(
            eleve=random.choice(eleves),
            lecon=lecon,
            defaults={'statut': 'confirmee'}
        )

# Leçons futures (disponibles)
for i in range(10):
    date = now + timedelta(days=random.randint(1, 14), hours=random.randint(8, 17))
    lecon, created = Lesson.objects.get_or_create(
        moniteur=random.choice(moniteurs),
        date_heure=date,
        defaults={
            'vehicule': random.choice(vehicules),
            'duree': random.choice([60, 90]),
            'statut': 'disponible',
        }
    )
    if created:
        lecons_created += 1

# Leçons réservées (futures, complètes)
for i in range(4):
    date = now + timedelta(days=random.randint(1, 7), hours=random.randint(8, 17))
    lecon, created = Lesson.objects.get_or_create(
        moniteur=random.choice(moniteurs),
        date_heure=date,
        defaults={
            'vehicule': random.choice(vehicules),
            'duree': 60,
            'statut': 'complete',
        }
    )
    if created:
        lecons_created += 1
        Booking.objects.get_or_create(
            eleve=random.choice(eleves),
            lecon=lecon,
            defaults={'statut': 'confirmee'}
        )

print(f"  ✅ {lecons_created} leçons créées")

# ─── Créer des paiements ─────────────────────────────────────────
paiements_created = 0
for eleve in eleves:
    for i in range(random.randint(1, 3)):
        Payment.objects.create(
            eleve=eleve,
            montant=random.choice([45, 50, 90, 100, 200]),
            methode=random.choice(['carte', 'especes', 'virement']),
            statut=random.choice(['paye', 'paye', 'paye', 'en_attente']),
            description=random.choice(["Leçon de conduite", "Forfait 5 heures", "Inscription", "Leçon supplémentaire"])
        )
        paiements_created += 1
print(f"  ✅ {paiements_created} paiements créés")

# ─── Créer des questions de quiz ──────────────────────────────────
quiz_data = [
    {
        'question': "Quelle est la vitesse maximale autorisée en agglomération ?",
        'option_a': "30 km/h", 'option_b': "50 km/h", 'option_c': "70 km/h", 'option_d': "90 km/h",
        'reponse_correcte': 'B',
        'explication': "En agglomération, la vitesse est limitée à 50 km/h sauf indication contraire."
    },
    {
        'question': "Quelle est la distance de sécurité minimale sur autoroute à 130 km/h ?",
        'option_a': "50 mètres", 'option_b': "100 mètres", 'option_c': "130 mètres", 'option_d': "200 mètres",
        'reponse_correcte': 'C',
        'explication': "La distance de sécurité correspond à 2 secondes, soit environ la vitesse en mètres."
    },
    {
        'question': "Le taux d'alcoolémie maximal autorisé pour un jeune conducteur est de :",
        'option_a': "0,0 g/l", 'option_b': "0,2 g/l", 'option_c': "0,5 g/l", 'option_d': "0,8 g/l",
        'reponse_correcte': 'B',
        'explication': "Pour les conducteurs en période probatoire, le taux est de 0,2 g/l."
    },
    {
        'question': "Un panneau rond à fond bleu est un panneau de :",
        'option_a': "Danger", 'option_b': "Interdiction", 'option_c': "Obligation", 'option_d': "Indication",
        'reponse_correcte': 'C',
        'explication': "Les panneaux ronds à fond bleu indiquent une obligation."
    },
    {
        'question': "Quand doit-on allumer ses feux de croisement ?",
        'option_a': "Uniquement la nuit", 'option_b': "En cas de pluie", 'option_c': "La nuit et par visibilité réduite", 'option_d': "Jamais en ville",
        'reponse_correcte': 'C',
        'explication': "Les feux de croisement s'utilisent la nuit et par visibilité réduite (pluie, brouillard...)."
    },
    {
        'question': "À une intersection sans signalisation, qui est prioritaire ?",
        'option_a': "Le véhicule venant de gauche", 'option_b': "Le véhicule venant de droite", 'option_c': "Le premier arrivé", 'option_d': "Le plus gros véhicule",
        'reponse_correcte': 'B',
        'explication': "La règle de priorité à droite s'applique par défaut."
    },
    {
        'question': "Le triangle de présignalisation doit être placé à quelle distance du véhicule immobilisé ?",
        'option_a': "10 mètres", 'option_b': "30 mètres", 'option_c': "50 mètres", 'option_d': "100 mètres",
        'reponse_correcte': 'B',
        'explication': "Le triangle doit être placé à au moins 30 mètres en amont du véhicule."
    },
    {
        'question': "Le port de la ceinture de sécurité est obligatoire :",
        'option_a': "Uniquement à l'avant", 'option_b': "Uniquement sur autoroute", 'option_c': "Pour tous les passagers", 'option_d': "Uniquement pour le conducteur",
        'reponse_correcte': 'C',
        'explication': "La ceinture est obligatoire pour tous les occupants du véhicule."
    },
    {
        'question': "Quelle est la durée de validité du permis de conduire au format carte ?",
        'option_a': "5 ans", 'option_b': "10 ans", 'option_c': "15 ans", 'option_d': "À vie",
        'reponse_correcte': 'C',
        'explication': "Le permis au format carte de crédit est valable 15 ans (renouvellement administratif)."
    },
    {
        'question': "Un piéton engage la traversée sur un passage protégé. Que devez-vous faire ?",
        'option_a': "Klaxonner pour qu'il se dépêche", 'option_b': "Accélérer pour passer avant lui", 'option_c': "Vous arrêter pour le laisser passer", 'option_d': "Le contourner",
        'reponse_correcte': 'C',
        'explication': "Le piéton engagé sur un passage protégé a toujours la priorité."
    },
]

quiz_created = 0
for q in quiz_data:
    _, created = QuizQuestion.objects.get_or_create(
        question=q['question'],
        defaults=q
    )
    if created:
        quiz_created += 1
print(f"  ✅ {quiz_created} questions de quiz créées")

print("\n🎉 Base de données peuplée avec succès !")
print("\n📋 Comptes disponibles :")
print("  Admin    : admin / admin123")
print("  Moniteur : m.dupont / moniteur123")
print("  Élève    : l.petit / eleve123")

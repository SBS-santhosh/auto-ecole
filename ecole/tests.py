"""
Tests unitaires — AutoÉcole Pro
================================
Méthodologie : Django TestCase (unittest sous-jacent)
Ces tests vérifient les fonctionnalités principales exigées pour l'épreuve E6 BTS SIO :
  - Modèles (création, relations)
  - Inscription élève + complexité du mot de passe
  - Connexion / déconnexion (authentification)
  - Contrôle d'accès par rôle (décorateurs)
  - Réservation de leçon (association N,N via Booking)
  - Annulation de réservation

Lancer les tests :
    python manage.py test ecole
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile, Vehicle, Lesson, Booking, Payment
from django.utils import timezone
from datetime import timedelta


# ══════════════════════════════════════════════════════════════════
#  TESTS DES MODÈLES
# ══════════════════════════════════════════════════════════════════

class ProfileModelTest(TestCase):
    """Vérifie le modèle Profile (association 1,1 → 1,N avec User)."""

    def setUp(self):
        """Création d'un utilisateur de test avec son profil."""
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!',
            first_name='Jean',
            last_name='Dupont',
        )
        # Le profil est créé manuellement ici (pas de signal, c'est via le form en prod)
        self.profile = Profile.objects.create(user=self.user, role='eleve')

    def test_profil_cree_correctement(self):
        """Le profil est bien lié à l'utilisateur avec le bon rôle."""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.role, 'eleve')

    def test_str_profil(self):
        """La représentation textuelle du profil est correcte."""
        expected = "Jean Dupont (Élève)"
        self.assertEqual(str(self.profile), expected)

    def test_role_choices_valides(self):
        """Les rôles disponibles sont exactement : eleve, moniteur, admin."""
        roles = [r[0] for r in Profile.ROLE_CHOICES]
        self.assertIn('eleve', roles)
        self.assertIn('moniteur', roles)
        self.assertIn('admin', roles)


class VehicleModelTest(TestCase):
    """Vérifie le modèle Vehicle."""

    def test_creation_vehicule(self):
        """Un véhicule peut être créé avec les bons attributs."""
        v = Vehicle.objects.create(
            immatriculation='AB-123-CD',
            marque='Peugeot',
            modele='208',
            annee=2022,
            actif=True,
        )
        self.assertEqual(str(v), "Peugeot 208 (AB-123-CD)")
        self.assertTrue(v.actif)


class BookingModelTest(TestCase):
    """Vérifie le modèle Booking (association N,N porteuse de statut)."""

    def setUp(self):
        """Création d'un moniteur, un élève, un véhicule et une leçon."""
        # Moniteur
        self.moniteur_user = User.objects.create_user(username='moniteur1', password='pass')
        Profile.objects.create(user=self.moniteur_user, role='moniteur')
        # Élève
        self.eleve_user = User.objects.create_user(username='eleve1', password='pass')
        Profile.objects.create(user=self.eleve_user, role='eleve')
        # Véhicule
        self.vehicule = Vehicle.objects.create(
            immatriculation='XY-456-ZZ', marque='Renault', modele='Clio', annee=2021
        )
        # Leçon
        self.lecon = Lesson.objects.create(
            moniteur=self.moniteur_user,
            vehicule=self.vehicule,
            date_heure=timezone.now() + timedelta(days=3),
            duree=60,
            statut='disponible',
        )

    def test_reservation_cree_booking(self):
        """Une réservation crée bien un Booking liant l'élève à la leçon."""
        booking = Booking.objects.create(
            eleve=self.eleve_user,
            lecon=self.lecon,
            statut='confirmee',
        )
        self.assertEqual(booking.eleve, self.eleve_user)
        self.assertEqual(booking.lecon, self.lecon)
        self.assertEqual(booking.statut, 'confirmee')

    def test_unicite_reservation(self):
        """Un élève ne peut pas réserver deux fois la même leçon (unique_together)."""
        from django.db import IntegrityError
        Booking.objects.create(eleve=self.eleve_user, lecon=self.lecon, statut='confirmee')
        with self.assertRaises(IntegrityError):
            Booking.objects.create(eleve=self.eleve_user, lecon=self.lecon, statut='confirmee')


# ══════════════════════════════════════════════════════════════════
#  TESTS D'INSCRIPTION (COMPLEXITÉ MOT DE PASSE)
# ══════════════════════════════════════════════════════════════════

class InscriptionTest(TestCase):
    """Vérifie la page d'inscription et la validation du mot de passe."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('inscription')

    def test_inscription_valide(self):
        """Un élève peut créer un compte avec un mot de passe valide."""
        data = {
            'username': 'nouveau_eleve',
            'first_name': 'Marie',
            'last_name': 'Martin',
            'email': 'marie@test.fr',
            'telephone': '0601020304',
            'password1': 'MonMotDePasse123!',
            'password2': 'MonMotDePasse123!',
        }
        response = self.client.post(self.url, data)
        # Après inscription réussie → redirection vers le dashboard élève
        self.assertEqual(response.status_code, 302)
        # L'utilisateur a bien été créé en base
        self.assertTrue(User.objects.filter(username='nouveau_eleve').exists())
        # Un profil 'eleve' lui a été associé automatiquement
        user = User.objects.get(username='nouveau_eleve')
        self.assertEqual(user.profile.role, 'eleve')

    def test_inscription_mot_de_passe_trop_court(self):
        """Le formulaire doit rejeter un mot de passe trop court (< 8 caractères)."""
        data = {
            'username': 'eleve2',
            'first_name': 'Jean',
            'last_name': 'Paul',
            'email': 'jp@test.fr',
            'password1': '123',
            'password2': '123',
        }
        response = self.client.post(self.url, data)
        # Le formulaire doit être réaffiché (pas de redirection)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='eleve2').exists())

    def test_inscription_mot_de_passe_entierement_numerique(self):
        """Le formulaire doit rejeter un mot de passe 100% numérique."""
        data = {
            'username': 'eleve3',
            'first_name': 'Alice',
            'last_name': 'Durand',
            'email': 'alice@test.fr',
            'password1': '12345678',
            'password2': '12345678',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='eleve3').exists())

    def test_inscription_mots_de_passe_differents(self):
        """Le formulaire doit rejeter les mots de passe qui ne correspondent pas."""
        data = {
            'username': 'eleve4',
            'first_name': 'Bob',
            'last_name': 'Lapin',
            'email': 'bob@test.fr',
            'password1': 'MotDePasse123!',
            'password2': 'AutreMotDePasse456!',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='eleve4').exists())


# ══════════════════════════════════════════════════════════════════
#  TESTS DE CONNEXION (AUTHENTIFICATION)
# ══════════════════════════════════════════════════════════════════

class ConnexionTest(TestCase):
    """Vérifie la page de connexion avec mot de passe chiffré."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('connexion')
        # Créer un utilisateur élève de test
        self.user = User.objects.create_user(
            username='eleve_test', password='BonMotDePasse42!'
        )
        Profile.objects.create(user=self.user, role='eleve')

    def test_connexion_valide(self):
        """Un utilisateur peut se connecter avec les bons identifiants."""
        response = self.client.post(self.url, {
            'username': 'eleve_test',
            'password': 'BonMotDePasse42!',
        })
        # Redirection après connexion réussie (le mot de passe est vérifié côté Django)
        self.assertEqual(response.status_code, 302)

    def test_connexion_mauvais_mot_de_passe(self):
        """La connexion échoue avec un mauvais mot de passe."""
        response = self.client.post(self.url, {
            'username': 'eleve_test',
            'password': 'MauvaisMotDePasse!',
        })
        # Réaffichage du formulaire (pas de redirection)
        self.assertEqual(response.status_code, 200)
        # Vérifier que le message d'erreur est présent dans la réponse
        self.assertContains(response, 'Identifiants incorrects')

    def test_connexion_utilisateur_inexistant(self):
        """La connexion échoue pour un username qui n'existe pas."""
        response = self.client.post(self.url, {
            'username': 'fantome',
            'password': 'nImporteQuoi!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Identifiants incorrects')

    def test_utilisateur_deja_connecte_redirige(self):
        """Un utilisateur déjà connecté est redirigé depuis la page de connexion."""
        self.client.login(username='eleve_test', password='BonMotDePasse42!')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


# ══════════════════════════════════════════════════════════════════
#  TESTS DE CONTRÔLE D'ACCÈS PAR RÔLE
# ══════════════════════════════════════════════════════════════════

class ControleAccesTest(TestCase):
    """Vérifie que les décorateurs de rôle fonctionnent correctement."""

    def setUp(self):
        self.client = Client()
        # Créer les 3 types d'utilisateurs
        self.eleve = User.objects.create_user(username='el', password='pass')
        Profile.objects.create(user=self.eleve, role='eleve')

        self.moniteur = User.objects.create_user(username='mo', password='pass')
        Profile.objects.create(user=self.moniteur, role='moniteur')

        self.admin = User.objects.create_user(username='ad', password='pass')
        Profile.objects.create(user=self.admin, role='admin')

    def test_eleve_ne_peut_pas_acceder_admin(self):
        """Un élève est redirigé s'il essaie d'accéder au panel admin."""
        self.client.login(username='el', password='pass')
        response = self.client.get(reverse('admin_dashboard'))
        # Doit être redirigé (pas 200)
        self.assertNotEqual(response.status_code, 200)

    def test_moniteur_ne_peut_pas_acceder_admin(self):
        """Un moniteur est redirigé s'il essaie d'accéder au panel admin."""
        self.client.login(username='mo', password='pass')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_admin_peut_acceder_son_dashboard(self):
        """Un admin peut accéder à son tableau de bord."""
        self.client.login(username='ad', password='pass')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_eleve_ne_peut_pas_acceder_espace_moniteur(self):
        """Un élève est redirigé s'il tente d'accéder au planning moniteur."""
        self.client.login(username='el', password='pass')
        response = self.client.get(reverse('moniteur_dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_utilisateur_non_connecte_redirige_vers_connexion(self):
        """Un visiteur non connecté est redirigé vers la page de connexion."""
        response = self.client.get(reverse('eleve_dashboard'))
        self.assertRedirects(response, '/connexion/?next=/dashboard/', fetch_redirect_response=False)


# ══════════════════════════════════════════════════════════════════
#  TESTS DE RÉSERVATION (FONCTIONNALITÉ 1,N → 1,N)
# ══════════════════════════════════════════════════════════════════

class ReservationTest(TestCase):
    """Vérifie la réservation et l'annulation de leçons (Lesson ↔ User via Booking)."""

    def setUp(self):
        self.client = Client()
        # Moniteur
        self.moniteur = User.objects.create_user(username='mon', password='pass')
        Profile.objects.create(user=self.moniteur, role='moniteur')
        # Élève (avec code obtenu pour pouvoir réserver)
        self.eleve = User.objects.create_user(username='elv', password='pass')
        Profile.objects.create(user=self.eleve, role='eleve', code_obtenu=True)
        # Véhicule
        self.vehicule = Vehicle.objects.create(
            immatriculation='AA-111-BB', marque='Citroën', modele='C3', annee=2023
        )
        # Leçon disponible dans le futur
        self.lecon = Lesson.objects.create(
            moniteur=self.moniteur,
            vehicule=self.vehicule,
            date_heure=timezone.now() + timedelta(days=5),
            duree=60,
            statut='disponible',
        )

    def test_reserver_lecon_disponible(self):
        """Un élève (avec code) peut réserver une leçon disponible."""
        self.client.login(username='elv', password='pass')
        url = reverse('eleve_reserver', args=[self.lecon.id])
        response = self.client.get(url)
        # Redirection après réservation
        self.assertEqual(response.status_code, 302)
        # La réservation existe en base
        self.assertTrue(
            Booking.objects.filter(eleve=self.eleve, lecon=self.lecon).exists()
        )
        # La leçon est passée en statut 'complete'
        self.lecon.refresh_from_db()
        self.assertEqual(self.lecon.statut, 'complete')

    def test_annuler_reservation(self):
        """Un élève peut annuler sa réservation ; la leçon repasse en 'disponible'."""
        # Créer la réservation d'abord
        booking = Booking.objects.create(
            eleve=self.eleve, lecon=self.lecon, statut='confirmee'
        )
        self.lecon.statut = 'complete'
        self.lecon.save()

        self.client.login(username='elv', password='pass')
        url = reverse('eleve_annuler', args=[booking.id])
        self.client.get(url)

        # Vérifier que la réservation est annulée
        booking.refresh_from_db()
        self.assertEqual(booking.statut, 'annulee')
        # Vérifier que la leçon est de nouveau disponible
        self.lecon.refresh_from_db()
        self.assertEqual(self.lecon.statut, 'disponible')

    def test_eleve_sans_code_ne_peut_pas_reserver(self):
        """Un élève sans code de la route est redirigé depuis la liste des leçons."""
        # Créer un élève sans code
        eleve_sans_code = User.objects.create_user(username='nocode', password='pass')
        Profile.objects.create(user=eleve_sans_code, role='eleve', code_obtenu=False)
        self.client.login(username='nocode', password='pass')
        response = self.client.get(reverse('eleve_lecons'))
        # Doit être redirigé (pas accès à la liste)
        self.assertEqual(response.status_code, 302)


# ══════════════════════════════════════════════════════════════════
#  TEST CRUD ADMIN (RELATION PRINCIPALE)
# ══════════════════════════════════════════════════════════════════

class CRUDVehiculeTest(TestCase):
    """Vérifie le CRUD des véhicules depuis l'espace admin (exigence E6)."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username='admin_test', password='pass')
        Profile.objects.create(user=self.admin, role='admin')
        self.client.login(username='admin_test', password='pass')

    def test_creer_vehicule(self):
        """L'admin peut créer un véhicule via le formulaire."""
        url = reverse('admin_vehicule_creer')
        data = {
            'immatriculation': 'ZZ-999-XX',
            'marque': 'Toyota',
            'modele': 'Yaris',
            'annee': 2024,
            'actif': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Vehicle.objects.filter(immatriculation='ZZ-999-XX').exists())

    def test_modifier_vehicule(self):
        """L'admin peut modifier les informations d'un véhicule."""
        v = Vehicle.objects.create(
            immatriculation='AA-001-BB', marque='Peugeot', modele='206', annee=2010
        )
        url = reverse('admin_vehicule_modifier', args=[v.id])
        data = {
            'immatriculation': 'AA-001-BB',
            'marque': 'Peugeot',
            'modele': '308',  # modèle modifié
            'annee': 2020,
            'actif': True,
        }
        self.client.post(url, data)
        v.refresh_from_db()
        self.assertEqual(v.modele, '308')

    def test_supprimer_vehicule(self):
        """L'admin peut supprimer un véhicule."""
        v = Vehicle.objects.create(
            immatriculation='BB-002-CC', marque='Ford', modele='Fiesta', annee=2015
        )
        url = reverse('admin_vehicule_supprimer', args=[v.id])
        self.client.post(url)
        self.assertFalse(Vehicle.objects.filter(id=v.id).exists())

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    """Extension du modèle User Django pour ajouter le rôle et les infos supplémentaires."""
    ROLE_CHOICES = [
        ('eleve', 'Élève'),
        ('moniteur', 'Moniteur'),
        ('admin', 'Administrateur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='eleve')
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    numero_permis = models.CharField(max_length=50, blank=True, null=True, verbose_name="Numéro de permis")
    date_inscription = models.DateTimeField(default=timezone.now)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"


class Vehicle(models.Model):
    """Véhicule de l'auto-école."""
    immatriculation = models.CharField(max_length=20, unique=True)
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=50, verbose_name="Modèle")
    annee = models.IntegerField(verbose_name="Année")
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ['marque', 'modele']

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.immatriculation})"


class Lesson(models.Model):
    """Leçon de conduite proposée par un moniteur."""
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('complete', 'Complète'),
        ('effectuee', 'Effectuée'),
        ('annulee', 'Annulée'),
    ]
    moniteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons_moniteur',
                                  limit_choices_to={'profile__role': 'moniteur'})
    vehicule = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    date_heure = models.DateTimeField(verbose_name="Date et heure")
    duree = models.IntegerField(default=60, verbose_name="Durée (minutes)",
                                 help_text="Durée de la leçon en minutes")
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='disponible')
    notes = models.TextField(blank=True, null=True, verbose_name="Notes d'évaluation")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Leçon"
        verbose_name_plural = "Leçons"
        ordering = ['date_heure']

    def __str__(self):
        return f"Leçon {self.date_heure.strftime('%d/%m/%Y %H:%M')} - {self.moniteur.get_full_name()}"


class Booking(models.Model):
    """Réservation d'une leçon par un élève."""
    STATUT_CHOICES = [
        ('confirmee', 'Confirmée'),
        ('en_attente', 'En attente'),
        ('annulee', 'Annulée'),
    ]
    eleve = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings',
                               limit_choices_to={'profile__role': 'eleve'})
    lecon = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='bookings')
    date_reservation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='confirmee')

    class Meta:
        verbose_name = "Réservation"
        verbose_name_plural = "Réservations"
        ordering = ['-date_reservation']
        unique_together = ['eleve', 'lecon']

    def __str__(self):
        return f"Réservation de {self.eleve.get_full_name()} — {self.lecon}"


class Payment(models.Model):
    """Paiement effectué par un élève."""
    METHODE_CHOICES = [
        ('carte', 'Carte bancaire'),
        ('especes', 'Espèces'),
        ('virement', 'Virement'),
        ('cheque', 'Chèque'),
    ]
    STATUT_CHOICES = [
        ('paye', 'Payé'),
        ('en_attente', 'En attente'),
        ('rembourse', 'Remboursé'),
    ]
    eleve = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments',
                               limit_choices_to={'profile__role': 'eleve'})
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    methode = models.CharField(max_length=15, choices=METHODE_CHOICES, default='carte',
                                verbose_name="Méthode de paiement")
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default='en_attente')
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date']

    def __str__(self):
        return f"Paiement {self.montant}€ — {self.eleve.get_full_name()}"


class QuizQuestion(models.Model):
    """Question de quiz pour le code de la route."""
    question = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255, blank=True, null=True)
    reponse_correcte = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])
    explication = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Question Quiz"
        verbose_name_plural = "Questions Quiz"

    def __str__(self):
        return self.question[:80]

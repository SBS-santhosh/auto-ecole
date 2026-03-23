from django.contrib import admin
from .models import Profile, Vehicle, Lesson, Booking, Payment, QuizQuestion


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'telephone', 'date_inscription')
    list_filter = ('role',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('immatriculation', 'marque', 'modele', 'annee', 'actif')
    list_filter = ('actif', 'marque')
    search_fields = ('immatriculation', 'marque', 'modele')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('date_heure', 'moniteur', 'vehicule', 'duree', 'statut')
    list_filter = ('statut', 'moniteur')
    search_fields = ('moniteur__first_name', 'moniteur__last_name')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'lecon', 'date_reservation', 'statut')
    list_filter = ('statut',)
    search_fields = ('eleve__first_name', 'eleve__last_name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'montant', 'date', 'methode', 'statut')
    list_filter = ('statut', 'methode')
    search_fields = ('eleve__first_name', 'eleve__last_name')


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'reponse_correcte')
    search_fields = ('question',)

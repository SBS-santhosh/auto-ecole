import csv
import json
import random
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from .models import Profile, Vehicle, Lesson, Booking, Payment, QuizQuestion
from .forms import (
    InscriptionForm, ProfileForm, UserCreateForm, UserEditForm,
    LessonForm, VehicleForm, PaymentForm, LessonNotesForm,
)
from .decorators import eleve_required, moniteur_required, admin_required


# ══════════════════════════════════════════════════════════════════
#  PAGES PUBLIQUES
# ══════════════════════════════════════════════════════════════════

def index(request):
    """Page d'accueil publique."""
    nb_moniteurs = Profile.objects.filter(role='moniteur').count()
    nb_vehicules = Vehicle.objects.filter(actif=True).count()
    nb_eleves = Profile.objects.filter(role='eleve').count()
    return render(request, 'index.html', {
        'nb_moniteurs': nb_moniteurs,
        'nb_vehicules': nb_vehicules,
        'nb_eleves': nb_eleves,
    })


def inscription(request):
    """Page d'inscription pour les élèves."""
    if request.user.is_authenticated:
        return redirect('redirect_dashboard')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Inscription réussie ! Bienvenue.")
            return redirect('eleve_dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'registration/inscription.html', {'form': form})


def connexion(request):
    """Page de connexion."""
    if request.user.is_authenticated:
        return redirect('redirect_dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Bonjour {user.get_full_name() or user.username} !")
            return redirect('redirect_dashboard')
        else:
            messages.error(request, "Identifiants incorrects.")
    return render(request, 'registration/connexion.html')


def deconnexion(request):
    """Déconnexion."""
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('index')


@login_required
def redirect_dashboard(request):
    """Redirige vers le bon dashboard selon le rôle."""
    try:
        role = request.user.profile.role
    except Profile.DoesNotExist:
        Profile.objects.create(user=request.user, role='admin')
        role = 'admin'

    if role == 'eleve':
        return redirect('eleve_dashboard')
    elif role == 'moniteur':
        return redirect('moniteur_dashboard')
    else:
        return redirect('admin_dashboard')


# ══════════════════════════════════════════════════════════════════
#  ESPACE ÉLÈVE
# ══════════════════════════════════════════════════════════════════

@login_required
@eleve_required
def eleve_dashboard(request):
    """Tableau de bord élève."""
    bookings = Booking.objects.filter(eleve=request.user, statut='confirmee')
    heures_effectuees = Booking.objects.filter(
        eleve=request.user,
        statut='confirmee',
        lecon__statut='effectuee'
    ).aggregate(total=Sum('lecon__duree'))['total'] or 0
    heures_effectuees = round(heures_effectuees / 60, 1)

    prochaines_lecons = Booking.objects.filter(
        eleve=request.user,
        statut='confirmee',
        lecon__date_heure__gte=timezone.now()
    ).select_related('lecon', 'lecon__moniteur', 'lecon__vehicule')[:5]

    total_paye = Payment.objects.filter(
        eleve=request.user, statut='paye'
    ).aggregate(total=Sum('montant'))['total'] or 0

    return render(request, 'eleve/dashboard.html', {
        'bookings': bookings,
        'heures_effectuees': heures_effectuees,
        'objectif_heures': 20,
        'prochaines_lecons': prochaines_lecons,
        'total_paye': total_paye,
    })


@login_required
@eleve_required
def eleve_lecons(request):
    """Liste des leçons disponibles pour réservation."""
    lecons = Lesson.objects.filter(
        statut='disponible',
        date_heure__gte=timezone.now()
    ).select_related('moniteur', 'vehicule')
    return render(request, 'eleve/lecons.html', {'lecons': lecons})


@login_required
@eleve_required
def eleve_reserver(request, lecon_id):
    """Réserver une leçon."""
    lecon = get_object_or_404(Lesson, id=lecon_id, statut='disponible')
    # Vérifier si déjà réservé
    if Booking.objects.filter(eleve=request.user, lecon=lecon).exists():
        messages.warning(request, "Vous avez déjà réservé cette leçon.")
        return redirect('eleve_lecons')
    Booking.objects.create(eleve=request.user, lecon=lecon, statut='confirmee')
    lecon.statut = 'complete'
    lecon.save()
    messages.success(request, "Leçon réservée avec succès !")
    return redirect('eleve_reservations')


@login_required
@eleve_required
def eleve_reservations(request):
    """Mes réservations."""
    reservations = Booking.objects.filter(
        eleve=request.user
    ).select_related('lecon', 'lecon__moniteur', 'lecon__vehicule').order_by('-lecon__date_heure')
    return render(request, 'eleve/reservations.html', {'reservations': reservations})


@login_required
@eleve_required
def eleve_annuler(request, reservation_id):
    """Annuler une réservation."""
    reservation = get_object_or_404(Booking, id=reservation_id, eleve=request.user)
    if reservation.statut == 'annulee':
        messages.warning(request, "Cette réservation est déjà annulée.")
    else:
        reservation.statut = 'annulee'
        reservation.save()
        # Remettre la leçon disponible
        reservation.lecon.statut = 'disponible'
        reservation.lecon.save()
        messages.success(request, "Réservation annulée.")
    return redirect('eleve_reservations')


@login_required
@eleve_required
def eleve_historique(request):
    """Historique des leçons effectuées."""
    historique = Booking.objects.filter(
        eleve=request.user,
        lecon__statut='effectuee'
    ).select_related('lecon', 'lecon__moniteur', 'lecon__vehicule').order_by('-lecon__date_heure')
    return render(request, 'eleve/historique.html', {'historique': historique})


@login_required
@eleve_required
def eleve_paiements(request):
    """Mes paiements."""
    paiements = Payment.objects.filter(eleve=request.user).order_by('-date')
    total_paye = paiements.filter(statut='paye').aggregate(total=Sum('montant'))['total'] or 0
    total_en_attente = paiements.filter(statut='en_attente').aggregate(total=Sum('montant'))['total'] or 0
    return render(request, 'eleve/paiements.html', {
        'paiements': paiements,
        'total_paye': total_paye,
        'total_en_attente': total_en_attente,
    })


@login_required
@eleve_required
def eleve_profil(request):
    """Modifier mon profil."""
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect('eleve_profil')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'eleve/profil.html', {'form': form})


@login_required
@eleve_required
def eleve_quiz(request):
    """Quiz code de la route."""
    questions = list(QuizQuestion.objects.all())
    if len(questions) > 10:
        questions = random.sample(questions, 10)

    if request.method == 'POST':
        score = 0
        total = 0
        resultats = []
        for q in QuizQuestion.objects.all():
            reponse = request.POST.get(f'question_{q.id}')
            if reponse:
                total += 1
                correct = reponse == q.reponse_correcte
                if correct:
                    score += 1
                resultats.append({
                    'question': q.question,
                    'reponse_donnee': reponse,
                    'reponse_correcte': q.reponse_correcte,
                    'correct': correct,
                    'explication': q.explication,
                })
        return render(request, 'eleve/quiz_result.html', {
            'score': score,
            'total': total,
            'resultats': resultats,
            'pourcentage': round(score / total * 100) if total > 0 else 0,
        })

    return render(request, 'eleve/quiz.html', {'questions': questions})


# ══════════════════════════════════════════════════════════════════
#  ESPACE MONITEUR
# ══════════════════════════════════════════════════════════════════

@login_required
@moniteur_required
def moniteur_dashboard(request):
    """Tableau de bord moniteur."""
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    mes_lecons = Lesson.objects.filter(moniteur=request.user)
    lecons_semaine = mes_lecons.filter(
        date_heure__date__gte=week_start,
        date_heure__date__lte=week_end
    )
    nb_eleves = Booking.objects.filter(
        lecon__moniteur=request.user,
        statut='confirmee'
    ).values('eleve').distinct().count()

    lecons_a_venir = mes_lecons.filter(
        date_heure__gte=timezone.now(),
        statut__in=['disponible', 'complete']
    )[:5]

    return render(request, 'moniteur/dashboard.html', {
        'total_lecons': mes_lecons.count(),
        'lecons_semaine': lecons_semaine.count(),
        'nb_eleves': nb_eleves,
        'lecons_a_venir': lecons_a_venir,
    })


@login_required
@moniteur_required
def moniteur_planning(request):
    """Planning hebdomadaire du moniteur."""
    today = timezone.now().date()
    week_offset = int(request.GET.get('week', 0))
    week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=6)

    lecons = Lesson.objects.filter(
        moniteur=request.user,
        date_heure__date__gte=week_start,
        date_heure__date__lte=week_end
    ).select_related('vehicule').prefetch_related('bookings__eleve')

    jours = []
    for i in range(7):
        jour = week_start + timedelta(days=i)
        lecons_jour = [l for l in lecons if l.date_heure.date() == jour]
        jours.append({'date': jour, 'lecons': lecons_jour})

    return render(request, 'moniteur/planning.html', {
        'jours': jours,
        'week_start': week_start,
        'week_end': week_end,
        'week_offset': week_offset,
    })


@login_required
@moniteur_required
def moniteur_eleves(request):
    """Liste des élèves du moniteur."""
    eleve_ids = Booking.objects.filter(
        lecon__moniteur=request.user,
        statut='confirmee'
    ).values_list('eleve', flat=True).distinct()
    eleves = User.objects.filter(id__in=eleve_ids).select_related('profile')

    # Ajouter les stats pour chaque élève
    eleves_data = []
    for eleve in eleves:
        heures = Booking.objects.filter(
            eleve=eleve,
            lecon__moniteur=request.user,
            lecon__statut='effectuee'
        ).aggregate(total=Sum('lecon__duree'))['total'] or 0
        nb_lecons = Booking.objects.filter(
            eleve=eleve,
            lecon__moniteur=request.user,
            statut='confirmee'
        ).count()
        eleves_data.append({
            'user': eleve,
            'heures': round(heures / 60, 1),
            'nb_lecons': nb_lecons,
        })

    return render(request, 'moniteur/eleves.html', {'eleves': eleves_data})


@login_required
@moniteur_required
def moniteur_creer_lecon(request):
    """Créer un créneau de leçon."""
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lecon = form.save(commit=False)
            lecon.moniteur = request.user
            lecon.save()
            messages.success(request, "Créneau créé avec succès.")
            return redirect('moniteur_planning')
    else:
        form = LessonForm(initial={'moniteur': request.user})
    return render(request, 'moniteur/creer_lecon.html', {'form': form})


@login_required
@moniteur_required
def moniteur_marquer_effectuee(request, lecon_id):
    """Marquer une leçon comme effectuée."""
    lecon = get_object_or_404(Lesson, id=lecon_id, moniteur=request.user)
    lecon.statut = 'effectuee'
    lecon.save()
    messages.success(request, "Leçon marquée comme effectuée.")
    return redirect('moniteur_planning')


@login_required
@moniteur_required
def moniteur_notes(request, lecon_id):
    """Ajouter des notes d'évaluation à une leçon."""
    lecon = get_object_or_404(Lesson, id=lecon_id, moniteur=request.user)
    if request.method == 'POST':
        form = LessonNotesForm(request.POST, instance=lecon)
        if form.is_valid():
            form.save()
            messages.success(request, "Notes enregistrées.")
            return redirect('moniteur_planning')
    else:
        form = LessonNotesForm(instance=lecon)
    booking = lecon.bookings.filter(statut='confirmee').first()
    return render(request, 'moniteur/notes.html', {
        'form': form,
        'lecon': lecon,
        'eleve': booking.eleve if booking else None,
    })


@login_required
@moniteur_required
def moniteur_dossier_eleve(request, eleve_id):
    """Voir le dossier complet d'un élève."""
    eleve = get_object_or_404(User, id=eleve_id, profile__role='eleve')
    lecons = Booking.objects.filter(
        eleve=eleve,
        lecon__moniteur=request.user
    ).select_related('lecon', 'lecon__vehicule').order_by('-lecon__date_heure')

    heures = Booking.objects.filter(
        eleve=eleve,
        lecon__statut='effectuee'
    ).aggregate(total=Sum('lecon__duree'))['total'] or 0

    return render(request, 'moniteur/dossier_eleve.html', {
        'eleve': eleve,
        'lecons': lecons,
        'heures': round(heures / 60, 1),
    })


# ══════════════════════════════════════════════════════════════════
#  ESPACE ADMIN
# ══════════════════════════════════════════════════════════════════

@login_required
@admin_required
def admin_dashboard(request):
    """Tableau de bord administrateur avec statistiques."""
    nb_eleves = Profile.objects.filter(role='eleve').count()
    nb_moniteurs = Profile.objects.filter(role='moniteur').count()
    nb_lecons = Lesson.objects.count()
    nb_vehicules = Vehicle.objects.filter(actif=True).count()
    nb_reservations = Booking.objects.filter(statut='confirmee').count()

    total_revenus = Payment.objects.filter(statut='paye').aggregate(
        total=Sum('montant'))['total'] or 0
    paiements_en_attente = Payment.objects.filter(statut='en_attente').aggregate(
        total=Sum('montant'))['total'] or 0

    lecons_recentes = Lesson.objects.all().select_related('moniteur', 'vehicule')[:10]
    reservations_recentes = Booking.objects.all().select_related(
        'eleve', 'lecon', 'lecon__moniteur')[:10]

    return render(request, 'admin_panel/dashboard.html', {
        'nb_eleves': nb_eleves,
        'nb_moniteurs': nb_moniteurs,
        'nb_lecons': nb_lecons,
        'nb_vehicules': nb_vehicules,
        'nb_reservations': nb_reservations,
        'total_revenus': total_revenus,
        'paiements_en_attente': paiements_en_attente,
        'lecons_recentes': lecons_recentes,
        'reservations_recentes': reservations_recentes,
    })


# ─── CRUD Élèves ─────────────────────────────────────────────────

@login_required
@admin_required
def admin_eleves(request):
    """Liste des élèves."""
    eleves = User.objects.filter(profile__role='eleve').select_related('profile')
    return render(request, 'admin_panel/eleves.html', {'eleves': eleves})


@login_required
@admin_required
def admin_eleve_creer(request):
    """Créer un élève."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.cleaned_data['role'] = 'eleve'
            form.save()
            messages.success(request, "Élève créé avec succès.")
            return redirect('admin_eleves')
    else:
        form = UserCreateForm(initial={'role': 'eleve'})
    return render(request, 'admin_panel/user_form.html', {
        'form': form, 'titre': 'Créer un élève', 'back_url': 'admin_eleves'
    })


@login_required
@admin_required
def admin_eleve_modifier(request, user_id):
    """Modifier un élève."""
    user = get_object_or_404(User, id=user_id, profile__role='eleve')
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Élève modifié.")
            return redirect('admin_eleves')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'admin_panel/user_form.html', {
        'form': form, 'titre': 'Modifier l\'élève', 'back_url': 'admin_eleves'
    })


@login_required
@admin_required
def admin_eleve_supprimer(request, user_id):
    """Supprimer un élève."""
    user = get_object_or_404(User, id=user_id, profile__role='eleve')
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Élève supprimé.")
        return redirect('admin_eleves')
    return render(request, 'admin_panel/confirm_delete.html', {
        'objet': user.get_full_name(), 'back_url': 'admin_eleves'
    })


# ─── CRUD Moniteurs ──────────────────────────────────────────────

@login_required
@admin_required
def admin_moniteurs(request):
    """Liste des moniteurs."""
    moniteurs = User.objects.filter(profile__role='moniteur').select_related('profile')
    return render(request, 'admin_panel/moniteurs.html', {'moniteurs': moniteurs})


@login_required
@admin_required
def admin_moniteur_creer(request):
    """Créer un moniteur."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.cleaned_data['role'] = 'moniteur'
            form.save()
            messages.success(request, "Moniteur créé avec succès.")
            return redirect('admin_moniteurs')
    else:
        form = UserCreateForm(initial={'role': 'moniteur'})
    return render(request, 'admin_panel/user_form.html', {
        'form': form, 'titre': 'Créer un moniteur', 'back_url': 'admin_moniteurs'
    })


@login_required
@admin_required
def admin_moniteur_modifier(request, user_id):
    """Modifier un moniteur."""
    user = get_object_or_404(User, id=user_id, profile__role='moniteur')
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Moniteur modifié.")
            return redirect('admin_moniteurs')
    else:
        form = UserEditForm(instance=user)
    return render(request, 'admin_panel/user_form.html', {
        'form': form, 'titre': 'Modifier le moniteur', 'back_url': 'admin_moniteurs'
    })


@login_required
@admin_required
def admin_moniteur_supprimer(request, user_id):
    """Supprimer un moniteur."""
    user = get_object_or_404(User, id=user_id, profile__role='moniteur')
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Moniteur supprimé.")
        return redirect('admin_moniteurs')
    return render(request, 'admin_panel/confirm_delete.html', {
        'objet': user.get_full_name(), 'back_url': 'admin_moniteurs'
    })


# ─── CRUD Leçons ─────────────────────────────────────────────────

@login_required
@admin_required
def admin_lecons(request):
    """Liste de toutes les leçons."""
    lecons = Lesson.objects.all().select_related('moniteur', 'vehicule')
    return render(request, 'admin_panel/lecons.html', {'lecons': lecons})


@login_required
@admin_required
def admin_lecon_creer(request):
    """Créer une leçon."""
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Leçon créée.")
            return redirect('admin_lecons')
    else:
        form = LessonForm()
    return render(request, 'admin_panel/lecon_form.html', {
        'form': form, 'titre': 'Créer une leçon'
    })


@login_required
@admin_required
def admin_lecon_modifier(request, lecon_id):
    """Modifier une leçon."""
    lecon = get_object_or_404(Lesson, id=lecon_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lecon)
        if form.is_valid():
            form.save()
            messages.success(request, "Leçon modifiée.")
            return redirect('admin_lecons')
    else:
        form = LessonForm(instance=lecon)
    return render(request, 'admin_panel/lecon_form.html', {
        'form': form, 'titre': 'Modifier la leçon'
    })


@login_required
@admin_required
def admin_lecon_supprimer(request, lecon_id):
    """Supprimer une leçon."""
    lecon = get_object_or_404(Lesson, id=lecon_id)
    if request.method == 'POST':
        lecon.delete()
        messages.success(request, "Leçon supprimée.")
        return redirect('admin_lecons')
    return render(request, 'admin_panel/confirm_delete.html', {
        'objet': str(lecon), 'back_url': 'admin_lecons'
    })


# ─── Réservations ────────────────────────────────────────────────

@login_required
@admin_required
def admin_reservations(request):
    """Toutes les réservations."""
    reservations = Booking.objects.all().select_related(
        'eleve', 'lecon', 'lecon__moniteur', 'lecon__vehicule')
    return render(request, 'admin_panel/reservations.html', {'reservations': reservations})


# ─── CRUD Véhicules ──────────────────────────────────────────────

@login_required
@admin_required
def admin_vehicules(request):
    """Liste des véhicules."""
    vehicules = Vehicle.objects.all()
    return render(request, 'admin_panel/vehicules.html', {'vehicules': vehicules})


@login_required
@admin_required
def admin_vehicule_creer(request):
    """Créer un véhicule."""
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Véhicule ajouté.")
            return redirect('admin_vehicules')
    else:
        form = VehicleForm()
    return render(request, 'admin_panel/vehicule_form.html', {
        'form': form, 'titre': 'Ajouter un véhicule'
    })


@login_required
@admin_required
def admin_vehicule_modifier(request, vehicule_id):
    """Modifier un véhicule."""
    vehicule = get_object_or_404(Vehicle, id=vehicule_id)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicule)
        if form.is_valid():
            form.save()
            messages.success(request, "Véhicule modifié.")
            return redirect('admin_vehicules')
    else:
        form = VehicleForm(instance=vehicule)
    return render(request, 'admin_panel/vehicule_form.html', {
        'form': form, 'titre': 'Modifier le véhicule'
    })


@login_required
@admin_required
def admin_vehicule_supprimer(request, vehicule_id):
    """Supprimer un véhicule."""
    vehicule = get_object_or_404(Vehicle, id=vehicule_id)
    if request.method == 'POST':
        vehicule.delete()
        messages.success(request, "Véhicule supprimé.")
        return redirect('admin_vehicules')
    return render(request, 'admin_panel/confirm_delete.html', {
        'objet': str(vehicule), 'back_url': 'admin_vehicules'
    })


# ─── Paiements ───────────────────────────────────────────────────

@login_required
@admin_required
def admin_paiements(request):
    """Suivi des paiements."""
    paiements = Payment.objects.all().select_related('eleve')
    total_paye = paiements.filter(statut='paye').aggregate(total=Sum('montant'))['total'] or 0
    total_en_attente = paiements.filter(statut='en_attente').aggregate(total=Sum('montant'))['total'] or 0
    return render(request, 'admin_panel/paiements.html', {
        'paiements': paiements,
        'total_paye': total_paye,
        'total_en_attente': total_en_attente,
    })


@login_required
@admin_required
def admin_paiement_creer(request):
    """Enregistrer un paiement."""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Paiement enregistré.")
            return redirect('admin_paiements')
    else:
        form = PaymentForm()
    return render(request, 'admin_panel/paiement_form.html', {
        'form': form, 'titre': 'Enregistrer un paiement'
    })


@login_required
@admin_required
def admin_paiement_modifier(request, paiement_id):
    """Modifier un paiement."""
    paiement = get_object_or_404(Payment, id=paiement_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=paiement)
        if form.is_valid():
            form.save()
            messages.success(request, "Paiement modifié.")
            return redirect('admin_paiements')
    else:
        form = PaymentForm(instance=paiement)
    return render(request, 'admin_panel/paiement_form.html', {
        'form': form, 'titre': 'Modifier le paiement'
    })


# ─── Export CSV ──────────────────────────────────────────────────

@login_required
@admin_required
def admin_export_eleves_csv(request):
    """Exporter la liste des élèves en CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="eleves.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prénom', 'Email', 'Téléphone', 'Date inscription'])
    eleves = User.objects.filter(profile__role='eleve').select_related('profile')
    for e in eleves:
        writer.writerow([
            e.last_name, e.first_name, e.email,
            e.profile.telephone or '',
            e.profile.date_inscription.strftime('%d/%m/%Y')
        ])
    return response

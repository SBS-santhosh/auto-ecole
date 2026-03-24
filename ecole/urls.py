from django.urls import path
from . import views

urlpatterns = [
    # ─── Pages publiques ──────────────────────────────────────────
    path('', views.index, name='index'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('redirect/', views.redirect_dashboard, name='redirect_dashboard'),

    # ─── Espace Élève ─────────────────────────────────────────────
    path('dashboard/', views.eleve_dashboard, name='eleve_dashboard'),
    path('lecons/', views.eleve_lecons, name='eleve_lecons'),
    path('lecons/<int:lecon_id>/reserver/', views.eleve_reserver, name='eleve_reserver'),
    path('reservations/', views.eleve_reservations, name='eleve_reservations'),
    path('reservations/<int:reservation_id>/annuler/', views.eleve_annuler, name='eleve_annuler'),
    path('historique/', views.eleve_historique, name='eleve_historique'),
    path('paiements/', views.eleve_paiements, name='eleve_paiements'),
    path('profil/', views.eleve_profil, name='eleve_profil'),
    path('quiz/', views.eleve_quiz, name='eleve_quiz'),
    path('documents/', views.eleve_documents, name='eleve_documents'),
    path('demande-neph/', views.eleve_demande_neph, name='eleve_demande_neph'),
    path('cours/', views.eleve_cours, name='eleve_cours'),
    path('cours/<int:cours_id>/', views.eleve_cours_detail, name='eleve_cours_detail'),

    # ─── Espace Moniteur ──────────────────────────────────────────
    path('moniteur/dashboard/', views.moniteur_dashboard, name='moniteur_dashboard'),
    path('moniteur/planning/', views.moniteur_planning, name='moniteur_planning'),
    path('moniteur/eleves/', views.moniteur_eleves, name='moniteur_eleves'),
    path('moniteur/lecon/creer/', views.moniteur_creer_lecon, name='moniteur_creer_lecon'),
    path('moniteur/lecon/<int:lecon_id>/effectuee/', views.moniteur_marquer_effectuee, name='moniteur_marquer_effectuee'),
    path('moniteur/lecon/<int:lecon_id>/notes/', views.moniteur_notes, name='moniteur_notes'),
    path('moniteur/eleve/<int:eleve_id>/', views.moniteur_dossier_eleve, name='moniteur_dossier_eleve'),

    # ─── Espace Admin ─────────────────────────────────────────────
    path('gestion/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('gestion/eleves/', views.admin_eleves, name='admin_eleves'),
    path('gestion/eleves/creer/', views.admin_eleve_creer, name='admin_eleve_creer'),
    path('gestion/eleves/<int:user_id>/modifier/', views.admin_eleve_modifier, name='admin_eleve_modifier'),
    path('gestion/eleves/<int:user_id>/supprimer/', views.admin_eleve_supprimer, name='admin_eleve_supprimer'),
    path('gestion/eleves/<int:user_id>/valider_documents/', views.admin_valider_documents, name='admin_valider_documents'),
    path('gestion/eleves/<int:user_id>/valider_neph/', views.admin_valider_neph, name='admin_valider_neph'),

    path('gestion/moniteurs/', views.admin_moniteurs, name='admin_moniteurs'),
    path('gestion/moniteurs/creer/', views.admin_moniteur_creer, name='admin_moniteur_creer'),
    path('gestion/moniteurs/<int:user_id>/modifier/', views.admin_moniteur_modifier, name='admin_moniteur_modifier'),
    path('gestion/moniteurs/<int:user_id>/supprimer/', views.admin_moniteur_supprimer, name='admin_moniteur_supprimer'),

    path('gestion/lecons/', views.admin_lecons, name='admin_lecons'),
    path('gestion/lecons/creer/', views.admin_lecon_creer, name='admin_lecon_creer'),
    path('gestion/lecons/<int:lecon_id>/modifier/', views.admin_lecon_modifier, name='admin_lecon_modifier'),
    path('gestion/lecons/<int:lecon_id>/supprimer/', views.admin_lecon_supprimer, name='admin_lecon_supprimer'),

    path('gestion/reservations/', views.admin_reservations, name='admin_reservations'),

    path('gestion/vehicules/', views.admin_vehicules, name='admin_vehicules'),
    path('gestion/vehicules/creer/', views.admin_vehicule_creer, name='admin_vehicule_creer'),
    path('gestion/vehicules/<int:vehicule_id>/modifier/', views.admin_vehicule_modifier, name='admin_vehicule_modifier'),
    path('gestion/vehicules/<int:vehicule_id>/supprimer/', views.admin_vehicule_supprimer, name='admin_vehicule_supprimer'),

    path('gestion/paiements/', views.admin_paiements, name='admin_paiements'),
    path('gestion/paiements/creer/', views.admin_paiement_creer, name='admin_paiement_creer'),
    path('gestion/paiements/<int:paiement_id>/modifier/', views.admin_paiement_modifier, name='admin_paiement_modifier'),

    path('gestion/export/eleves/', views.admin_export_eleves_csv, name='admin_export_eleves_csv'),
]

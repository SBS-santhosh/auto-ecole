import os
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'Dossier de Validation - Projet Auto-École (Épreuve E6)', align='C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

pdf = PDF()
pdf.add_page()

# Title
pdf.set_font('helvetica', 'B', 16)
pdf.cell(0, 10, '1. User Stories (Récits Utilisateurs)', ln=True)
pdf.ln(5)

# Role: Eleve
pdf.set_font('helvetica', 'B', 12)
pdf.cell(0, 10, 'Role: Eleve (Student)', ln=True)
pdf.set_font('helvetica', '', 11)
us_eleve = [
    "- US-01 [Securite & Inscription]: En tant qu'eleve, je souhaite m'inscrire sur la plateforme",
    "  avec un mot de passe robuste (valide par AUTH_PASSWORD_VALIDATORS) afin de",
    "  securiser mon compte.",
    "- US-02 [Authentification]: Je souhaite me connecter a mon espace via une",
    "  authentification securisee (PBKDF2 SHA-256) (via le decorateur @eleve_required).",
    "- US-03 [Reservation]: Je souhaite pouvoir reserver une ou plusieurs lecons de",
    "  conduite (creation de l'entite porteuse 'Booking' avec statut).",
    "- US-04 [Paiements]: Je souhaite disposer d'un historique de l'ensemble de",
    "  mes paiements associes a mon compte."
]
for line in us_eleve:
    pdf.cell(0, 6, line, ln=True)
pdf.ln(5)

# Role: Moniteur
pdf.set_font('helvetica', 'B', 12)
pdf.cell(0, 10, 'Role: Moniteur (Instructor)', ln=True)
pdf.set_font('helvetica', '', 11)
us_moni = [
    "- US-05 [Authentification]: En tant que moniteur, je dois pouvoir me",
    "  connecter a mon espace dedie (@moniteur_required).",
    "- US-06 [Planning]: En tant que moniteur, je souhaite creer, visualiser et",
    "  administrer le planning de mes lecons proposees via une interface centralisee."
]
for line in us_moni:
    pdf.cell(0, 6, line, ln=True)
pdf.ln(5)

# Role: Admin
pdf.set_font('helvetica', 'B', 12)
pdf.cell(0, 10, 'Role: Administrateur (Admin)', ln=True)
pdf.set_font('helvetica', '', 11)
us_admin = [
    "- US-07 [Acces Back-office]: Je souhaite acceder a l'interface de gestion (@admin_required).",
    "- US-08 [Gestion]: Je souhaite avoir le controle (CRUD) sur les Utilisateurs,",
    "  les Lecons et les Vehicules (Ex: administration complete du modele)."
]
for line in us_admin:
    pdf.cell(0, 6, line, ln=True)
pdf.ln(10)

# SECTION 2
pdf.set_font('helvetica', 'B', 16)
pdf.cell(0, 10, '2. Base de donnees exigee (MCD / Modeles)', ln=True)
pdf.ln(5)

pdf.set_font('helvetica', '', 11)
pdf.multi_cell(0, 6, "La base de donnees relationnelle implemente rigoureusement les associations de cardinalites requises :")
pdf.ln(3)

pdf.set_font('helvetica', 'B', 12)
pdf.cell(0, 6, "Type 1,1 vers 1,N :", ln=True)
pdf.set_font('helvetica', '', 11)
pdf.multi_cell(0, 6, "- Un Utilisateur (1,1) vers Paiements (1,N). Un eleve possede plusieurs Paiements.\n- Un Moniteur (1,1) vers Lecons (1,N). Un moniteur propose plusieurs lecons de conduite.")
pdf.ln(5)

pdf.set_font('helvetica', 'B', 12)
pdf.cell(0, 6, "Type 1,N vers 1,N (porteuse de donnees) :", ln=True)
pdf.set_font('helvetica', '', 11)
pdf.multi_cell(0, 6, "- La Reservation (Booking) : L'entite Reservation porte des donnees (date de reservation, statut confirme/annule). Elle formalise l'association entre l'Entite Eleve (User) (1,N) et l'Entite Lecon (Lesson) (1,N). En effet, un eleve peut etre inscrit a une ou plusieurs lecons, et une lecon peut etre liee a de multiples eleves si annulee ou re-assignee.")
pdf.ln(10)

# SECTION 3
pdf.set_font('helvetica', 'B', 16)
pdf.cell(0, 10, '3. Fonctionnalites et validations E6', ln=True)
pdf.ln(5)
pdf.set_font('helvetica', '', 11)
validations = [
    "- CRUD : Manipulation complete (Creation, Lecture, Mise a jour, Suppression) implementee.",
    "  Verifie dans l'espace Administration pour les Profils, Lecons et Vehicules.",
    "- Inscription & Mot de Passe : Verifications natives (AUTH_PASSWORD_VALIDATORS).",
    "- Authentification stricte : Privileges geres (@admin_required, @moniteur_required).",
    "- Illustration association 1,1 -> 1,N : Interface planning gerant les 'N' lecons.",
    "- Illustration association 1,N -> 1,N : Modulable via le processus 'Reservation' Booking.",
    "- Nettoyage du code : Boilerplate inutile retire, bug de templates resolu.",
    "- Commentaires : Descriptions HTML/Django ajoutees aux 32 templates frontend."
]
for line in validations:
    pdf.cell(0, 6, line, ln=True)

pdf.output('Dossier_UserStory_E6.pdf')
print("PDF created successfully!")

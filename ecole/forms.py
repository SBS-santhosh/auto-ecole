from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Vehicle, Lesson, Booking, Payment


# ─── Authentification ─────────────────────────────────────────────

class InscriptionForm(UserCreationForm):
    """Formulaire d'inscription pour les élèves."""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    telephone = forms.CharField(max_length=20, required=False, label="Téléphone")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                role='eleve',
                telephone=self.cleaned_data.get('telephone', '')
            )
        return user


class ProfileForm(forms.ModelForm):
    """Formulaire de modification du profil."""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = Profile
        fields = ['telephone', 'adresse', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.first_name = self.cleaned_data['first_name']
        profile.user.last_name = self.cleaned_data['last_name']
        profile.user.email = self.cleaned_data['email']
        if commit:
            profile.user.save()
            profile.save()
        return profile


# ─── Admin forms ──────────────────────────────────────────────────

class UserCreateForm(UserCreationForm):
    """Formulaire admin pour créer un utilisateur (élève ou moniteur)."""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    telephone = forms.CharField(max_length=20, required=False, label="Téléphone")
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, label="Rôle")
    numero_permis = forms.CharField(max_length=50, required=False, label="N° de permis (moniteur)")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                telephone=self.cleaned_data.get('telephone', ''),
                numero_permis=self.cleaned_data.get('numero_permis', '')
            )
        return user


class UserEditForm(forms.ModelForm):
    """Formulaire admin pour modifier un utilisateur."""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="Email")
    telephone = forms.CharField(max_length=20, required=False, label="Téléphone")
    numero_permis = forms.CharField(max_length=50, required=False, label="N° de permis")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            profile = self.instance.profile
            self.fields['telephone'].initial = profile.telephone
            self.fields['numero_permis'].initial = profile.numero_permis
        except Profile.DoesNotExist:
            pass

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.telephone = self.cleaned_data.get('telephone', '')
            profile.numero_permis = self.cleaned_data.get('numero_permis', '')
            profile.save()
        return user


# ─── Lesson / Vehicle / Payment forms ─────────────────────────────

class LessonForm(forms.ModelForm):
    """Formulaire pour créer/modifier une leçon."""
    class Meta:
        model = Lesson
        fields = ['moniteur', 'vehicule', 'date_heure', 'duree', 'statut']
        widgets = {
            'date_heure': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['moniteur'].queryset = User.objects.filter(profile__role='moniteur')
        self.fields['moniteur'].label_from_instance = lambda u: u.get_full_name() or u.username
        self.fields['date_heure'].input_formats = ['%Y-%m-%dT%H:%M']


class VehicleForm(forms.ModelForm):
    """Formulaire pour créer/modifier un véhicule."""
    class Meta:
        model = Vehicle
        fields = ['immatriculation', 'marque', 'modele', 'annee', 'actif']


class PaymentForm(forms.ModelForm):
    """Formulaire pour enregistrer un paiement."""
    class Meta:
        model = Payment
        fields = ['eleve', 'montant', 'methode', 'statut', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['eleve'].queryset = User.objects.filter(profile__role='eleve')
        self.fields['eleve'].label_from_instance = lambda u: u.get_full_name() or u.username


class LessonNotesForm(forms.ModelForm):
    """Formulaire pour ajouter des notes d'évaluation."""
    class Meta:
        model = Lesson
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'placeholder': "Notes d'évaluation de l'élève..."}),
        }

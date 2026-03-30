import os
import glob

def get_comment(filename):
    if 'eleve' in filename:
        return "{# Dashboard et interface pour les étudiants (élèves). Permet la gestion des leçons, profil, et paiements. #}\n"
    elif 'moniteur' in filename:
        return "{# Dashboard et interface pour les moniteurs. Gestion des plannings, leçons, et fiches élèves. #}\n"
    elif 'admin_panel' in filename:
        return "{# Interface d'administration. Permet le CRUD sur les utilisateurs, véhicules, leçons et paiements. #}\n"
    elif 'registration' in filename:
        return "{# Pages liées à l'authentification (connexion, inscription, gestion des mots de passe). #}\n"
    elif 'index.html' in filename or 'base.html' in filename:
        return ""
    return "{# Vue détaillée ou composant UI de l'application auto-école. #}\n"

templates_dir = 'ecole/templates/**/*.html'
for filepath in glob.glob(templates_dir, recursive=True):
    with open(filepath, 'r+', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('{#') and not content.startswith('{% comment %}') and not content.startswith('{% extends'):
            # Some start with extends
            pass
        
        # If the file starts with extends, we can insert our comment after
        lines = content.split('\n')
        
        # Check if already has a descriptive comment
        has_desc = any('Dashboard' in l or 'Interface' in l or 'Pages' in l for l in lines[:5])
        if has_desc:
            continue
            
        comment = get_comment(filepath)
        if not comment: continue

        if lines[0].startswith('{% extends'):
            lines.insert(1, comment.strip())
        elif lines[0].startswith('{% load'):
            lines.insert(1, comment.strip())
        else:
            lines.insert(0, comment.strip())
            
        f.seek(0)
        f.write('\n'.join(lines))
        f.truncate()
        print(f"Added comment to {filepath}")

# projet-de-probastat
# ⚡ Modélisation et Analyse des Délestages Électriques de la SONABEL à Ouagadougou

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/Interface-Tkinter-green)
![Monte Carlo](https://img.shields.io/badge/Méthode-Monte--Carlo-orange)
![License](https://img.shields.io/badge/Licence-MIT-lightgrey)

**ÉCOLES POLYTECHNIQUE DE OUAGADOUGOU (EPO)**  
IGIT — Génie Informatique & Télécom — Semestre 5  
Cours de Probabilités & Statistiques — 2025–2026

| Membre | Rôle |
|--------|------|
| NADINGA Yentema Josaphat | Modélisation & Simulation |
| SOMÉ Ansovla Mathias | Analyse des données & Rapport |
| YAGO Jefferson Hassan Saïb Rachid | Interface graphique & GitHub |

**Enseignant responsable : Dr Cheick Amed Diloma Gabriel TRAORÉ**

</div>

---

## 📋 Contexte

Chaque année entre mars et avril, la ville de Ouagadougou subit des délestages électriques tournants imposés par la **SONABEL** (Société Nationale Burkinabè d'Électricité). Ces coupures touchent inégalement les quartiers selon leur priorité dans le réseau de distribution, causant des pertes économiques estimées à **26 milliards de FCFA** par saison pour le seul quartier de Karpala.

Ce projet modélise et analyse ces délestages à partir de **56 réponses terrain** collectées via Google Forms auprès de résidents de 22 quartiers de Ouagadougou, en appliquant les outils probabilistes du cours : lois de probabilité, simulation Monte-Carlo et Théorème Central Limite.

---

## 🗂️ Structure du projet

```
sonabel_final/
│
├── main.py                  # Point d'entrée — lance login puis dashboard
├── requirements.txt         # Dépendances Python
│
├── data/
│   └── reponses.xlsx        # Données collectées (56 répondants, Google Forms)
│
└── modules/
    ├── __init__.py
    ├── data_loader.py       # Chargement, nettoyage, paramètres C2/C3
    ├── stats_model.py       # Modélisation statistique & Monte-Carlo
    ├── figures.py           # Génération des 5 figures matplotlib
    ├── login.py             # Fenêtre d'identification Tkinter
    └── dashboard.py         # Dashboard principal (7 pages)
```

---

## 🎯 Quartiers étudiés (Tableau C2/C3)

| Zone | Quartier | Priorité réseau | λ (coup/j) | μ_Y (h) | E[Z] (h/j) |
|------|----------|-----------------|------------|---------|------------|
| Z1 | Ouaga 2000 | 🔴 Faible | 1,5 | 2,0 | **3,00** |
| Z2 | Tampouy | 🟡 Moyenne | 3,5 | 3,5 | **12,25** |
| Z3 | Pissy | 🟡 Moyenne | 2,0 | 3,0 | **6,00** |
| Z4 | Patte d'Oie | 🟢 Haute | 2,0 | 2,5 | **5,00** |
| Z5 | Karpala | 🟡 Moyenne | 3,5 | 4,5 | **15,75** |
| Z6 | Balkuy | 🟢 Haute | 3,0 | 4,0 | **12,00** |

---

## 📐 Méthodologie

### Variables aléatoires modélisées

```
X ~ Poisson(λ̂ = 2,27)   →  nombre de coupures par jour
                              validé : ratio Var/E = 0,890 ≈ 1 ✓

Y ~ Exp(μ̂ = 2,03 h)     →  durée d'une coupure
                              retenu après comparaison graphique + Q-Q plot

Z = Σ Yᵢ (i=1..X)       →  durée totale journalière
    E[Z] = λ × μ          (X et Y indépendants)
    Var[Z] = (λ²+λ)(μ²+σ²) − (λμ)²
```

### Algorithme Monte-Carlo

```python
def simule_journee(quartier, n_rep=50000):
    # Tire X ~ Poisson(λ) : nombre de coupures
    # Tire Y₁,...,Yₓ ~ Exp(μ) : durée de chaque coupure
    # Retourne Z = Y₁ + ... + Yₓ  pour chaque répétition
```

> **50 000 répétitions** par quartier → erreur standard < 0,5 %

---

## 📊 Résultats clés

| Indicateur | Valeur |
|-----------|--------|
| Quartier le plus vulnérable | **Karpala** — 77,7 % des journées > 6h |
| P(Z_Karpala > 8h) via TCL | **75,9 %** |
| P(Z_Karpala > 8h) par simulation | **69,9 %** |
| Gain plafond 3h/coupure à Karpala | **−8,0 h/jour (−50,7 %)** |
| Perte économique Karpala/saison | **≈ 26 milliards FCFA** |
| Ratio perte/onduleur (par ménage) | **29,5× le coût d'un onduleur** |

---

## 🚀 Installation et lancement

### Prérequis

- Python 3.10 ou supérieur
- Tkinter (inclus avec Python sur Windows/Mac, voir ci-dessous pour Linux)

```bash
# Vérifier Tkinter
python -m tkinter
```

```bash
# Sur Linux/Ubuntu si manquant
sudo apt install python3-tk
```

### Installation

```bash
# Cloner le dépôt
git clone https://github.com/[votre-nom]/sonabel-delesages.git
cd sonabel-delesages

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement

```bash
python main.py
```

### Comptes de démonstration

| Identifiant | Mot de passe |
|-------------|-------------|
| `admin` | `sonabel2026` |
| `etudiant` | `igit2026` |
| `prof` | `prof123` |

---

## 🖥️ Dashboard — Pages disponibles

| Page | Contenu |
|------|---------|
| 🏠 Accueil | KPIs, tableau C2/C3, membres du groupe |
| 📊 P1 — Descriptive | Fréquences empiriques vs Poisson, IC 95% |
| 📐 P2 — Modélisation | Loi Y : histogramme + Q-Q plot, E[Z] par quartier |
| 🎲 P3 — Monte-Carlo | Distributions Z par quartier (50 000 simulations) |
| 📈 P3 — TCL Karpala | Convergence Monte-Carlo vs approximation TCL |
| 🛡️ P3 — Vulnérabilité | Classement + impact plafonnement 3h/coupure |
| 💰 Approfondissement | Perte économique Karpala + test d'indépendance |

---

## 📦 Dépendances

```
numpy>=1.24
pandas>=1.5
matplotlib>=3.6
scipy>=1.10
openpyxl>=3.1
```

---

## 📝 Rapport

Le rapport complet (10-15 pages) suit la structure imposée :
**Résumé — Introduction — Matériels & Méthodes — Résultats — Conclusion & Perspectives**

Il est disponible dans le fichier `rapport_SONABEL_EPO_final.pdf`.

---

## 📄 Licence

Projet académique — EPO/IGIT — 2025-2026  
Utilisation libre à des fins éducatives.

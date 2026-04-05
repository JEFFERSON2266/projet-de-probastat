"""
stats_model.py — Réponses complètes à toutes les questions du Sujet C final.
"""
import numpy as np
from scipy.stats import norm, expon, poisson
from scipy import stats

# ── Partie 2 Q1 : Choix loi X ───────────────────────────────────────────────
def analyse_loi_X(serie):
    """
    Poisson si ratio Var/E ≈ 1.
    Binomiale si ratio < 1 (sous-dispersion).
    Géométrique si ratio >> 1 (sur-dispersion).
    """
    e=serie.mean(); v=serie.var(ddof=1); ratio=v/e
    if abs(ratio-1)<0.35:   loi="Poisson"
    elif ratio<1:            loi="Binomiale"
    else:                    loi="Géométrique"
    return {'esperance':round(e,4),'variance':round(v,4),
            'ratio_V_E':round(ratio,4),'loi_choisie':loi,'lambda':round(e,4)}

# ── Partie 2 Q2 : Choix loi Y ───────────────────────────────────────────────
def analyse_loi_Y(serie):
    """Normale vs Exponentielle — histogramme + Shapiro-Wilk."""
    s=serie.dropna()
    _,p_sw = stats.shapiro(s) if len(s)<=50 else stats.normaltest(s)
    mu_n,sig_n = norm.fit(s)
    _,sc_e     = expon.fit(s,floc=0)
    ks_n,_=stats.kstest(s,'norm',args=(mu_n,sig_n))
    ks_e,_=stats.kstest(s,'expon',args=(0,sc_e))
    cv = s.std(ddof=1)/s.mean()
    return {
        'loi_choisie':'Exponentielle' if ks_e<ks_n else 'Normale',
        'p_shapiro':round(p_sw,4),'cv':round(cv,4),
        'mu_norm':round(mu_n,4),'sig_norm':round(sig_n,4),'ks_norm':round(ks_n,4),
        'mu_exp':round(sc_e,4),'lambda_exp':round(1/sc_e,4),'ks_exp':round(ks_e,4),
    }

# ── Partie 2 Q3 : E[Z] = E[X]×E[Y] ─────────────────────────────────────────
def calcul_EZ():
    """
    E[Z]=λ×μ valide car X (nb coupures) et Y (durée) sont indépendants :
    le fait qu'une coupure survienne ne détermine pas sa durée.
    """
    from modules.data_loader import QUARTIERS_C3
    res={}
    for q,p in QUARTIERS_C3.items():
        EZ=p['lambda']*p['mu_Y']
        VZ=(p['lambda']**2+p['lambda'])*(p['mu_Y']**2+p['sigma_Y']**2)-(p['lambda']*p['mu_Y'])**2
        res[q]={'zone':p['zone'],'lambda':p['lambda'],'mu_Y':p['mu_Y'],
                'EZ':round(EZ,2),'VZ':round(VZ,2),'priorite':p['priorite']}
    return res

# ── Partie 2 Q4 : Tampouy (Z2) + Karpala (Z5) ───────────────────────────────
def calcul_Z2_plus_Z5():
    """
    Z_total = X1Y1 + X2Y2, Z2⊥Z5 (transformateurs distincts).
    E[Zi*Yi] = λi*μi   Var[Zi*Yi] = (λi²+λi)(μi²+σi²)-(λi*μi)²
    """
    from modules.data_loader import QUARTIERS_C3
    def varz(p): return (p['lambda']**2+p['lambda'])*(p['mu_Y']**2+p['sigma_Y']**2)-(p['lambda']*p['mu_Y'])**2
    p2=QUARTIERS_C3['Tampouy']; p5=QUARTIERS_C3['Karpala']
    EZ2=p2['lambda']*p2['mu_Y']; EZ5=p5['lambda']*p5['mu_Y']
    VZ2=varz(p2); VZ5=varz(p5)
    return {'EZ2':EZ2,'EZ5':EZ5,'E_total':EZ2+EZ5,
            'VZ2':round(VZ2,2),'VZ5':round(VZ5,2),
            'V_total':round(VZ2+VZ5,2),'sigma_total':round(np.sqrt(VZ2+VZ5),2)}

# ── Partie 3 Q1 : simule_journee ─────────────────────────────────────────────
def simule_journee(quartier, n_rep=50000, seed=None):
    """X~Poisson(λ), Y_i~Exp(μ_Y), Z=ΣY_i"""
    from modules.data_loader import QUARTIERS_C3
    p=QUARTIERS_C3[quartier]
    rng=np.random.default_rng(seed)
    Z=np.zeros(n_rep)
    for i in range(n_rep):
        x=rng.poisson(p['lambda'])
        if x>0: Z[i]=rng.exponential(p['mu_Y'],x).sum()
    return Z

def simule_tous(n_rep=50000):
    from modules.data_loader import QUARTIERS_C3
    return {q:simule_journee(q,n_rep,seed=i) for i,q in enumerate(QUARTIERS_C3)}

# ── Partie 3 Q2 : TCL Karpala ────────────────────────────────────────────────
def analyse_TCL_karpala(Z_k):
    """P(Z>8h) via TCL et simulation + courbe de convergence."""
    from modules.data_loader import QUARTIERS_C3
    def varz(p): return (p['lambda']**2+p['lambda'])*(p['mu_Y']**2+p['sigma_Y']**2)-(p['lambda']*p['mu_Y'])**2
    p=QUARTIERS_C3['Karpala']
    EZ=p['lambda']*p['mu_Y']; VZ=varz(p); SZ=np.sqrt(VZ)
    z=(8-EZ)/SZ; p_tcl=1-norm.cdf(z)
    p_sim=(Z_k>8).mean()
    tailles=np.unique(np.logspace(1,np.log10(len(Z_k)),300).astype(int))
    conv=[(Z_k[:n]>8).mean()*100 for n in tailles]
    return {'EZ':EZ,'SZ':round(SZ,3),'z':round(z,3),
            'p_tcl':round(p_tcl,4),'p_sim':round(p_sim,4),
            'tailles':tailles,'conv':conv}

# ── Partie 3 Q3 : Vulnérabilité onduleur ─────────────────────────────────────
def vulnerabilite(sims):
    vuln={q:round((Z>6).mean(),4) for q,Z in sims.items()}
    return dict(sorted(vuln.items(),key=lambda x:-x[1]))

# ── Partie 3 Q4 : Plafond 3h/coupure ────────────────────────────────────────
def simule_plafond(n_rep=50000):
    from modules.data_loader import QUARTIERS_C3
    avant,apres,gains={},{},{}
    for i,(q,p) in enumerate(QUARTIERS_C3.items()):
        rng=np.random.default_rng(i+10)
        Za,Zp=np.zeros(n_rep),np.zeros(n_rep)
        for j in range(n_rep):
            x=rng.poisson(p['lambda'])
            if x>0:
                d=rng.exponential(p['mu_Y'],x)
                Za[j]=d.sum(); Zp[j]=np.minimum(d,3.0).sum()
        avant[q]=round(Za.mean(),2); apres[q]=round(Zp.mean(),2)
        gains[q]=round(Za.mean()-Zp.mean(),2)
    return avant,apres,gains

# ── Appro Q1 : Perte économique Karpala ──────────────────────────────────────
def perte_eco_karpala():
    from modules.data_loader import QUARTIERS_C3
    p=QUARTIERS_C3['Karpala']; EZ=p['lambda']*p['mu_Y']; men=p['pop']/5
    return {'EZ':EZ,'menages':men,
            'perte_j_men':EZ*2500,'perte_s_men':EZ*2500*60,
            'ratio_onduleur':round(EZ*2500*60/80000,1),
            'perte_totale':EZ*2500*60*men,
            'jours_rentab':round(80000/(EZ*2500),1)}

# ── Appro Q2 : Test indépendance priorité / fréquence ────────────────────────
def test_independance(n_sim=100000,seed=99):
    """
    Sujet C : Faible=Ouaga2000(λ=1.5), Haute={Patte d'Oie(2.0),Balkuy(3.0)},
              Moyenne={Tampouy(3.5),Pissy(2.0),Karpala(3.5)}
    """
    from modules.data_loader import QUARTIERS_C3
    rng=np.random.default_rng(seed)
    def grp(prio): return [q for q,p in QUARTIERS_C3.items() if p['priorite']==prio]
    def lam_moy(prio): return np.mean([QUARTIERS_C3[q]['lambda'] for q in grp(prio)])
    lf=lam_moy('Faible'); lh=lam_moy('Haute'); lm=lam_moy('Moyenne')
    pf=(rng.poisson(lf,n_sim)>2).mean()
    ph=(rng.poisson(lh,n_sim)>2).mean()
    pm=(rng.poisson(lm,n_sim)>2).mean()
    return {'q_faible':grp('Faible'),'q_haute':grp('Haute'),'q_moyenne':grp('Moyenne'),
            'lam_faible':lf,'lam_haute':lh,'lam_moyenne':lm,
            'p_faible':round(pf,3),'p_haute':round(ph,3),'p_moyenne':round(pm,3),
            'rapport_h_f':round(ph/pf,2)}

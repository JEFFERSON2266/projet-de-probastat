"""
data_loader.py
Sujet C final — Tableau C2/C3 :
  Z1 Ouaga 2000  Faible   λ=1.5 μ=2.0 σ=0.7
  Z2 Tampouy     Moyenne  λ=3.5 μ=3.5 σ=1.4
  Z3 Pissy       Moyenne  λ=2.0 μ=3.0 σ=1.0
  Z4 Patte d'Oie Haute    λ=2.0 μ=2.5 σ=0.9
  Z5 Karpala     Moyenne  λ=3.5 μ=4.5 σ=1.8
  Z6 Balkuy      Haute    λ=3.0 μ=4.0 σ=1.5
"""
import os, unicodedata
import pandas as pd
import numpy as np
from scipy import stats as sp

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'reponses.xlsx')

# Tableau C2 + C3 (sujet final)
QUARTIERS_C3 = {
    "Ouaga 2000":   {"zone":"Z1","lambda":1.5,"mu_Y":2.0,"sigma_Y":0.7,"pop":40000,"priorite":"Faible"},
    "Tampouy":      {"zone":"Z2","lambda":3.5,"mu_Y":3.5,"sigma_Y":1.4,"pop":85000,"priorite":"Moyenne"},
    "Pissy":        {"zone":"Z3","lambda":2.0,"mu_Y":3.0,"sigma_Y":1.0,"pop":70000,"priorite":"Moyenne"},
    "Patte d'Oie":  {"zone":"Z4","lambda":2.0,"mu_Y":2.5,"sigma_Y":0.9,"pop":48000,"priorite":"Haute"},
    "Karpala":      {"zone":"Z5","lambda":3.5,"mu_Y":4.5,"sigma_Y":1.8,"pop":55000,"priorite":"Moyenne"},
    "Balkuy":       {"zone":"Z6","lambda":3.0,"mu_Y":4.0,"sigma_Y":1.5,"pop":62000,"priorite":"Haute"},
}

COUPURES_MAP = {
    "1 coupure/jour":1,"2 coupures/jour":2,"3 coupures/jour":3,
    "4 coupures/jour":4,"5 coupures/jours":5,"Plus de 5 coupures/jour":6,
}
DUREE_MAP = {"15min":0.25,"30min":0.5,"1h":1.0,"2h":2.0,"Plus de 2h":3.0}
IMPACT_MAP = {"1. Aucun":1,"2. Leger impact":2,"3. Plus ou moins important":3,
              "4. Impact important":4,"5. Très important":5}

def _clean(s):
    s = str(s).strip().replace('\u2019',"'").replace('\u02bc',"'").replace('\u2018',"'")
    s = ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
    return s.lower().strip()

_NORM = {
    "balkuy":"Balkuy","balkui":"Balkuy",
    "tampouy":"Tampouy","pissy":"Pissy",
    "patte d'oie":"Patte d'Oie","pate d'oie":"Patte d'Oie",
    "karpala":"Karpala","tanghin karpala":"Karpala",
    "ouaga 2000":"Ouaga 2000",
    "kamboinsin":"Kamboinsin","kamboisin":"Kamboinsin",
    "saaba":"Saaba","somgande":"Somgandé","bassinko":"Bassinko",
    "cissin":"Cissin","ouidi":"Ouidi","tabtenga":"Tabtenga",
    "zone 1":"Zone 1","zone une":"Zone 1","tanghin":"Tanghin",
    "rimkieta":"Rimkiéta","kalgondin":"Kalgondin","nagrin":"Nagrin",
    "garghin":"Garghin","sondogo":"Sondogo",
    "katre yaar":"Katr Yaar","kate yaar":"Katr Yaar","katr yaar":"Katr Yaar",
}

def _norm(x):
    c = _clean(x)
    return _NORM.get(c, _NORM.get(c.rstrip(), str(x).strip().title()))

def load_data():
    df = pd.read_excel(DATA_PATH, header=0)
    df.columns = ['timestamp','quartier','nb_coupures','duree','activite','impact']
    df = df[~df['quartier'].astype(str).str.contains('Veuillez|quartier',na=False,case=False)]
    df['quartier']        = df['quartier'].astype(str).apply(_norm)
    df['nb_coupures_num'] = df['nb_coupures'].map(COUPURES_MAP)
    df['duree_num']       = df['duree'].map(DUREE_MAP)
    df['impact_num']      = df['impact'].map(IMPACT_MAP)
    df = df.dropna(subset=['nb_coupures_num','duree_num']).copy()
    df['Z'] = df['nb_coupures_num'] * df['duree_num']
    return df.reset_index(drop=True)

def get_stats_par_quartier(df):
    return df.groupby('quartier').agg(
        n=('nb_coupures_num','count'),
        moy_coupures=('nb_coupures_num','mean'),
        var_coupures=('nb_coupures_num','var'),
        moy_duree=('duree_num','mean'),
        std_duree=('duree_num','std'),
        moy_Z=('Z','mean'),
    ).reset_index()

def get_summary(df):
    """Partie 1 Q3 — IC95% sur μ_Y."""
    n=len(df); moy=df['duree_num'].mean(); std=df['duree_num'].std(ddof=1)
    t=sp.t.ppf(0.975,df=n-1); marge=t*std/np.sqrt(n)
    mx=df['nb_coupures_num'].mean(); vx=df['nb_coupures_num'].var(ddof=1)
    return {'n':n,'moy_duree':moy,'std_duree':std,
            'ic_bas':moy-marge,'ic_haut':moy+marge,
            'moy_coupures':mx,'var_coupures':vx,'ratio_VE':vx/mx}

def get_comparaison_C3(df):
    """Partie 1 Q2 — fréquences empiriques vs C3 pour les 6 quartiers."""
    rows=[]
    for q,p in QUARTIERS_C3.items():
        sub=df[df['quartier']==q]
        n_obs=len(sub)
        l_obs=round(sub['nb_coupures_num'].mean(),2) if n_obs>0 else None
        ecart=round(l_obs-p['lambda'],2) if l_obs else None
        # Fréquences empiriques X=1,2,3,4,>=5
        freqs={}
        if n_obs>0:
            for k in [1,2,3,4,5]:
                if k<5: freqs[k]=round((sub['nb_coupures_num']==k).mean()*100,1)
                else:   freqs[k]=round((sub['nb_coupures_num']>=k).mean()*100,1)
        rows.append({'quartier':q,'zone':p['zone'],'priorite':p['priorite'],
                     'lambda_C3':p['lambda'],'lambda_obs':l_obs,'n':n_obs,
                     'ecart':ecart,'freqs':freqs})
    return rows

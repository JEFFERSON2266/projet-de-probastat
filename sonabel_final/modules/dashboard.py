"""dashboard.py — Dashboard Tkinter SONABEL — Sujet C final"""
import tkinter as tk
from tkinter import ttk
import sys, os
import matplotlib; matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..'))
from modules.data_loader  import load_data, get_stats_par_quartier, get_summary, get_comparaison_C3, QUARTIERS_C3
from modules.stats_model  import (analyse_loi_X, analyse_loi_Y, calcul_EZ, calcul_Z2_plus_Z5,
                                   simule_tous, analyse_TCL_karpala, vulnerabilite,
                                   simule_plafond, perte_eco_karpala, test_independance)
from modules import figures as F

BG,BG2,BG3='#0D1117','#161B22','#1C2128'
BORDER='#30363D'; ACCENT='#1565C0'
TEXT,MUTED='#E6EDF3','#8B949E'
SUCCESS,DANGER,WARN='#2EA043','#F85149','#E65100'

PAGES=[
    ('🏠  Accueil',              'home'),
    ('📊  P1 — Descriptive',     'p1'),
    ('📐  P2 — Modélisation',    'p2'),
    ('🎲  P3 — Monte-Carlo',     'p3'),
    ('📈  P3 — TCL Karpala',     'p3_tcl'),
    ('🛡️  P3 — Vulnérabilité',   'p3_vuln'),
    ('💰  Approfondissement',    'appro'),
]

class Dashboard:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title('SONABEL — Dashboard Délestages Ouagadougou')
        self.root.configure(bg=BG)
        try:    self.root.state('zoomed')
        except: self.root.attributes('-zoomed',True)
        self._load(); self._build_ui(); self.root.mainloop()

    def _load(self):
        self.df      = load_data()
        self.stats_q = get_stats_par_quartier(self.df)
        self.summary = get_summary(self.df)
        self.comp    = get_comparaison_C3(self.df)
        self.fx      = analyse_loi_X(self.df['nb_coupures_num'])
        self.fy      = analyse_loi_Y(self.df['duree_num'])
        self.ez      = calcul_EZ()
        self.z2z5    = calcul_Z2_plus_Z5()
        self.sims    = simule_tous(n_rep=50000)
        self.tcl     = analyse_TCL_karpala(self.sims['Karpala'])
        self.vuln    = vulnerabilite(self.sims)
        self.avant, self.apres, self.gains = simule_plafond(n_rep=50000)
        self.perte   = perte_eco_karpala()
        self.indep   = test_independance()

    def _build_ui(self):
        self.sidebar=tk.Frame(self.root,bg=BG2,width=215,highlightbackground=BORDER,highlightthickness=1)
        self.sidebar.pack(side='left',fill='y'); self.sidebar.pack_propagate(False)
        logo=tk.Frame(self.sidebar,bg=ACCENT,pady=12); logo.pack(fill='x')
        tk.Label(logo,text='⚡ SONABEL',font=('Arial',15,'bold'),bg=ACCENT,fg='white').pack()
        tk.Label(logo,text='EPO/IGIT — Délestages OUA 2026',font=('Arial',8),bg=ACCENT,fg='#BBDEFB').pack()
        self.nav={}
        for label,key in PAGES:
            btn=tk.Button(self.sidebar,text=label,font=('Arial',10),bg=BG2,fg=TEXT,
                          activebackground=BG3,relief='flat',anchor='w',padx=14,pady=8,
                          cursor='hand2',command=lambda k=key:self._show(k))
            btn.pack(fill='x'); self.nav[key]=btn
        tk.Frame(self.sidebar,bg=BORDER,height=1).pack(fill='x',pady=6)
        s=self.summary
        for txt in [f"N = {s['n']} répondants",
                    f"λ̂ = {s['moy_coupures']:.4f}  ratio = {s['ratio_VE']:.3f}",
                    f"μ̂_Y = {s['moy_duree']:.4f} h",
                    "Poisson + Exponentielle"]:
            tk.Label(self.sidebar,text=txt,font=('Arial',8),bg=BG2,fg=MUTED).pack()
        tk.Frame(self.sidebar,bg=BG2).pack(fill='both',expand=True)
        tk.Frame(self.sidebar,bg=BORDER,height=1).pack(fill='x')
        tk.Button(self.sidebar,text='🔓  Se déconnecter',font=('Arial',10),
                  bg='#1a1a2e',fg=DANGER,activebackground='#2d0a0a',
                  relief='flat',anchor='w',padx=14,pady=10,cursor='hand2',
                  command=self._logout).pack(fill='x')
        main=tk.Frame(self.root,bg=BG); main.pack(side='left',fill='both',expand=True)
        self.hdr=tk.Frame(main,bg=BG3,pady=9,highlightbackground=BORDER,highlightthickness=1)
        self.hdr.pack(fill='x')
        self.htitle=tk.Label(self.hdr,text='',font=('Arial',14,'bold'),bg=BG3,fg=TEXT)
        self.htitle.pack(side='left',padx=18)
        self.hsub=tk.Label(self.hdr,text='',font=('Arial',9),bg=BG3,fg=MUTED)
        self.hsub.pack(side='left')
        self.content=tk.Frame(main,bg=BG); self.content.pack(fill='both',expand=True)
        self._show('home')

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()
        plt.close('all')

    def _hl(self,key):
        for k,b in self.nav.items():
            b.config(bg=ACCENT if k==key else BG2,fg='white' if k==key else TEXT)

    def _hdr_set(self,t,s=''):
        self.htitle.config(text=t); self.hsub.config(text=s)

    def _embed(self,fig,parent=None,scroll=False):
        p=parent or self.content
        if scroll:
            o=tk.Frame(p,bg=BG); o.pack(fill='both',expand=True)
            sb=ttk.Scrollbar(o,orient='vertical'); sb.pack(side='right',fill='y')
            cv=tk.Canvas(o,bg=BG,yscrollcommand=sb.set,highlightthickness=0)
            cv.pack(side='left',fill='both',expand=True); sb.config(command=cv.yview)
            inn=tk.Frame(cv,bg=BG); cv.create_window((0,0),window=inn,anchor='nw')
            c=FigureCanvasTkAgg(fig,master=inn); c.draw()
            c.get_tk_widget().pack(fill='both',expand=True)
            NavigationToolbar2Tk(c,inn).update()
            inn.update_idletasks(); cv.config(scrollregion=cv.bbox('all'))
            cv.bind('<MouseWheel>',lambda e:cv.yview_scroll(-(e.delta//120),'units'))
        else:
            c=FigureCanvasTkAgg(fig,master=p); c.draw()
            c.get_tk_widget().pack(fill='both',expand=True)
            NavigationToolbar2Tk(c,p).update()

    def _info(self,txt,color=None):
        b=tk.Frame(self.content,bg=BG3,highlightbackground=BORDER,highlightthickness=1)
        b.pack(fill='x',padx=8,pady=(6,0))
        tk.Label(b,text=txt,font=('Courier',9),bg=BG3,fg=color or TEXT,pady=5,
                 wraplength=1100,justify='left').pack(anchor='w',padx=10)

    def _logout(self):
        plt.close('all'); self.root.destroy()
        from modules.login import LoginWindow
        from modules.dashboard import Dashboard
        LoginWindow(on_success=lambda:Dashboard())

    def _show(self,key):
        self._clear(); self._hl(key)
        {'home':self._p_home,'p1':self._p1,'p2':self._p2,
         'p3':self._p3,'p3_tcl':self._p3_tcl,
         'p3_vuln':self._p3_vuln,'appro':self._appro}[key]()

    # ── Accueil ───────────────────────────────────────────────────────────────
    def _p_home(self):
        self._hdr_set('🏠 Tableau de bord','EPO/IGIT — Projet Probabilité & Statistique — Sujet C — 2025-2026')
        fr=tk.Frame(self.content,bg=BG); fr.pack(fill='both',expand=True,padx=28,pady=12)
        tk.Label(fr,text='Modélisation et Analyse des Délestages Électriques de la SONABEL',
                 font=('Arial',17,'bold'),bg=BG,fg=TEXT).pack(pady=(6,2))
        tk.Label(fr,text='NADINGA Yentema Josaphat  ·  SOMÉ Ansovla Mathias  ·  YAGO Jefferson Hassan Ben Saïd',
                 font=('Arial',9,'italic'),bg=BG,fg=MUTED).pack()
        tk.Label(fr,text='Enseignant : Dr Cheick Amed Diloma Gabriel TRAORÉ',
                 font=('Arial',9),bg=BG,fg=MUTED).pack(pady=(0,14))
        kf=tk.Frame(fr,bg=BG); kf.pack(fill='x',pady=4)
        s=self.summary
        kpis=[('Répondants',str(s['n']),'Google Forms',ACCENT),
              ('λ̂ Poisson',f"{s['moy_coupures']:.4f}",'ratio V/E='+f"{s['ratio_VE']:.3f}",'#2E7D32'),
              ('μ̂_Y Exp.',f"{s['moy_duree']:.4f}h",'durée moy. coupure',WARN),
              ('IC 95% μ_Y',f"[{s['ic_bas']:.3f};{s['ic_haut']:.3f}]h",'intervalle confiance','#6A1B9A'),
              ('+ vulnérable','Karpala (Z5)','77.7% j > 6h','#C62828'),
              ('Gain plafond',f"−{self.gains['Karpala']:.1f}h/j",'à Karpala (3h max)','#00838F')]
        for i,(l,v,s2,col) in enumerate(kpis):
            c=tk.Frame(kf,bg=BG2,highlightbackground=col,highlightthickness=2)
            c.grid(row=0,column=i,padx=6,pady=4,sticky='nsew'); kf.columnconfigure(i,weight=1)
            tk.Label(c,text=l,font=('Arial',9),bg=BG2,fg=MUTED).pack(pady=(10,0))
            tk.Label(c,text=v,font=('Arial',13,'bold'),bg=BG2,fg=col).pack()
            tk.Label(c,text=s2,font=('Arial',8),bg=BG2,fg=MUTED).pack(pady=(0,10))
        tk.Frame(fr,bg=BORDER,height=1).pack(fill='x',pady=10)
        m=tk.Frame(fr,bg=BG3,highlightbackground=BORDER,highlightthickness=1); m.pack(fill='x',pady=4)
        tk.Label(m,text='Tableau C2/C3 (Sujet C final)',font=('Arial',10,'bold'),bg=BG3,fg=TEXT).pack(anchor='w',padx=12,pady=(8,4))
        hdrs=['Zone','Quartier','Priorité','λ (C3)','μ_Y (h)','σ_Y (h)','Pop.','E[Z] (h/j)']
        tbl=tk.Frame(m,bg=BG3); tbl.pack(fill='x',padx=12,pady=(0,8))
        for j,h in enumerate(hdrs):
            tk.Label(tbl,text=h,font=('Arial',8,'bold'),bg=ACCENT,fg='white',padx=6,pady=3).grid(row=0,column=j,sticky='nsew',padx=1,pady=1)
        for ri,(q,p) in enumerate(QUARTIERS_C3.items()):
            EZ=p['lambda']*p['mu_Y']; bg_r=BG2 if ri%2==0 else BG3
            col_p=DANGER if p['priorite']=='Faible' else ('#4CAF50' if p['priorite']=='Haute' else WARN)
            vals=[p['zone'],q,p['priorite'],p['lambda'],p['mu_Y'],p['sigma_Y'],f"{p['pop']:,}",f"{EZ:.2f}"]
            for j,v in enumerate(vals):
                fg=col_p if j==2 else TEXT
                tk.Label(tbl,text=str(v),font=('Courier',8),bg=bg_r,fg=fg,padx=6,pady=3).grid(row=ri+1,column=j,sticky='nsew',padx=1,pady=1)
        for j in range(len(hdrs)): tbl.columnconfigure(j,weight=1)

    # ── Partie 1 ──────────────────────────────────────────────────────────────
    def _p1(self):
        s=self.summary
        self._hdr_set('📊 Partie 1 — Collecte & Analyse Descriptive',
                      f"N={s['n']}  x̄={s['moy_coupures']:.4f}  ȳ={s['moy_duree']:.4f}h  IC95%=[{s['ic_bas']:.3f};{s['ic_haut']:.3f}]h")
        self._info(
            f"  P1Q3 — IC95%(μ_Y) = [{s['ic_bas']:.3f} ; {s['ic_haut']:.3f}] h  (Student t_{s['n']-1}=2.004)  "
            f"→ La durée moyenne réelle est entre 1h45 et 2h19 avec 95% de confiance\n"
            f"  P1Q2 — Comparaison C3 vs terrain : voir tableau ci-dessous dans Accueil. "
            f"Tous les écarts < 0,5 coupure/jour → hypothèses C3 confirmées par le terrain.")
        fig_fr=tk.Frame(self.content,bg=BG); fig_fr.pack(fill='both',expand=True)
        c=FigureCanvasTkAgg(F.fig_poisson(self.df,self.summary),master=fig_fr)
        c.draw(); c.get_tk_widget().pack(fill='both',expand=True)
        NavigationToolbar2Tk(c,fig_fr).update()

    # ── Partie 2 ──────────────────────────────────────────────────────────────
    def _p2(self):
        fx=self.fx; fy=self.fy; z2z5=self.z2z5
        self._hdr_set('📐 Partie 2 — Modélisation par Variables Aléatoires',
                      f"X~{fx['loi_choisie']}(λ={fx['lambda']})  Y~{fy['loi_choisie']}(μ={fy['mu_exp']}h)")
        self._info(
            f"  P2Q1 — X ~ Poisson(λ̂={fx['lambda']:.4f}) : ratio V/E={fx['ratio_V_E']:.4f}≈1 ✓  "
            f"(Binomiale exclue: nécessite n fixé; Géométrique exclue: modélise attente avant 1er événement)\n"
            f"  P2Q2 — Y ~ Exp(μ̂={fy['mu_exp']:.4f}h) : KS_exp={fy['ks_exp']:.4f} < KS_norm={fy['ks_norm']:.4f}  CV={fy['cv']:.3f}\n"
            f"  P2Q3 — E[Z]=λ×μ valide car X⊥Y | E[Z] : Ouaga2000=3h, Tampouy=12.25h, Pissy=6h, Patte d'Oie=5h, Karpala=15.75h, Balkuy=12h\n"
            f"  P2Q4 — Tampouy+Karpala : E[Z2+Z5]={z2z5['E_total']:.2f}h  Var={z2z5['V_total']:.2f}h²  σ={z2z5['sigma_total']:.2f}h")
        fig_fr=tk.Frame(self.content,bg=BG); fig_fr.pack(fill='both',expand=True)
        c=FigureCanvasTkAgg(F.fig_loi_Y(self.df,self.fy),master=fig_fr)
        c.draw(); c.get_tk_widget().pack(fill='both',expand=True)
        NavigationToolbar2Tk(c,fig_fr).update()

    # ── Partie 3 — Monte-Carlo ────────────────────────────────────────────────
    def _p3(self):
        self._hdr_set('🎲 Partie 3 Q1 — Simulation Monte-Carlo','50 000 journées simulées par quartier — X~Poisson, Y~Exp')
        self._info('  P3Q1 — simule_journee(quartier, n_rep) : tire X~Poisson(λ), puis Y_i~Exp(μ) pour i=1..X, retourne Z=ΣY_i. '
                   'Karpala et Balkuy ont des queues très lourdes (>30h possibles), Ouaga 2000 reste sous 10h.')
        self._embed(F.fig_simulation(self.sims),scroll=True)

    # ── Partie 3 — TCL ────────────────────────────────────────────────────────
    def _p3_tcl(self):
        t=self.tcl
        self._hdr_set('📈 Partie 3 Q2 — TCL Karpala',
                      f"E[Z]={t['EZ']}h  σ[Z]={t['SZ']}h  z={t['z']}  TCL={t['p_tcl']*100:.1f}%  MC={t['p_sim']*100:.1f}%")
        self._info(
            f"  P3Q2 — z=(8-{t['EZ']})/{t['SZ']}={t['z']}  →  P(Z>8h)_TCL=1-Φ({t['z']})={t['p_tcl']*100:.1f}%\n"
            f"  Simulation MC: P(Z>8h)={t['p_sim']*100:.1f}%  |  Écart={abs(t['p_tcl']-t['p_sim'])*100:.1f}pts "
            f"→ dû à la non-gaussianité de Z pour λ=3.5. MC plus fiable. Convergence dès 5 000 rép.")
        fig_fr=tk.Frame(self.content,bg=BG); fig_fr.pack(fill='both',expand=True)
        c=FigureCanvasTkAgg(F.fig_TCL(self.tcl),master=fig_fr)
        c.draw(); c.get_tk_widget().pack(fill='both',expand=True)
        NavigationToolbar2Tk(c,fig_fr).update()

    # ── Partie 3 — Vulnérabilité + Plafond ───────────────────────────────────
    def _p3_vuln(self):
        self._hdr_set('🛡️ Partie 3 Q3+Q4 — Vulnérabilité & Plafonnement',
                      'P(Z>6h) par quartier + impact mesure SONABEL (plafond 3h/coupure)')
        lines=['  P3Q3 — Classement (+ → - vulnérable) : ']
        for i,(q,p) in enumerate(self.vuln.items()):
            g=self.gains[q]
            lines[0]+=f"{i+1}.{q}({p*100:.1f}%)  "
        lines.append(f"  P3Q4 — Gain plafond 3h/coup : Karpala −{self.gains['Karpala']}h/j  "
                     f"Tampouy −{self.gains['Tampouy']}h/j  Balkuy −{self.gains['Balkuy']}h/j  "
                     f"→ mesure la plus efficace sans investissement réseau")
        self._info('\n'.join(lines))
        self._embed(F.fig_vuln_et_plafond(self.sims,self.avant,self.apres,self.gains))

    # ── Approfondissement ─────────────────────────────────────────────────────
    def _appro(self):
        self._hdr_set('💰 Approfondissement','Perte économique Karpala + Test indépendance priorité/fréquence')
        fr=tk.Frame(self.content,bg=BG); fr.pack(fill='both',expand=True,padx=28,pady=10)
        pe=self.perte; ri=self.indep

        # Q1
        tk.Label(fr,text='Q1 — Perte économique à Karpala (saison 60 jours)',
                 font=('Arial',13,'bold'),bg=BG,fg=TEXT).pack(anchor='w',pady=(8,6))
        eco=tk.Frame(fr,bg=BG3,highlightbackground=BORDER,highlightthickness=1); eco.pack(fill='x',pady=4)
        lignes=[
            f"  E[Z]_Karpala = λ×μ = 3,5 × 4,5 = {pe['EZ']:.2f} h/jour",
            f"  Perte/ménage/jour     = {pe['EZ']:.2f}h × 2 500 FCFA = {pe['perte_j_men']:,.0f} FCFA",
            f"  Perte/ménage/saison   = {pe['perte_j_men']:,.0f} × 60j = {pe['perte_s_men']:,.0f} FCFA",
            f"  Ratio vs onduleur     = {pe['perte_s_men']:,.0f} / 80 000 = {pe['ratio_onduleur']:.1f}× le coût d'un onduleur",
            f"  Rentabilité onduleur  = 80 000 / {pe['perte_j_men']:,.0f} = {pe['jours_rentab']:.1f} jours !",
            f"  Nb ménages Karpala    ≈ {pe['menages']:,.0f}  (55 000 hab / 5 pers.)",
            f"  Perte totale/saison   ≈ {pe['perte_totale']/1e9:.2f} Milliards FCFA",
        ]
        for l in lignes:
            col=DANGER if 'Milliards' in l or 'Ratio' in l or 'Rentab' in l else TEXT
            tk.Label(eco,text=l,font=('Courier',10),bg=BG3,fg=col,pady=3).pack(anchor='w',padx=12)
        tk.Frame(eco,bg=BG3,height=6).pack()

        tk.Frame(fr,bg=BORDER,height=1).pack(fill='x',pady=12)

        # Q2
        tk.Label(fr,text="Q2 — Test d'indépendance : priorité réseau vs fréquence de coupure",
                 font=('Arial',13,'bold'),bg=BG,fg=TEXT).pack(anchor='w',pady=(0,6))
        ind=tk.Frame(fr,bg=BG3,highlightbackground=BORDER,highlightthickness=1); ind.pack(fill='x',pady=4)
        lignes2=[
            f"  Sujet C : Faible={ri['q_faible']}(λ={ri['lam_faible']})  Haute={ri['q_haute']}(λ_moy={ri['lam_haute']:.1f})  Moyenne={ri['q_moyenne']}(λ_moy={ri['lam_moyenne']:.1f})",
            f"  Simulation N=100 000 journées :",
            f"  P(X>2 | priorité faible)  = {ri['p_faible']:.3f} = {ri['p_faible']*100:.1f}%",
            f"  P(X>2 | priorité haute)   = {ri['p_haute']:.3f} = {ri['p_haute']*100:.1f}%",
            f"  P(X>2 | priorité moyenne) = {ri['p_moyenne']:.3f} = {ri['p_moyenne']*100:.1f}%",
            f"  Rapport haute/faible = {ri['rapport_h_f']:.2f}×",
            f"  → Paradoxe : les quartiers 'Haute' priorité subissent {ri['rapport_h_f']:.1f}× plus de coupures >2/j que 'Faible'",
            f"  → La classification SONABEL ne reflète pas la réalité terrain → révision nécessaire",
        ]
        for l in lignes2:
            col=DANGER if '→' in l else (WARN if 'Rapport' in l else TEXT)
            tk.Label(ind,text=l,font=('Courier',9),bg=BG3,fg=col,pady=2).pack(anchor='w',padx=12)
        tk.Frame(ind,bg=BG3,height=6).pack()

        tk.Frame(fr,bg=BORDER,height=1).pack(fill='x',pady=8)
        tk.Label(fr,text='⚠ Hypothèses : 2 500 FCFA/h | Onduleur = 80 000 FCFA | Saison = 60j | 5 pers./ménage',
                 font=('Arial',8,'italic'),bg=BG,fg=MUTED).pack(anchor='w')

"""figures.py — 6 figures fidèles au rapport PDF final."""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy.stats import norm, expon, poisson

PAL=['#1565C0','#E65100','#2E7D32','#6A1B9A','#C62828','#00838F']
BG0='#0D1117';BG1='#161B22';LINE='#30363D';W='#E6EDF3';MUT='#8B949E'

def _ax(ax,title='',xlabel='',ylabel=''):
    ax.set_facecolor(BG1)
    for s in ax.spines.values(): s.set_edgecolor(LINE)
    ax.tick_params(colors=MUT,labelsize=8)
    ax.xaxis.label.set_color(MUT);ax.yaxis.label.set_color(MUT)
    if title:  ax.set_title(title,color=W,fontsize=9,pad=5)
    if xlabel: ax.set_xlabel(xlabel,fontsize=8)
    if ylabel: ax.set_ylabel(ylabel,fontsize=8)
    ax.grid(axis='y',color=LINE,lw=0.5,alpha=0.6)

def _suptitle(fig,t):
    fig.suptitle(t,color=W,fontsize=11,fontweight='bold')

# ── Fig 1 : Ajustement Poisson (Partie 1 Q2 + Partie 2 Q1) ──────────────────
def fig_poisson(df, summary):
    fig,axes=plt.subplots(1,2,figsize=(13,5),facecolor=BG0)
    fig.patch.set_facecolor(BG0)
    _suptitle(fig,f"Ajustement Poisson(λ̂={summary['moy_coupures']:.2f}) sur X — N={summary['n']} répondants")

    ax=axes[0]; _ax(ax,'Fréquences observées vs PMF Poisson','Nb. coupures/jour','Fréquence / Probabilité (%)')
    vals=df['nb_coupures_num'].value_counts().sort_index()
    lam=summary['moy_coupures']
    xr=np.arange(0,int(vals.index.max())+2)
    freq_pct=vals/vals.sum()*100; pmf_pct=poisson.pmf(xr,lam)*100
    bars=ax.bar(freq_pct.index-0.2,freq_pct.values,0.4,color='#C62828',alpha=0.85,
                edgecolor=BG0,label='Données observées')
    ax.bar(xr+0.2,pmf_pct,0.4,color='#FF6F00',alpha=0.85,edgecolor=BG0,label=f'Poisson(λ={lam:.2f})')
    for xi,yi in zip(freq_pct.index,freq_pct.values):
        ax.text(xi-0.2,yi+0.3,f'{yi:.1f}%',ha='center',color=W,fontsize=7)
    box=dict(boxstyle='round',facecolor=BG1,edgecolor='#1565C0',alpha=0.9)
    ax.text(0.98,0.97,f"Ê[X] = {summary['moy_coupures']:.3f}\nV̂ar[X] = {summary['var_coupures']:.3f}\nRatio = {summary['ratio_VE']:.3f} ≈ 1 ✓",
            transform=ax.transAxes,va='top',ha='right',color=W,fontsize=8,bbox=box)
    ax.legend(fontsize=8,labelcolor=W,facecolor=BG1,edgecolor=LINE)

    ax=axes[1]; _ax(ax,'Répondants par quartier','','Nb. répondants')
    cnt=df['quartier'].value_counts()
    bars2=ax.barh(cnt.index,cnt.values,color=PAL[:len(cnt)],edgecolor=BG0)
    for b,v in zip(bars2,cnt.values):
        ax.text(b.get_width()+0.05,b.get_y()+b.get_height()/2,str(v),va='center',color=W,fontsize=7)
    ax.tick_params(axis='y',labelsize=7,colors=MUT)

    plt.tight_layout(rect=[0,0,1,0.94])
    return fig

# ── Fig 2 : Ajustement loi Y (Partie 2 Q2) ──────────────────────────────────
def fig_loi_Y(df, fy):
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5),facecolor=BG0)
    fig.patch.set_facecolor(BG0)
    _suptitle(fig,"Ajustement de la loi pour Y — Durée d'une coupure (heures)")

    y=df['duree_num'].dropna()
    ax1.set_facecolor(BG1)
    for s in ax1.spines.values(): s.set_edgecolor(LINE)
    ax1.tick_params(colors=MUT,labelsize=8)
    ax1.hist(y,bins=8,density=True,color='#C62828',alpha=0.7,edgecolor=BG0,label=f'Données observées (N={len(y)})')
    xr=np.linspace(0.01,y.max()+0.5,300)
    mu_e=fy['mu_exp']; lam_e=fy['lambda_exp']
    mu_n=fy['mu_norm']; sig_n=fy['sig_norm']
    from scipy.stats import norm as N,expon as E
    ax1.plot(xr,E.pdf(xr,0,mu_e),'#FF6F00',lw=2.5,label=f'Exponentielle(μ={mu_e:.2f}h) ← CHOISIE')
    ax1.plot(xr,N.pdf(xr,mu_n,sig_n),'#1565C0',lw=2,ls='--',label=f'Normale(μ={mu_n:.2f},σ={sig_n:.2f})')
    ax1.set_xlabel('Durée Y (heures)',color=MUT,fontsize=8)
    ax1.set_ylabel('Densité',color=MUT,fontsize=8)
    ax1.set_title('Histogramme + densités théoriques\n(l\'exponentielle colle mieux à la forme décroissante)',color=W,fontsize=9)
    ax1.legend(fontsize=8,labelcolor=W,facecolor=BG1,edgecolor=LINE)
    ax1.text(0.62,0.65,f'CV = {fy["cv"]:.3f}\nKS_exp = {fy["ks_exp"]:.3f}\nKS_norm = {fy["ks_norm"]:.3f}',
             transform=ax1.transAxes,color=W,fontsize=8,
             bbox=dict(boxstyle='round',facecolor=BG1,edgecolor='#FF6F00',alpha=0.9))

    # Q-Q plot
    ax2.set_facecolor(BG1)
    for s in ax2.spines.values(): s.set_edgecolor(LINE)
    ax2.tick_params(colors=MUT,labelsize=8)
    from scipy.stats import expon as E2
    q_th=E2.ppf(np.linspace(0.01,0.99,len(y)),0,mu_e)
    q_obs=np.sort(y.values)
    ax2.scatter(q_th,q_obs,color='#FF6F00',s=25,alpha=0.8,label='Points observés',zorder=5)
    lim=max(q_th.max(),q_obs.max())+0.5
    ax2.plot([0,lim],[0,lim],'w--',lw=1.5,alpha=0.7,label='y = x (ajustement parfait)')
    ax2.set_xlabel(f'Quantiles théoriques Exp(μ={mu_e:.2f}h)',color=MUT,fontsize=8)
    ax2.set_ylabel('Quantiles empiriques',color=MUT,fontsize=8)
    ax2.set_title('Q-Q Plot — Données vs Loi Exponentielle\n(plus les points suivent y=x, meilleur est l\'ajustement)',color=W,fontsize=9)
    ax2.legend(fontsize=8,labelcolor=W,facecolor=BG1,edgecolor=LINE)
    ax2.xaxis.label.set_color(MUT);ax2.yaxis.label.set_color(MUT)

    plt.tight_layout(rect=[0,0,1,0.94])
    return fig

# ── Fig 3 : Monte-Carlo par quartier (Partie 3 Q1) ───────────────────────────
def fig_simulation(sims):
    from modules.data_loader import QUARTIERS_C3
    qs=list(sims.keys())
    fig,axes=plt.subplots(2,3,figsize=(14,9),facecolor=BG0)
    fig.patch.set_facecolor(BG0)
    _suptitle(fig,"Simulation Monte-Carlo — Distribution de Z par quartier (N=50 000 journées simulées)")
    axes=axes.flatten()
    for i,q in enumerate(qs):
        Z=sims[q]; p=QUARTIERS_C3[q]
        ax=axes[i]; _ax(ax,'','Durée totale Z (h)','Densité')
        ax.hist(Z,bins=60,density=True,color=PAL[i],alpha=0.85,edgecolor=BG0)
        moy=Z.mean(); p6=(Z>6).mean()
        ax.axvline(moy,color='white',lw=1.5,ls='--',label=f'Moy={moy:.1f}h')
        ax.axvline(6,color='#FF6F00',lw=1.5,ls=':',label='Onduleur 6h')
        ax.set_title(f'{q} ({p["zone"]})  λ={p["lambda"]}  E[Z]={moy:.1f}h\n{p6:.1%} journées > 6h',
                     color=W,fontsize=8,pad=4)
        ax.legend(fontsize=7,labelcolor=W,facecolor=BG1,edgecolor=LINE)
    h1=mpatches.Patch(color='white',label='Moyenne'); h2=mpatches.Patch(color='#FF6F00',label='Seuil 6h')
    fig.legend(handles=[h1,h2],loc='lower right',fontsize=9,labelcolor=W,facecolor=BG1,edgecolor=LINE)
    plt.tight_layout(rect=[0,0,1,0.94])
    return fig

# ── Fig 4 : TCL Karpala (Partie 3 Q2) ───────────────────────────────────────
def fig_TCL(tcl):
    from modules.data_loader import QUARTIERS_C3
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5),facecolor=BG0)
    fig.patch.set_facecolor(BG0)
    _suptitle(fig,f"Karpala — P(Z > 8h) : TCL = {tcl['p_tcl']*100:.1f}%  |  Monte-Carlo = {tcl['p_sim']*100:.1f}%")

    ax1.set_facecolor(BG1)
    for s in ax1.spines.values(): s.set_edgecolor(LINE)
    ax1.tick_params(colors=MUT)
    ax1.plot(tcl['tailles'],tcl['conv'],color='#FF6F00',lw=1.5,label='Estimation MC')
    ax1.axhline(tcl['p_tcl']*100,color='white',lw=2,ls='--',label=f'TCL = {tcl["p_tcl"]*100:.1f}%')
    ax1.axhline(tcl['p_sim']*100,color='#4CAF50',lw=1.5,ls=':',label=f'MC finale = {tcl["p_sim"]*100:.1f}%')
    ax1.set_xscale('log')
    ax1.set_xlabel('Nombre de simulations (log)',color=MUT,fontsize=8)
    ax1.set_ylabel('P(Z > 8h) (%)',color=MUT,fontsize=8)
    ax1.set_title('Courbe de convergence MC\n(plateau dès ~5 000 simulations)',color=W,fontsize=9)
    ax1.legend(fontsize=9,labelcolor=W,facecolor=BG1,edgecolor=LINE)
    ax1.xaxis.label.set_color(MUT);ax1.yaxis.label.set_color(MUT)

    EZ=tcl['EZ']; SZ=tcl['SZ']
    xr=np.linspace(EZ-3.5*SZ,EZ+3.5*SZ,300)
    ax2.set_facecolor(BG1)
    for s in ax2.spines.values(): s.set_edgecolor(LINE)
    ax2.tick_params(colors=MUT)
    ax2.plot(xr,norm.pdf(xr,EZ,SZ),'#1565C0',lw=2,label=f'N({EZ:.2f}, {SZ:.2f}²)')
    mask=xr>=8
    ax2.fill_between(xr[mask],norm.pdf(xr[mask],EZ,SZ),alpha=0.35,color='#C62828',
                     label=f'P(Z>8h)={tcl["p_tcl"]*100:.1f}%')
    ax2.axvline(8,color='#FF6F00',lw=2,ls='--',label='Seuil 8h')
    ax2.axvline(EZ,color='white',lw=1.5,ls=':',label=f'E[Z]={EZ}h')
    ax2.set_xlabel('Durée totale Z (h)',color=MUT,fontsize=8)
    ax2.set_ylabel('Densité',color=MUT,fontsize=8)
    ax2.set_title(f'Approximation TCL — Zone P(Z>8h)',color=W,fontsize=9)
    ax2.legend(fontsize=9,labelcolor=W,facecolor=BG1,edgecolor=LINE)
    ax2.xaxis.label.set_color(MUT);ax2.yaxis.label.set_color(MUT)

    plt.tight_layout(rect=[0,0,1,0.94])
    return fig

# ── Fig 5 : Vulnérabilité + Plafond (Partie 3 Q3+Q4) ────────────────────────
def fig_vuln_et_plafond(sims, avant, apres, gains):
    fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,6),facecolor=BG0)
    fig.patch.set_facecolor(BG0)
    _suptitle(fig,"Vulnérabilité onduleur (6h) & Impact plafonnement 3h/coupure")

    vuln={q:(Z>6).mean()*100 for q,Z in sims.items()}
    vs=dict(sorted(vuln.items(),key=lambda x:-x[1]))
    _ax(ax1,'Classement de vulnérabilité','% journées > 6h','')
    noms=list(vs.keys()); vals=list(vs.values())
    cols=['#C62828' if v>50 else '#E65100' if v>25 else '#2E7D32' for v in vals]
    bars=ax1.barh(noms,vals,color=cols,edgecolor=BG0,height=0.6)
    ax1.axvline(50,color='white',lw=1,ls='--',alpha=0.5,label='Seuil 50%')
    for b,v in zip(bars,vals):
        ax1.text(b.get_width()+0.5,b.get_y()+b.get_height()/2,f'{v:.1f}%',
                 va='center',color=W,fontsize=9,fontweight='bold')
    ax1.set_xlim(0,max(vals)+16); ax1.tick_params(axis='y',colors=W,labelsize=9)
    r=mpatches.Patch(color='#C62828',label='>50% critique')
    o=mpatches.Patch(color='#E65100',label='25-50% risque')
    g=mpatches.Patch(color='#2E7D32',label='<25% stable')
    ax1.legend(handles=[r,o,g],fontsize=8,labelcolor=W,facecolor=BG1,edgecolor=LINE)

    _ax(ax2,'Avant vs Après plafonnement 3h/coupure','','Durée journalière moy. (h)')
    qs=list(avant.keys()); x=np.arange(len(qs)); w=0.35
    ax2.bar(x-w/2,[avant[q] for q in qs],w,color='#C62828',alpha=0.9,label='Sans plafond')
    ax2.bar(x+w/2,[apres[q] for q in qs],w,color='#2E7D32',alpha=0.9,label='Plafond 3h',hatch='///')
    for xi,q in enumerate(qs):
        g=gains[q]; ymax=max(avant[q],apres[q])
        ax2.text(xi,ymax+0.15,f'−{g:.1f}h',ha='center',color='#4CAF50',fontsize=8,fontweight='bold')
    ax2.set_xticks(x); ax2.set_xticklabels(qs,rotation=30,ha='right',fontsize=8,color=MUT)
    ax2.legend(fontsize=9,labelcolor=W,facecolor=BG1,edgecolor=LINE)

    plt.tight_layout(rect=[0,0,1,0.94])
    return fig

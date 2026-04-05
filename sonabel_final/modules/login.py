"""login.py — Fenêtre d'identification SONABEL"""
import tkinter as tk, hashlib

COMPTES = {
    'admin':    hashlib.sha256(b'sonabel2026').hexdigest(),
    'etudiant': hashlib.sha256(b'igit2026').hexdigest(),
    'prof':     hashlib.sha256(b'prof123').hexdigest(),
}
BG,BG2,BORDER='#0D1117','#161B22','#30363D'
ACCENT,TEXT,MUTED,SUCCESS,DANGER='#1565C0','#E6EDF3','#8B949E','#2EA043','#F85149'

class LoginWindow:
    def __init__(self,on_success):
        self.on_success=on_success
        self.root=tk.Tk(); self.root.title('SONABEL — Identification')
        self.root.configure(bg=BG); self.root.resizable(False,False)
        w,h=420,540; sw=self.root.winfo_screenwidth(); sh=self.root.winfo_screenheight()
        self.root.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')
        self._build(); self.root.mainloop()

    def _entry(self,p,show=''):
        return tk.Entry(p,font=('Arial',11),bg=BG2,fg=TEXT,insertbackground=TEXT,
                        relief='flat',highlightbackground=BORDER,highlightthickness=1,show=show)

    def _build(self):
        tk.Frame(self.root,bg=ACCENT,height=5).pack(fill='x')
        card=tk.Frame(self.root,bg=BG2,highlightbackground=BORDER,highlightthickness=1)
        card.pack(padx=40,pady=22,fill='x')
        tk.Label(card,text='⚡',font=('Arial',38),bg=BG2,fg=ACCENT).pack(pady=(16,0))
        tk.Label(card,text='SONABEL',font=('Arial',22,'bold'),bg=BG2,fg=TEXT).pack()
        tk.Label(card,text='Analyse des Délestages — Ouagadougou',font=('Arial',9),bg=BG2,fg=MUTED).pack()
        tk.Label(card,text='EPO/IGIT — Probabilités & Statistiques 2025-2026',font=('Arial',8),bg=BG2,fg=MUTED).pack(pady=(0,14))
        f=tk.Frame(self.root,bg=BG); f.pack(padx=40,fill='x')
        tk.Label(f,text='Identifiant',font=('Arial',10,'bold'),bg=BG,fg=TEXT,anchor='w').pack(fill='x',pady=(0,3))
        self.ue=self._entry(f); self.ue.pack(fill='x',ipady=5,pady=(0,12))
        tk.Label(f,text='Mot de passe',font=('Arial',10,'bold'),bg=BG,fg=TEXT,anchor='w').pack(fill='x',pady=(0,3))
        self.pe=self._entry(f,show='●'); self.pe.pack(fill='x',ipady=5)
        self.sv=tk.BooleanVar(value=False)
        tk.Checkbutton(f,text='Afficher',variable=self.sv,
                       command=lambda:self.pe.config(show='' if self.sv.get() else '●'),
                       bg=BG,fg=MUTED,activebackground=BG,selectcolor=BG2,font=('Arial',8)).pack(anchor='w',pady=(4,12))
        self.err=tk.Label(f,text='',font=('Arial',9),bg=BG,fg=DANGER); self.err.pack(pady=(0,6))
        tk.Button(f,text='Se connecter →',font=('Arial',11,'bold'),bg=ACCENT,fg='white',
                  activebackground='#1976D2',relief='flat',cursor='hand2',pady=10,
                  command=self._login).pack(fill='x')
        hint=tk.Frame(self.root,bg=BG2,highlightbackground=BORDER,highlightthickness=1)
        hint.pack(padx=40,pady=16,fill='x')
        tk.Label(hint,text='Comptes de démonstration',font=('Arial',8,'bold'),bg=BG2,fg=MUTED).pack(pady=(8,2))
        for u,p in [('admin','sonabel2026'),('etudiant','igit2026'),('prof','prof123')]:
            tk.Label(hint,text=f'  {u}  /  {p}',font=('Courier',8),bg=BG2,fg=MUTED).pack(anchor='w',padx=12)
        tk.Frame(hint,bg=BG2,height=8).pack()
        self.root.bind('<Return>',lambda e:self._login()); self.ue.focus_set()

    def _login(self):
        u=self.ue.get().strip().lower()
        ph=hashlib.sha256(self.pe.get().encode()).hexdigest()
        if u in COMPTES and COMPTES[u]==ph:
            self.err.config(text='✓ Connexion réussie !',fg=SUCCESS)
            self.root.after(600,lambda:[self.root.destroy(),self.on_success()])
        else:
            self.err.config(text='✗ Identifiant ou mot de passe incorrect.',fg=DANGER)
            self.pe.delete(0,'end')

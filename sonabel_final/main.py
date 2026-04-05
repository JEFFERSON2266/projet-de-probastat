"""
main.py — Point d'entrée SONABEL
Sujet C final — EPO/IGIT — 2025-2026

Lancement : python main.py

Quartiers C2/C3 :
  Z1 Ouaga 2000  Faible   λ=1.5 μ=2.0h
  Z2 Tampouy     Moyenne  λ=3.5 μ=3.5h
  Z3 Pissy       Moyenne  λ=2.0 μ=3.0h
  Z4 Patte d'Oie Haute    λ=2.0 μ=2.5h
  Z5 Karpala     Moyenne  λ=3.5 μ=4.5h
  Z6 Balkuy      Haute    λ=3.0 μ=4.0h

Comptes : admin/sonabel2026  etudiant/igit2026  prof/prof123
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from modules.login import LoginWindow
from modules.dashboard import Dashboard

if __name__ == '__main__':
    LoginWindow(on_success=lambda: Dashboard())

"""Comparer les résultats avant/après amélioration"""

# Lire les deux fichiers
with open('test_results.txt', 'r', encoding='latin-1') as f:
    before = f.read()

with open('test_results_final.txt', 'r', encoding='latin-1') as f:
    after = f.read()

# Extraire les métriques
import re

def extract_problems(text):
    matches = re.findall(r'Problemes detectes: (\d+)', text)
    return [int(m) for m in matches]

def extract_palatability(text):
    matches = re.findall(r'Palatabilit.: ([\d.]+)/100', text)
    return [float(m) for m in matches]

def extract_portions_issues(text):
    pattern = r'\[X\] (.+?): (\d+)g trop petit'
    return re.findall(pattern, text)

before_problems = extract_problems(before)
after_problems = extract_problems(after)

before_palatability = extract_palatability(before)
after_palatability = extract_palatability(after)

before_portions = extract_portions_issues(before)
after_portions = extract_portions_issues(after)

print("=" * 80)
print("COMPARAISON AVANT/APRÈS AMÉLIORATIONS")
print("=" * 80)

print("\n1. NOMBRE DE PROBLÈMES DÉTECTÉS")
print(f"   Avant: {before_problems}")
print(f"   Après: {after_problems}")
print(f"   Amélioration: {[b-a for b, a in zip(before_problems, after_problems)]}")

print("\n2. SCORE DE PALATABILITÉ")
print(f"   Avant: {[f'{p:.1f}' for p in before_palatability]}")
print(f"   Après: {[f'{p:.1f}' for p in after_palatability]}")
print(f"   Amélioration: {[f'+{a-b:.1f}' if a > b else f'{a-b:.1f}' for b, a in zip(before_palatability, after_palatability)]}")

print("\n3. PORTIONS < 30g")
print(f"   Avant: {len(before_portions)} cas")
print(f"   Après: {len(after_portions)} cas")
print(f"   Réduction: {len(before_portions) - len(after_portions)} cas ({((len(before_portions) - len(after_portions)) / len(before_portions) * 100):.1f}%)")

print("\n4. PORTIONS < 30g DÉTAIL")
print("\n   Avant (échantillon):")
for food, qty in before_portions[:10]:
    print(f"      - {food}: {qty}g")

print("\n   Après (échantillon):")
for food, qty in after_portions[:10]:
    print(f"      - {food}: {qty}g")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

avg_before_prob = sum(before_problems) / len(before_problems) if before_problems else 0
avg_after_prob = sum(after_problems) / len(after_problems) if after_problems else 0
avg_before_pal = sum(before_palatability) / len(before_palatability) if before_palatability else 0
avg_after_pal = sum(after_palatability) / len(after_palatability) if after_palatability else 0

print(f"\nProblèmes moyens: {avg_before_prob:.1f} → {avg_after_prob:.1f} ({avg_after_prob - avg_before_prob:+.1f})")
print(f"Palatabilité moyenne: {avg_before_pal:.1f} → {avg_after_pal:.1f} ({avg_after_pal - avg_before_pal:+.1f})")
print(f"Portions < 30g: {len(before_portions)} → {len(after_portions)} ({len(after_portions) - len(before_portions):+d})")

if avg_after_prob < avg_before_prob:
    print("\n✓ AMÉLIORATION des problèmes détectés")
else:
    print("\n✗ PAS d'amélioration des problèmes")

if avg_after_pal > avg_before_pal:
    print("✓ AMÉLIORATION de la palatabilité")
else:
    print("✗ PAS d'amélioration de la palatabilité")

if len(after_portions) < len(before_portions):
    print("✓ RÉDUCTION des portions aberrantes")
else:
    print("✗ PAS de réduction des portions aberrantes")

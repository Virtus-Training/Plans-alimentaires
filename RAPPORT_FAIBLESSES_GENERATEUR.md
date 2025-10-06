# Rapport d'Analyse Avancée - Faiblesses du Générateur de Repas

## Méthodologie

**Tests effectués** : 5 profils nutritionnels × 7 jours = 35 plans journaliers (140 repas au total)

**Profils testés** :
1. Standard (2000 kcal, 150g protéines)
2. Haute protéine (2000 kcal, 180g protéines)
3. Faible glucides (2000 kcal, 100g glucides)
4. Végétarien équilibré (1800 kcal)
5. Gain musculaire (2500 kcal, 200g protéines)

**Analyses effectuées** :
- Diversité des aliments
- Cohérence nutritionnelle
- Respect des règles de palatabilité (féculents)
- Cohérence des tailles de repas
- Équilibre des catégories
- Détection d'anomalies

---

## 🔴 FAIBLESSES CRITIQUES

### 1. Dépassement Systématique des Glucides (CRITIQUE)

**Problème** : Tous les profils dépassent significativement leur cible de glucides.

| Profil | Cible Glucides | Moyenne Réelle | Écart |
|--------|---------------|----------------|-------|
| Standard | 200g | 270g | **+35%** |
| Haute protéine | 150g | 212g | **+41%** |
| Faible glucides | 100g | 171g | **+71%** |
| Végétarien | 220g | 290g | **+32%** |
| Gain musculaire | 250g | 320g | **+28%** |

**Impact** :
- Impossible de suivre un régime low-carb
- Déséquilibre macro pour tous les profils
- Profil "Faible glucides" avec +71% de glucides est **totalement inefficace**

**Cause probable** :
- Algorithme privilégie trop les aliments riches en glucides
- Poids insuffisant des glucides dans le score macro
- Pas de contrainte stricte sur le dépassement des glucides

---

### 2. Variance Calorique Excessive sur les Collations (CRITIQUE)

**Problème** : Les collations (snacks) dépassent systématiquement leur cible de **200-500%**.

**Exemples** :
- Standard Jour 1 : 400 kcal au lieu de 95 kcal (écart **+321%**)
- Végétarien Jour 1 : 540 kcal au lieu de 86 kcal (écart **+531%**)
- Haute protéine Jour 1 : 345 kcal au lieu de 95 kcal (écart **+263%**)

**Impact** :
- Distribution calorique journalière déséquilibrée
- Collations deviennent des "demi-repas"
- Risque de suralimentation
- Difficulté à respecter les cibles caloriques totales

**Cause probable** :
- Target_percentage de 0.05 (5%) trop faible
- Algorithme compense en ajoutant plus d'aliments
- Nombre minimum d'aliments (5) incompatible avec petit repas

---

### 3. Dépassement Calorique Global (MAJEUR)

**Problème** : Tous les profils dépassent systématiquement leur cible calorique.

| Profil | Cible Calories | Moyenne Réelle | Écart |
|--------|---------------|----------------|-------|
| Standard | 2000 kcal | 2396 kcal | **+20%** |
| Haute protéine | 2000 kcal | 2257 kcal | **+13%** |
| Faible glucides | 2000 kcal | 2249 kcal | **+12%** |
| Végétarien | 1800 kcal | 2137 kcal | **+19%** |
| Gain musculaire | 2500 kcal | 2875 kcal | **+15%** |

**Impact** :
- Prise de poids non désirée pour profils perte de poids
- Plans inadaptés pour déficit calorique
- Écart moyen de +15% systématique

**Cause probable** :
- Tolérance trop permissive (15%)
- Pas de correction à la baisse des portions
- Accumulation des petits dépassements sur 4 repas

---

## 🟡 FAIBLESSES MODÉRÉES

### 4. Violations de la Règle "Un Féculent" (MODÉRÉ)

**Problème** : Certains profils violent encore la règle d'un seul féculent par repas.

**Résultats** :
- Standard : 100% conformité ✅
- Haute protéine : 96.4% conformité (1 violation)
- Faible glucides : 100% conformité ✅
- **Végétarien : 89.3% conformité (3 violations)** ⚠️
- Gain musculaire : 100% conformité ✅

**Violations détectées** :
- Végétarien Jour 2 lunch : Patate douce + Millet
- Végétarien Jour 6 dinner : Boulgour + Quinoa rouge
- Végétarien Jour 7 dinner : Boulgour + Quinoa rouge
- Haute protéine Jour 6 lunch : Boulgour (2 portions séparées)

**Impact** :
- 10.7% des repas végétariens ne respectent pas la règle
- Problème récurrent avec quinoa/boulgour/millet
- Palatabilité compromise

**Cause probable** :
- Règle stricte contournée dans certains cas
- Catégorisation ambiguë de certains féculents
- Algorithme privilégie l'atteinte des macros sur la cohérence

---

### 5. Répétitivité Excessive de Certains Aliments (MODÉRÉ)

**Problème** : Certains aliments reviennent très fréquemment (jusqu'à 10×/semaine).

**Aliments les plus répétés** :
- Tomates : jusqu'à 10× sur 7 jours (5.4% de tous les aliments)
- Grenade (arilles) : jusqu'à 10× sur 7 jours
- Lait de soja : jusqu'à 9× sur 7 jours
- Courge butternut : jusqu'à 9× sur 7 jours

**Impact** :
- Monotonie alimentaire
- Lassitude possible
- Manque de variété nutritionnelle

**Statistiques** :
- Aliments uniques : 49-56 sur 108 disponibles (45-52%)
- Répétition moyenne : 3.3-3.9× par aliment
- Top 5 aliments : 15-25% du total des portions

**Cause probable** :
- Système `used_foods` se réinitialise trop tôt
- Algorithme favorise toujours les mêmes aliments "optimaux"
- Pas assez de randomisation

---

### 6. Nombre d'Aliments Incohérent par Type de Repas (MINEUR)

**Problème** : Tous les petit-déjeuners et collations ont exactement 9 aliments.

**Observations** :
- Breakfast : 9.0 ± 0.0 aliments (TOUS identiques)
- Snack : 9.0 ± 0.0 aliments (TOUS identiques)
- Lunch : 5.1-6.1 ± 0.4-2.0 aliments (variable)
- Dinner : 5.0-6.4 ± 0.0-1.9 aliments (variable)

**Impact** :
- Manque de variété dans la structure des repas
- Petit-déjeuner toujours "complexe" avec 9 composants
- Pas d'adaptation selon les besoins

**Cause probable** :
- max_foods fixé à 9 pour tous les repas
- Algorithme atteint systématiquement le maximum
- Pas de variation aléatoire du nombre d'aliments

---

### 7. Portions Très Petites (<20g) pour Certains Aliments (MINEUR)

**Problème** : Quelques portions de 10g détectées (beurre, huile).

**Exemples** :
- Faible glucides Jour 1 dinner : Beurre = 10g
- Faible glucides Jour 4 dinner : Huile d'olive = 10g

**Impact** :
- Portions peu pratiques à mesurer
- Contribution nutritionnelle marginale
- Complexité de préparation

**Note** : Limité aux matières grasses, ce qui est acceptable.

---

## 🟢 POINTS FORTS

### 1. Cohérence des Protéines ✅

**Très bonne précision** sur les protéines pour la plupart des profils :
- Haute protéine : **+2.8%** seulement
- Gain musculaire : **+4.5%**
- Végétarien : **+9.3%**

### 2. Cohérence des Lipides ✅

**Bon contrôle** des lipides :
- Végétarien : **+2.7%**
- Faible glucides : **+5.0%**

### 3. Règle Féculents Globalement Respectée ✅

**Taux de conformité moyen : 97.1%** sur 140 repas
- 4 violations sur 140 repas (2.9%)
- Amélioration significative par rapport à avant

### 4. Diversité Acceptable ✅

**49-56 aliments uniques** utilisés sur 108 disponibles (45-52%)
- Bon équilibre entre variété et répétition
- Pas de mono-alimentation

---

## 📊 RECOMMANDATIONS PRIORITAIRES

### Priorité 1 - Critique (à corriger immédiatement)

#### 1.1 Revoir l'algorithme de gestion des glucides
**Actions** :
- Augmenter le poids des glucides dans le score macro (actuellement 1.0, passer à 1.5)
- Ajouter une pénalité exponentielle pour dépassement glucides
- Filtrer les aliments trop riches en glucides pour profil low-carb

#### 1.2 Recalibrer les collations
**Actions** :
- Réduire min_foods pour les snacks (passer de 5 à 2-3)
- Augmenter target_percentage des snacks (0.05 → 0.10)
- Ou supprimer les collations si <150 kcal

#### 1.3 Resserrer la tolérance calorique
**Actions** :
- Passer la tolérance de 15% à 10% maximum
- Appliquer correction à la baisse sur le dernier repas si dépassement
- Vérifier l'accumulation journalière plus strictement

### Priorité 2 - Importante (à améliorer)

#### 2.1 Renforcer la règle anti-multi-féculents
**Actions** :
- Revoir la détection pour millet/quinoa/boulgour (ajuster STARCH_KEYWORDS)
- Empêcher COMPLÈTEMENT l'ajout de 2e féculent (pas de contournement)
- Tester spécifiquement sur profil végétarien

#### 2.2 Améliorer la variété
**Actions** :
- Augmenter le poids du variety_score (25% → 30%)
- Ne réinitialiser used_foods que tous les 2 jours au lieu de chaque jour
- Ajouter bonus pour aliments jamais utilisés

### Priorité 3 - Améliorations (si temps disponible)

#### 3.1 Varier le nombre d'aliments
**Actions** :
- Randomiser max_foods entre min+2 et max (ex: 5-9 au lieu de toujours 9)
- Adapter selon le type de repas (breakfast: 5-7, lunch: 5-8, snack: 2-4)

#### 3.2 Créer des profils de distribution
**Actions** :
- Breakfast simple : 5-6 aliments
- Breakfast complet : 7-9 aliments
- Permettre à l'utilisateur de choisir

---

## 🎯 CONCLUSION

### Synthèse des Problèmes

1. **Gestion des glucides défaillante** (tous profils +28% à +71%)
2. **Collations surdimensionnées** (écarts +200% à +500%)
3. **Dépassement calorique systématique** (+12% à +20%)
4. **Quelques violations palatabilité** (3-4 cas sur 140 repas)
5. **Répétitivité modérée** de certains aliments

### Score Global du Générateur

| Critère | Score | Commentaire |
|---------|-------|-------------|
| Protéines | 8/10 | ✅ Excellent |
| Lipides | 8/10 | ✅ Très bon |
| **Glucides** | **3/10** | ❌ **Problème majeur** |
| Calories totales | 5/10 | ⚠️ Dépassement systématique |
| Palatabilité (féculents) | 8.5/10 | ✅ Très bon (97% conformité) |
| Diversité | 7/10 | ✅ Acceptable |
| Cohérence portions | 6/10 | ⚠️ Collations problématiques |

**SCORE GLOBAL : 6.5/10**

### Verdict

Le générateur est **fonctionnel mais nécessite des corrections urgentes** sur :
1. La gestion des glucides (priorité absolue)
2. Le calibrage des collations
3. La tolérance calorique

Les améliorations de palatabilité (règle féculents) sont **réussies à 97%** ✅

Une fois ces corrections apportées, le générateur pourrait atteindre **8.5-9/10**.

---

## 📋 FICHIERS GÉNÉRÉS

- `test_advanced_analysis.py` : Suite de tests avancés (6 analyses)
- `RAPPORT_FAIBLESSES_GENERATEUR.md` : Ce rapport

---

*Rapport généré le : 2025-10-05*
*Version du générateur testée : FoodBasedGenerator (algorithme hybride, sans ILP)*

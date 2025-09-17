# Dashboard 2 - Affichage Plein Écran

## Vue d'ensemble

Le Dashboard 2 utilise maintenant un système d'affichage plein écran avec rotation automatique de **3 minutes par bloc**.

## Blocs disponibles (5 au total)

1. **👥 Disponibilité Équipe** - TeamAvailability
2. **📅 Planning Hebdomadaire** - WeeklyPlanning  
3. **✅ Tâches Basecamp** - TodosList
4. **📹 Vidéo Facebook** - FacebookVideo
5. **💰 Flux de Trésorerie** - CashFlowMonitor

## Fonctionnalités

### Rotation automatique
- Chaque bloc est affiché pendant **3 minutes (180 secondes)**
- Transition fluide entre les blocs avec animations
- Rotation en boucle continue

### Navigation manuelle
- **Boutons de navigation** : Flèches gauche/droite sur les côtés
- **Touches clavier** : 
  - `←` (flèche gauche) : Bloc précédent
  - `→` (flèche droite) : Bloc suivant

### Indicateurs visuels
- **Indicateur central** : Nom du bloc actuel + icône + progression (1/5, 2/5, etc.)
- **Compteur de temps** : Temps restant avant le prochain bloc (format MM:SS)
- **Barre de progression** : Barre en bas de l'écran qui se remplit progressivement
- **Points de navigation** : Indicateurs visuels pour chaque bloc

## Configuration

Le layout est configuré dans `frontend/src/dashboard2/App.tsx` :

```tsx
<Dashboard2FullscreenLayout
  teamAvailability={<TeamAvailability />}
  weeklyPlanning={<WeeklyPlanning />}
  basecampTodos={<TodosList />}
  facebookVideo={<FacebookVideo />}
  cashFlow={<CashFlowMonitor />}
  rotationInterval={180} // 3 minutes en secondes
/>
```

## Avantages

- **Affichage optimal** : Chaque bloc utilise tout l'espace disponible
- **Lisibilité améliorée** : Plus de détails visibles sur chaque composant
- **Navigation intuitive** : Contrôles visuels et clavier
- **Feedback temporel** : L'utilisateur sait toujours combien de temps reste
- **Expérience immersive** : Focus sur un seul bloc à la fois

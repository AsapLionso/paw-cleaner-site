# Paw Cleaner — Site public

Landing page officielle de [Paw Cleaner](https://pawcleaner.app), servie statiquement via GitHub Pages. Aucune dépendance, aucun build step : HTML/CSS/JS vanilla.

## Structure

```
index.html          Landing page
support/index.html  Page support (/support)
privacy/index.html  Politique de confidentialité (/privacy)
legal/index.html    Mentions légales (/legal)
404.html            Page d'erreur
assets/
  css/style.css      Design system (tokens repris de theme/index.ts de l'app)
  js/main.js         Nav mobile + reveal-on-scroll (respecte prefers-reduced-motion)
  img/               Logo, favicons, screenshots, mascotte, grain, OG image
  fonts/             Manrope (woff2, auto-hébergée)
CNAME                Domaine custom GitHub Pages (pawcleaner.app)
robots.txt / sitemap.xml
```

## Déploiement

Poussé sur `main`, servi via GitHub Pages (Settings → Pages → branch `main` / root). Le fichier `CNAME` déclare le domaine custom.

## Repo séparé du projet mobile

Ce site est volontairement un repo distinct de l'application PurrClean/Paw Cleaner (React Native/Expo) : aucune dépendance croisée, aucun risque pour le build iOS.

## Placeholder App Store

Les CTA "Download" pointent vers `#` et portent l'attribut `data-app-store-cta` — à remplacer par l'URL réelle de l'App Store dès la publication de l'app (`grep -rl data-app-store-cta .`).

## Mentions légales — en attente

`/legal/` contient un gabarit avec des champs `[TO COMPLETE]` (identité légale de l'éditeur). À compléter avant soumission App Store — voir le même gabarit côté app (`src/screens/LegalNoticeScreen.tsx`).

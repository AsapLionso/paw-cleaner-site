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

## Mentions légales — complètes

`/legal/` porte l'identité légale de l'éditeur (entrepreneur individuel, adresse, SIREN/SIRET, téléphone, contact), l'hébergeur et les conditions d'utilisation. Complété le 2026-08-18.

**Deux règles à tenir :**

1. **Ces informations existent en double**, ici et dans l'app (`src/i18n/locales/{fr,en}.ts`, clé `legalScreen`). Toute correction se fait des deux côtés dans le même geste — une divergence sur des mentions légales ne se remarque qu'à la lecture croisée, donc jamais.
2. **Les conditions d'utilisation décrivent la v1** : application gratuite, sans publicité, sans achat intégré, EULA standard d'Apple. Elles seront à réécrire dès qu'un achat intégré sera réellement disponible.

L'hébergeur indiqué (GitHub Pages) a été vérifié sur le service en ligne — enregistrements A dans la plage GitHub Pages, en-tête `server: GitHub.com` — et non déduit de la présence du fichier `CNAME`.

## Sous-projet `react/`

Le dossier `react/` est un projet React/TypeScript/Tailwind/shadcn autonome, séparé du reste du site — il ne fait **pas** partie du site publié tel quel. Voir `react/README.md` pour le détail. Le site principal ci-dessus reste sans dépendance ni build step.

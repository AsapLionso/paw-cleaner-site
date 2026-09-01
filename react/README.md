# paw-cleaner-site-react

Sous-projet React/TypeScript autonome, isolé du reste de `paw-cleaner-site`
(qui reste un site statique HTML/CSS/JS sans dépendance ni build step — voir
le `README.md` racine). Créé pour un seul besoin : un composant "Témoignages"
(colonnes de cartes qui défilent, animé avec `motion`) qui nécessite React +
Tailwind + shadcn/ui, sans imposer cette stack au reste du site.

## Pourquoi un sous-projet séparé plutôt qu'une migration du site

Migrer l'intégralité du site (nav, hero, gestures, features, footer...) vers
React aurait été un risque disproportionné pour un seul composant, et aurait
nécessité un pipeline de build (GitHub Actions) pour continuer à publier sur
GitHub Pages. À la place :

- Ce dossier se build **en local** (`npm run build` → `react/dist/`).
- Le bundle compilé n'est **pas encore** intégré au site — voir "Activer le
  composant" plus bas.
- `src/index.css` importe Tailwind **sans `preflight`** (le reset global) :
  volontaire, pour ne jamais entrer en conflit avec `assets/css/style.css` du
  site principal le jour où ce composant y est monté.

## Structure

```
components.json              Config shadcn/ui (dossier composants : src/components/ui)
src/
  components/
    ui/testimonials-columns-1.tsx   Composant fourni (copie, avec le type Testimonial
                                     ajouté — l'original référençait `typeof testimonials`
                                     sans jamais le déclarer, ce qui ne compilait pas)
    Testimonials.tsx                Wrapper de section, tableau de données vide (voir plus bas)
  lib/utils.ts                Helper cn() (clsx + tailwind-merge), convention shadcn
  App.tsx, main.tsx            Aperçu de développement (npm run dev), données factices
                                locales à App.tsx, jamais utilisées côté site
  index.css                    Tailwind (theme + utilities, sans preflight)
```

## Contenu des témoignages — décision du 2026-08-10

Le composant fourni contenait 9 faux témoignages (noms fictifs, photos
placeholder d'un service tiers, texte générique sans rapport avec Paw
Cleaner). Paw Cleaner n'a pas encore d'utilisateurs réels (pas publiée sur
l'App Store) — afficher de faux avis clients serait trompeur. Décision :
`Testimonials.tsx` exporte un tableau `testimonials` **vide**. Ne jamais y
remettre de contenu fabriqué.

## Activer le composant sur le site (à faire plus tard)

Quand de vrais témoignages existent (App Store, retours beta testeurs) :

1. Remplir le tableau `testimonials` dans `src/components/Testimonials.tsx`
   avec du contenu réel (photos hébergées dans `assets/img/` du site
   principal, jamais un service tiers type `randomuser.me` — cohérent avec le
   reste du site, zéro dépendance externe).
2. `npm run build` → copier `dist/assets/*.js` et `dist/assets/*.css` dans
   `assets/` à la racine du site.
3. Ajouter un point de montage dans `index.html` (`<div id="testimonials-root">`)
   à l'endroit voulu, et charger le bundle compilé avec un `<script type="module">`.
4. Retirer `react/dist/` du `.gitignore` une fois prêt à committer le bundle.

## Développement

```bash
npm install
npm run dev     # aperçu local avec données factices (App.tsx)
npm run build   # build de production dans dist/
```

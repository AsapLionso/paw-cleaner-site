# Paw Cleaner — Site public

Landing page officielle de [Paw Cleaner](https://pawcleaner.app), servie statiquement via GitHub Pages. Aucune dépendance, aucun build step : HTML/CSS/JS vanilla.

## Structure

Le site est **en français d'abord** (`/`), avec une version anglaise complète (`/en/`). Chaque page a sa
jumelle dans l'autre langue : `hreflang`, pastille FR/EN dans la barre, lien dans le menu mobile et le pied.

```
index.html                    Landing, français (/)
en/index.html                 Landing, anglais (/en/)
aide/index.html               Aide (/aide/)                      ↔ support/index.html (/support/)
confidentialite/index.html    Confidentialité (/confidentialite/) ↔ privacy/index.html (/privacy/)
mentions-legales/index.html   Mentions légales (/mentions-legales/) ↔ legal/index.html (/legal/)
404.html                      Page d'erreur, bilingue
assets/
  css/style.css      Design system (tokens repris de theme/index.ts et warmPalette.ts de l'app)
  js/main.js         Nav mobile + reveal-on-scroll (respecte prefers-reduced-motion)
  js/companion.js    Monde du Compagnon : clignement du chat, marches de pixels, coffre, scènes
  js/cat-cursor.js   Curseur patte (passe à l'encre sur le monde chaud)
  img/               Logo, favicons (icône de l'app), grain, images de partage (og-image.jpg FR, og-image-en.jpg EN)
  img/app/fr, en/    Captures de l'app, une série par langue (accueil, tri, salon : iPhone, DA Paw ; boutique : build 9 ; shot-kibble n'est plus affichée)
  img/paw/           Objets 3D mats de la DA Paw (pictos, chat au cadenas), tirés de l'app
  video/             Les chats animés de l'app (boucles sur noir pur, fondues par « éclaircir ») + leur première image
  img/pixel/         Sprites de l'app à leur résolution d'art (chat du jour 0, silhouettes, coffres, crocks, jeux)
  img/shop/          Les 24 objets de la boutique montrés sur la page
  fonts/             Manrope (woff2) + Silkscreen (ttf, OFL — la police pixel de l'app)
tools/
  sync-app-assets.py Tire captures, sprites, objets de boutique et police depuis le dépôt de l'app (manuel)
  make-og-images.py  Refait les deux images de partage à partir des ressources du site
  da-paw-web.py      DA Paw : captures iPhone, objets 3D, boucles des chats, icônes (manuel)
_config.yml          Exclut README, tools/ et react/ de la publication GitHub Pages
CNAME                Domaine custom GitHub Pages (pawcleaner.app)
robots.txt / sitemap.xml (avec les alternates hreflang)
```

Les adresses anglaises `/support/`, `/privacy/` et `/legal/` n'ont pas changé : ce sont celles déclarées
dans App Store Connect.

## Déploiement

Poussé sur `main`, servi via GitHub Pages (Settings → Pages → branch `main` / root). Le fichier `CNAME` déclare le domaine custom.

## Repo séparé du projet mobile

Ce site est volontairement un repo distinct de l'application PurrClean/Paw Cleaner (React Native/Expo) : aucune dépendance croisée, aucun risque pour le build iOS.

## Placeholder App Store

Les CTA "Download" pointent vers `#` et portent l'attribut `data-app-store-cta` — à remplacer par l'URL réelle de l'App Store dès la publication de l'app (`grep -rl data-app-store-cta .`).

## Mentions légales — complètes

`/legal/` porte l'identité légale de l'éditeur (entrepreneur individuel, adresse, SIREN/SIRET, téléphone, contact), l'hébergeur et les conditions d'utilisation. Complété le 2026-08-18.

**Deux règles à tenir :**

1. **Ces informations existent en plusieurs exemplaires** : `/mentions-legales/` et `/confidentialite/` (français), `/legal/` et `/privacy/` (anglais), et l'app (`src/i18n/locales/{fr,en}.ts`, clés `legalScreen` et `privacyScreen`). Toute correction se fait partout dans le même geste — une divergence sur des mentions légales ne se remarque qu'à la lecture croisée, donc jamais.
2. **Les conditions d'utilisation décrivent la v1** : application gratuite, sans publicité, sans achat intégré, EULA standard d'Apple. Elles seront à réécrire dès qu'un achat intégré sera réellement disponible.

L'hébergeur indiqué (GitHub Pages) a été vérifié sur le service en ligne — enregistrements A dans la plage GitHub Pages, en-tête `server: GitHub.com` — et non déduit de la présence du fichier `CNAME`.

## Build 9 : le monde du Compagnon (2026-09-17)

La page présente l'app telle qu'elle est en build 9 : le tri (sombre, l'identité d'origine du site) et
l'onglet Familier (chaud, en pixel art), exactement comme l'app passe d'un monde à l'autre. Le passage se
fait par une frange de marches de pixels qui se pose au défilement.

**Le propos** : « Qui a dit que trier ses photos était ennuyeux ? » — le chat qui donne envie de trier sa galerie, un jour après l'autre. Héros, rituel du
jour (choisir, swiper, il grandit, revenir demain), puis le monde du familier (il t'attend, sa maison et la
boutique, les jeux, les quêtes et le coffre), puis le geste, les fonctions et la confidentialité.
**Aucun nom de marque tierce** pour décrire le principe : on parle de petit chat, de familier, de compagnon.

**Rien n'est redessiné pour le web.** Sprites, objets de boutique, police et palette viennent du dépôt de
l'app (branche `chantier/da-piece-principale`) par `tools/sync-app-assets.py` ; les sprites sur grille exacte
sont ramenés à leur résolution d'art et agrandis en `image-rendering: pixelated`.

**Chaque affirmation est vérifiée dans le code de l'app** (relevé du 2026-09-17, seuil revu le 2026-09-21, boutique le 2026-09-24) : le chat arrive le premier
jour où l'on atteint 30 actions ; il gagne un jour par jour de tri (ouvrir l'app ne compte pas) ; nouvelles
allures aux jours 7, 15, 30, 90 et 180 ; Croquettes et Memory dès le jour 0, pêche et cuisine au jour 7,
dehors au jour 30 ; **641 articles proposés en boutique** (497 objets à poser, 144 murs et sols ; le script
les recompte) ; Croquettes 42 s une fois par jour ; Memory six paliers ; pêche cinq appâts par jour ; jusqu'à
cinq quêtes par jour payées en diamants ; un coffre = 50 à 150 crocks + un rare, épique ou légendaire ; un
crock commun pour dix photos triées. **À revérifier à chaque build** qui touche ces règles.

Choix à connaître :
- **Seul le chat du jour 0 se montre** dans la frise et les images de partage. Les cinq allures suivantes
  sont en silhouette (celles de l'app) ; leurs sprites ne sont pas publiés. Exception voulue (fondateur,
  2026-09-24) : la capture du salon, prise sur son iPhone, montre son chat à 30 jours.
- **La page anglaise reprend les captures françaises** pour l'instant (fondateur, 2026-09-24).
- **Aucun chat pixel sur fond noir** : tous les chats de l'app sont noirs, ils disparaîtraient.
- **La boutique remplace les univers du dehors** : un nombre, les quatre raretés de crocks et 24 objets
  choisis (liste `SHOWCASE` du script), noms tirés des traductions de l'app.
- **Fonctions** : photos, vidéos, doublons. Favori et zoom restent dans la section du geste.
- **La photo de la capture du tri** est celle déjà publiée sur le site (réinjectée dans le simulateur) ; les
  photos d'exemple d'Apple du simulateur ne sont pas utilisées.
- **Pas de mention des publicités ni des achats** : désactivés en build 9, prévus plus tard.

Rafraîchir après une nouvelle build :
1. Captures, en français puis en anglais (clé `pawcleaner.locale` = `en`) : état de démonstration avec
   `pawcleaner.companion.ageFloor` = `3` et `pawcleaner.companion.lastSeenStage` = `kitten` (le chaton),
   barre d'état à 9:41 ; quatre fichiers par langue : `room.png`, `swipe.png`, `kibble.png` (en pleine
   partie), `shop_furniture.png`.
2. `python3 tools/sync-app-assets.py <dépôt-app> <captures-fr> <captures-en>` : il affiche les comptes de
   la boutique et le balisage de la grille dans les deux langues, à reporter dans `index.html` et `en/index.html`.
3. `python3 tools/da-paw-web.py <dépôt-app> <captures-iphone>` APRÈS le script précédent : il réécrit
   `shot-home`, `shot-swipe` et `shot-companion-room` (captures de l'iPhone, barre d'état remplacée par celle
   du simulateur à 9:41), les objets 3D, les boucles des chats et les icônes.
4. `python3 tools/make-og-images.py`.

## DA Paw sur le monde sombre (2026-09-24)

Le monde sombre reprend la DA Paw de l'app : noir, #EDEDED, Manrope, le grain avec une lumière douce en haut à
gauche (fixe, sous tout le contenu), le chat 3D au téléphone en tête, les objets 3D mats à la place des pictos
dessinés, le chat qui salue au dernier appel. Le monde du familier reste en pixel art chaud.
- **Les boucles vidéo se fondent par `mix-blend-mode: screen`** : aucun ancêtre ne doit créer de contexte
  d'empilement (transform, opacité, z-index, filtre), sinon le noir du clip réapparaît en carré. C'est pourquoi
  le chat du dernier appel est hors du bloc `.reveal`.
- **Les références CSS/JS portent `?v=AAAA-MM-JJ`** : à changer à chaque mise en ligne qui les touche (cache de
  GitHub Pages, 10 min).

## Sous-projet `react/`

Le dossier `react/` est un projet React/TypeScript/Tailwind/shadcn autonome, séparé du reste du site — il ne fait **pas** partie du site publié tel quel. Voir `react/README.md` pour le détail. Le site principal ci-dessus reste sans dépendance ni build step.

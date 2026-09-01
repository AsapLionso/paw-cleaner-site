import { TestimonialsColumn, type Testimonial } from "@/components/ui/testimonials-columns-1";

// Aperçu de développement uniquement (npm run dev) — sert à vérifier
// visuellement le rendu/l'animation/le responsive du composant Témoignages.
// Ces données ne sont jamais utilisées côté site (voir Testimonials.tsx, qui
// exporte un tableau vide tant qu'il n'y a pas de vrais témoignages).
const placeholderAvatar =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40'%3E%3Crect width='40' height='40' rx='20' fill='%23d4d4d4'/%3E%3C/svg%3E";

const previewTestimonials: Testimonial[] = [
  { text: "Aperçu de rendu — carte 1.", image: placeholderAvatar, name: "Aperçu", role: "Colonne" },
  { text: "Aperçu de rendu — carte 2.", image: placeholderAvatar, name: "Aperçu", role: "Colonne" },
  { text: "Aperçu de rendu — carte 3.", image: placeholderAvatar, name: "Aperçu", role: "Colonne" },
];

export default function App() {
  return (
    <div style={{ padding: 40 }}>
      <p style={{ marginBottom: 24, fontFamily: "sans-serif" }}>
        Aperçu dev du composant Témoignages (données factices, jamais commitées comme contenu réel).
      </p>
      <div className="flex justify-center gap-6 [mask-image:linear-gradient(to_bottom,transparent,black_25%,black_75%,transparent)] max-h-[600px] overflow-hidden">
        <TestimonialsColumn testimonials={previewTestimonials} duration={15} />
      </div>
    </div>
  );
}

import { motion } from "motion/react";
import { TestimonialsColumn, type Testimonial } from "@/components/ui/testimonials-columns-1";

// TODO(real-content): l'app n'a pas encore d'utilisateurs réels (pas publiée
// sur l'App Store) — ce tableau reste volontairement vide tant qu'il n'existe
// pas de vrais témoignages à afficher. Ne jamais y mettre de contenu fabriqué
// (faux noms/photos/citations) : voir la décision du 2026-08-10 dans
// react/README.md. Remplir avec de vrais avis (App Store, beta testeurs)
// avant d'activer cette section sur le site.
export const testimonials: Testimonial[] = [];

const firstColumn = testimonials.slice(0, Math.ceil(testimonials.length / 3));
const secondColumn = testimonials.slice(
  Math.ceil(testimonials.length / 3),
  Math.ceil((testimonials.length * 2) / 3)
);
const thirdColumn = testimonials.slice(Math.ceil((testimonials.length * 2) / 3));

export function Testimonials() {
  return (
    <section className="bg-background my-20 relative">
      <div className="container z-10 mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
          viewport={{ once: true }}
          className="flex flex-col items-center justify-center max-w-[540px] mx-auto"
        >
          <div className="flex justify-center">
            <div className="border py-1 px-4 rounded-lg">Testimonials</div>
          </div>

          <h2 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl font-bold tracking-tighter mt-5">
            What our users say
          </h2>
          <p className="text-center mt-5 opacity-75">
            See what our customers have to say about us.
          </p>
        </motion.div>

        <div className="flex justify-center gap-6 mt-10 [mask-image:linear-gradient(to_bottom,transparent,black_25%,black_75%,transparent)] max-h-[740px] overflow-hidden">
          <TestimonialsColumn testimonials={firstColumn} duration={15} />
          <TestimonialsColumn testimonials={secondColumn} className="hidden md:block" duration={19} />
          <TestimonialsColumn testimonials={thirdColumn} className="hidden lg:block" duration={17} />
        </div>
      </div>
    </section>
  );
}

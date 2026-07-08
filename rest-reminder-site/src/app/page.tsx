import Hero from "@/components/Hero";
import Features from "@/components/Features";
import WhyChoose from "@/components/WhyChoose";
import Download from "@/components/Download";
import Testimonials from "@/components/Testimonials";
import Sponsor from "@/components/Sponsor";
import Footer from "@/components/Footer";
import { useI18n } from "@/lib/i18n";

function Stats() {
  const { t } = useI18n();
  const stats = [
    { value: "48MB", label: t("stats.48mb") },
    { value: "60min", label: t("stats.60min") },
    { value: "12h+", label: t("stats.12h") },
    { value: "MIT", label: t("stats.mit") },
  ];
  return (
    <section className="py-16 px-6 border-y border-[var(--border)]">
      <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8">
        {stats.map((s) => (
          <div key={s.label} className="text-center">
            <div className="text-3xl md:text-4xl font-bold font-display gradient-text">{s.value}</div>
            <div className="text-sm text-[var(--fg-dim)] mt-2">{s.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <main className="flex-1">
      <Hero />
      <Stats />
      {/* 视觉展示横幅 */}
      <section className="py-12 px-6">
        <div className="max-w-5xl mx-auto">
          <img
            src="/hero-banner-promo.png"
            alt="Rest Reminder"
            className="w-full rounded-2xl border border-[var(--border)]"
          />
        </div>
      </section>
      <Features />
      <WhyChoose />
      <Download />
      <Testimonials />
      <Sponsor />
      <Footer />
    </main>
  );
}

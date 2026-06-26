import Hero from "@/components/Hero";
import Features from "@/components/Features";
import Changelog from "@/components/Changelog";
import Download from "@/components/Download";
import Footer from "@/components/Footer";

function Stats() {
  const stats = [
    { value: "46MB", label: "轻量安装" },
    { value: "60min", label: "自动循环" },
    { value: "12h+", label: "每日追踪" },
    { value: "MIT", label: "开源协议" },
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
      <Features />
      <Changelog />
      <Download />
      <Footer />
    </main>
  );
}

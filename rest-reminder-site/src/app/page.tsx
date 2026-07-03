import Hero from "@/components/Hero";
import Features from "@/components/Features";
import WhyChoose from "@/components/WhyChoose";
import Download from "@/components/Download";
import Testimonials from "@/components/Testimonials";
import Sponsor from "@/components/Sponsor";
import Footer from "@/components/Footer";

function Stats() {
  const stats = [
    { value: "48MB", label: "轻量安装" },
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

function Privacy() {
  return (
    <section className="py-20 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="card p-6">
            <div className="text-2xl mb-3">🔒</div>
            <h3 className="text-sm font-semibold mb-2">数据完全本地</h3>
            <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
              所有学习数据仅存储在本地 JSON 文件，不上传任何服务器。你的学习习惯只属于你。
            </p>
          </div>
          <div className="card p-6">
            <div className="text-2xl mb-3">🚫</div>
            <h3 className="text-sm font-semibold mb-2">无账号体系</h3>
            <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
              不需要注册、登录、绑定手机号。下载即用，零门槛。
            </p>
          </div>
          <div className="card p-6">
            <div className="text-2xl mb-3">📦</div>
            <h3 className="text-sm font-semibold mb-2">MIT 开源</h3>
            <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
              代码完全开源，可自行审计、二次开发。无隐藏逻辑，无数据采集。
            </p>
          </div>
        </div>
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
      <WhyChoose />
      <Privacy />
      <Download />
      <Testimonials />
      <Sponsor />
      <Footer />
    </main>
  );
}

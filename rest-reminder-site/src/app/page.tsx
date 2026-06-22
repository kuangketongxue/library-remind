import Hero from "@/components/Hero";
import Features from "@/components/Features";
import WhyChoose from "@/components/WhyChoose";
import Testimonials from "@/components/Testimonials";
import Pricing from "@/components/Pricing";
import Changelog from "@/components/Changelog";
import FAQ from "@/components/FAQ";
import Download from "@/components/Download";
import Footer from "@/components/Footer";
import StickyCTA from "@/components/StickyCTA";

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

function HowItWorks() {
  const steps = [
    { num: "1", title: "下载安装", desc: "下载 RestReminder.exe，双击运行，46MB 秒装" },
    { num: "2", title: "自动计时", desc: "右下角浮球自动出现，60分钟循环倒计时" },
    { num: "3", title: "到点休息", desc: "自动弹出B站护眼视频，休息完自动重启" },
    { num: "4", title: "查看数据", desc: "学习时长、连续打卡、每日统计一目了然" },
  ];
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <p className="text-center text-[var(--fg-dim)] text-lg mb-14">4步开始保护你的眼睛</p>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {steps.map((s, i) => (
            <div key={s.num} className="text-center relative">
              {i < steps.length - 1 && (
                <div className="hidden md:block absolute top-5 left-[60%] w-[80%] border-t border-dashed border-[var(--border)]" />
              )}
              <div className="w-10 h-10 rounded-full bg-[var(--accent-soft)] text-[var(--accent)] text-sm font-bold flex items-center justify-center border border-[var(--border-accent)] mx-auto mb-4 relative z-10">
                {s.num}
              </div>
              <h3 className="text-base font-semibold mb-2">{s.title}</h3>
              <p className="text-sm text-[var(--fg-dim)] leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <main className="flex-1">
      <StickyCTA />
      <Hero />
      <Stats />
      <Features />
      <HowItWorks />
      <WhyChoose />
      <Testimonials />
      <Changelog />
      <FAQ />
      <Download />
      <Footer />
    </main>
  );
}

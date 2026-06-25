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
import Sponsor from "@/components/Sponsor";

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
    { num: "1", title: "下载安装", desc: "从 GitHub Releases 下载 RestReminder.exe，46MB 秒装", img: "download" },
    { num: "2", title: "开始计时", desc: "右下角出现浮球，点击开始学习，60分钟自动循环", img: "timer" },
    { num: "3", title: "查看数据", desc: "学习时长、连续打卡一目了然，AI 自动生成学习报告", img: "stats" },
  ];
  return (
    <section className="py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <p className="text-center text-[var(--fg-dim)] text-lg mb-14">3步开始使用</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((s, i) => (
            <div key={s.num} className="text-center">
              <div className="w-10 h-10 rounded-full bg-[var(--accent-soft)] text-[var(--accent)] text-sm font-bold flex items-center justify-center border border-[var(--border-accent)] mx-auto mb-4">
                {s.num}
              </div>
              <h3 className="text-base font-semibold mb-2">{s.title}</h3>
              <p className="text-sm text-[var(--fg-dim)] leading-relaxed mb-5">{s.desc}</p>
              {/* CSS mockup card */}
              <div className="bg-[var(--surface-raised)] border border-[var(--border)] rounded-xl overflow-hidden shadow-lg mx-auto max-w-[240px]">
                {s.img === "download" && (
                  <div className="p-4">
                    <div className="flex items-center gap-2 mb-3 pb-3 border-b border-[var(--border)]">
                      <img src="/rest-reminder-logo.png" alt="Rest Reminder" className="w-5 h-5 rounded-sm" />
                      <div className="text-xs text-[var(--fg)]">Rest Reminder</div>
                    </div>
                    <div className="space-y-1.5">
                      <div className="flex items-center gap-2 text-xs text-[var(--fg-dim)]">
                        <span className="text-[var(--accent)]">✓</span> 开机自启动
                      </div>
                      <div className="flex items-center gap-2 text-xs text-[var(--fg-dim)]">
                        <span className="text-[var(--accent)]">📊</span> 学习统计
                      </div>
                      <div className="flex items-center gap-2 text-xs text-[var(--fg-dim)]">
                        <span className="text-[var(--accent)]">🔥</span> 连续打卡 5 天
                      </div>
                      <div className="flex items-center gap-2 text-xs text-[var(--fg-dim)]">
                        <span className="text-[var(--accent)]">💡</span> 提醒方式
                      </div>
                      <div className="flex items-center gap-2 text-xs text-[var(--accent)]">
                        📋 导出本周数据
                      </div>
                      <div className="bg-[var(--accent-soft)] text-[var(--accent)] rounded text-xs px-3 py-1.5 mt-2">重置位置到右侧</div>
                      <div className="text-xs text-[var(--fg-dim)]">退出</div>
                    </div>
                  </div>
                )}
                {s.img === "timer" && (
                  <div className="p-5">
                    <div className="text-center mb-3">
                      <div className="text-[var(--accent)] text-2xl font-bold font-display">04:59</div>
                      <div className="text-[10px] text-[var(--fg-dim)] mt-1">倒计时中 · 学习第 3 轮</div>
                    </div>
                    <div className="h-1.5 w-full bg-[var(--border)] rounded-full mb-4 overflow-hidden">
                      <div className="h-full bg-[var(--accent)] rounded-full" style={{ width: '75%' }} />
                    </div>
                    <div className="flex gap-2 justify-center">
                      <div className="bg-[var(--accent-soft)] text-[var(--accent)] text-[10px] px-3 py-1 rounded-full">⏸ 暂停</div>
                      <div className="bg-[var(--surface)] text-[var(--fg-dim)] text-[10px] px-3 py-1 rounded-full border border-[var(--border)]">✓ 完成</div>
                    </div>
                  </div>
                )}
                {s.img === "stats" && (
                  <div className="p-4">
                    <div className="text-xs text-[var(--fg-dim)] mb-2">📊 近7天学习统计</div>
                    <div className="flex items-end gap-2 h-20 mb-2">
                      {[15, 15, 15, 15, 5, 15, 6].map((h, i) => (
                        <div key={i} className="flex-1 flex flex-col items-center gap-1">
                          <div className="text-[8px] text-[var(--fg-dim)]">{h}.0</div>
                          <div className="w-full bg-[var(--accent)] rounded-sm" style={{ height: `${(h / 15) * 100}%`, minHeight: '4px' }} />
                        </div>
                      ))}
                    </div>
                    <div className="flex justify-between text-[8px] text-[var(--fg-dim)]">
                      <span>05/31</span><span>06/06</span>
                    </div>
                    <div className="flex gap-3 mt-2 text-[8px]">
                      <span className="flex items-center gap-1"><span className="w-2 h-2 bg-[var(--accent)] rounded-sm" /> 学习</span>
                    </div>
                  </div>
                )}
              </div>
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
      <Sponsor />
      <Footer />
    </main>
  );
}

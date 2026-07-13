"use client";

import DocsNav from "@/components/DocsNav";
import DocsTOC from "@/components/DocsTOC";
import { useI18n } from "@/lib/i18n";

export default function DocsPage() {
  const { t } = useI18n();
  return (
    <main className="flex-1">
      <div className="docs-layout">
        {/* 左侧导航 */}
        <DocsNav />

        {/* 内容区 */}
        <div className="docs-main" style={{ maxWidth: "800px" }}>
          {/* Breadcrumb */}
          <nav className="flex items-center gap-2 text-xs text-[var(--fg-dim)] mb-6">
            <a href="/" className="hover:text-[var(--fg)] transition-colors">{t("nav.docs")}</a>
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-[var(--fg)]">{t("nav.docs")}</span>
          </nav>

          {/* 搜索框 */}
          <div className="mb-8" id="搜索">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--fg-muted)]" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8" /><path strokeLinecap="round" d="M21 21l-4.35-4.35" />
              </svg>
              <input
                id="doc-search-input"
                type="text"
                placeholder={t("docs.search_placeholder")}
                className="w-full pl-10 pr-4 py-2.5 text-sm bg-[var(--surface)] border border-[var(--border)] rounded-lg text-[var(--fg)] placeholder:text-[var(--fg-muted)] focus:outline-none focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] transition-colors"
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    const q = (e.target as HTMLInputElement).value.trim().toLowerCase();
                    if (!q) return;
                    const sections = document.querySelectorAll("section[id]");
                    for (const s of sections) {
                      if (s.textContent?.toLowerCase().includes(q)) {
                        s.scrollIntoView({ behavior: "smooth", block: "start" });
                        break;
                      }
                    }
                  }
                }}
              />
              <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-[var(--fg-muted)] bg-[var(--bg)] border border-[var(--border)] rounded px-1.5 py-0.5">Enter</kbd>
            </div>
          </div>

          <h1 className="text-3xl font-extrabold tracking-tight mb-2 font-display">
            {t("docs.title")}
          </h1>
          <p className="text-[var(--fg-dim)] mb-10">
            {t("docs.subtitle")}
          </p>

          {/* ── 产品简介 ── */}
          <section className="mb-16" id="简介">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.what_is")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">{t("docs.what_is_desc")}</p>

            <div className="docs-card mb-6">
              <p className="text-sm text-[var(--fg)] leading-relaxed mb-3">
                <strong>Rest Reminder</strong> {t("docs.intro_p1")}
              </p>
              <p className="text-sm text-[var(--fg)] leading-relaxed mb-3">
                {t("docs.intro_p2")}
              </p>
              <p className="text-sm text-[var(--fg-dim)] leading-relaxed">
                {t("docs.intro_p3")}
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="docs-card text-center">
                <div className="text-2xl font-bold text-[var(--accent)] mb-1">48MB</div>
                <div className="text-xs text-[var(--fg-dim)]">{t("stats.48mb")}</div>
              </div>
              <div className="docs-card text-center">
                <div className="text-2xl font-bold text-[var(--accent)] mb-1">60min</div>
                <div className="text-xs text-[var(--fg-dim)]">{t("stats.60min")}</div>
              </div>
              <div className="docs-card text-center">
                <div className="text-2xl font-bold text-[var(--accent)] mb-1">17</div>
                <div className="text-xs text-[var(--fg-dim)]">{t("docs.stat_achievements")}</div>
              </div>
              <div className="docs-card text-center">
                <div className="text-2xl font-bold text-[var(--accent)] mb-1">MIT</div>
                <div className="text-xs text-[var(--fg-dim)]">{t("stats.mit")}</div>
              </div>
            </div>
          </section>

          {/* ── 快速开始 ── */}
          <section className="mb-16" id="快速开始">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.quickstart_title")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">{t("docs.quickstart_desc")}</p>

            <div className="docs-callout mb-6">
              <p className="text-sm font-semibold mb-2">{t("docs.privacy_card_title")}</p>
              <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                {t("docs.privacy_card_desc")}
              </p>
            </div>

            <div className="space-y-8">
              <div id="下载运行">
                <h3 className="text-base font-semibold mb-3 font-display">{t("docs.step1_title")}</h3>
                <div className="docs-card mb-3">
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-3">
                    {t("docs.step1_desc")}
                  </p>
                  <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                    {t("docs.step1_note")}
                  </p>
                  <pre className="bg-[var(--surface)] rounded-lg p-4 mt-3 text-xs font-mono text-[#b5651d] overflow-x-auto">
{`pip install -r requirements.txt
python rest_reminder.py`}
                  </pre>
                </div>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.step1_note2")}
                </p>
              </div>

              <div id="设定目标">
                <h3 className="text-base font-semibold mb-3 font-display">{t("docs.step2_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.step2_desc")}
                </p>
                <div className="docs-card mt-3">
                  <p className="text-xs text-[var(--fg-dim)]">
                    <span className="text-[var(--accent)]">{t("docs.step2_tip_label")}</span> {t("docs.step2_tip")}
                  </p>
                </div>
              </div>

              <div id="开始学习">
                <h3 className="text-base font-semibold mb-3 font-display">{t("docs.step3_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.step3_desc")}
                </p>
                <div className="docs-card mt-3">
                  <p className="text-sm font-semibold mb-2">{t("docs.step3_flow_title")}</p>
                  <div className="flex items-center gap-2 text-sm text-[var(--fg-dim)]">
                    <span className="bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-1 rounded-lg font-mono text-xs">{t("docs.step3_flow_learn")}</span>
                    <span>→</span>
                    <span className="bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-1 rounded-lg font-mono text-xs">{t("docs.step3_flow_discern")}</span>
                    <span>→</span>
                    <span className="bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-1 rounded-lg font-mono text-xs">{t("docs.step3_flow_rest")}</span>
                    <span>→</span>
                    <span className="bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-1 rounded-lg font-mono text-xs">{t("docs.step3_flow_bili")}</span>
                  </div>
                </div>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                  {t("docs.step3_note")}
                </p>
              </div>

              <div id="复盘追踪">
                <h3 className="text-base font-semibold mb-3 font-display">{t("docs.step4_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.step4_desc")}
                </p>
                <div className="space-y-3 mt-3">
                  <div className="docs-card">
                    <p className="text-sm font-semibold mb-1">{t("docs.step4_review_title")}</p>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                      {t("docs.step4_review_desc")}
                    </p>
                  </div>
                  <div className="docs-card">
                    <p className="text-sm font-semibold mb-1">{t("docs.step4_streak_title")}</p>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                      {t("docs.step4_streak_desc")}
                    </p>
                  </div>
                  <div className="docs-card">
                    <p className="text-sm font-semibold mb-1">{t("docs.step4_live_title")}</p>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                      {t("docs.step4_live_desc")}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* ── 界面预览 ── */}
          <section className="mb-16" id="界面预览">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.preview_title")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">{t("docs.preview_desc")}</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="docs-card overflow-hidden">
                <div className="bg-[var(--bg)] p-8 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-12 h-12 rounded-full bg-[var(--accent-soft)] flex items-center justify-center text-2xl mx-auto mb-2">⚡</div>
                    <p className="text-xs text-[var(--fg-dim)]">{t("docs.preview_float_title")}</p>
                  </div>
                </div>
                <div className="p-3 border-t border-[var(--border)]">
                  <p className="text-xs text-[var(--fg-dim)]">{t("docs.preview_float_desc")}</p>
                </div>
              </div>
              <div className="docs-card overflow-hidden">
                <div className="bg-[var(--bg)] p-8 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-2xl font-bold font-display text-[var(--accent)] mb-2">⏱ 58:32</div>
                    <p className="text-[10px] text-[var(--fg-dim)]">{t("docs.preview_timer_title")}</p>
                  </div>
                </div>
                <div className="p-3 border-t border-[var(--border)]">
                  <p className="text-xs text-[var(--fg-dim)]">{t("docs.preview_timer_desc")}</p>
                </div>
              </div>
              <div className="docs-card overflow-hidden">
                <div className="bg-[var(--bg)] p-8 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-8 rounded bg-[var(--accent-soft)] mb-2"></div>
                    <p className="text-[10px] text-[var(--fg-dim)]">{t("docs.preview_trend_title")}</p>
                  </div>
                </div>
                <div className="p-3 border-t border-[var(--border)]">
                  <p className="text-xs text-[var(--fg-dim)]">{t("docs.preview_trend_desc")}</p>
                </div>
              </div>
            </div>
          </section>

          {/* ── 功能说明 ── */}
          <section className="mb-16" id="功能说明">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.features_title")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-8">{t("docs.features_desc")}</p>

            <div className="space-y-5">
              <div className="docs-card" id="专注循环">
                <h3 className="text-sm font-semibold mb-2">{t("docs.feature_focus_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.feature_focus_desc")}
                </p>
                <div className="mt-3 bg-[var(--surface)] rounded-lg p-4">
                  <p className="text-xs font-mono text-[var(--fg-dim)]">
                    {t("docs.feature_focus_rule")}
                  </p>
                </div>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                  {t("docs.feature_focus_note")}
                </p>
              </div>

              <div className="docs-card" id="护眼提醒">
                <h3 className="text-sm font-semibold mb-2">{t("docs.feature_eye_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.feature_eye_desc")}
                </p>
              </div>

              <div className="docs-card" id="学习追踪">
                <h3 className="text-sm font-semibold mb-2">{t("docs.feature_track_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.feature_track_desc")}
                </p>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3 space-y-1 list-disc list-inside">
                  <li>{t("docs.feature_track_0")}</li>
                  <li>{t("docs.feature_track_1")}</li>
                  <li>{t("docs.feature_track_2")}</li>
                  <li>{t("docs.feature_track_3")}</li>
                </ul>
              </div>

              <div className="docs-card" id="趋势分析">
                <h3 className="text-sm font-semibold mb-2">{t("docs.feature_trend_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.feature_trend_desc")}
                </p>
                <div className="mt-3 space-y-2">
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">今日</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.feature_trend_0")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">周趋势</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.feature_trend_1")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">月趋势</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.feature_trend_2")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">季/年</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.feature_trend_3")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">时段</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.feature_trend_4")}</p>
                  </div>
                </div>
              </div>

              <div className="docs-card" id="ai分析">
                <h3 className="text-sm font-semibold mb-2">{t("docs.feature_ai_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.feature_ai_desc")}
                </p>
                <div className="mt-3 bg-[var(--surface)] rounded-xl p-4">
                  <p className="text-sm font-semibold mb-2">{t("docs.feature_ai_subtitle")}</p>
                  <ul className="text-xs text-[var(--fg-dim)] leading-relaxed space-y-1 list-disc list-inside">
                    <li>{t("docs.feature_ai_0")}</li>
                    <li>{t("docs.feature_ai_1")}</li>
                    <li>{t("docs.feature_ai_2")}</li>
                    <li>{t("docs.feature_ai_3")}</li>
                    <li>{t("docs.feature_ai_4")}</li>
                  </ul>
                </div>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mt-3">
                  {t("docs.feature_ai_note")}
                </p>
              </div>

              <div className="docs-card" id="使用技巧">
                <h3 className="text-sm font-semibold mb-2">{t("docs.tips_title")}</h3>
                <div className="space-y-3 mt-2">
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">{t("docs.tips_shortcut_title")}</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      {t("docs.tips_shortcut_desc")}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">{t("docs.tips_float_title")}</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      {t("docs.tips_float_desc")}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">{t("docs.tips_tray_title")}</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      {t("docs.tips_tray_desc")}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">{t("docs.tips_battery_title")}</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      {t("docs.tips_battery_desc")}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[var(--fg)]">{t("docs.tips_autostart_title")}</p>
                    <p className="text-xs text-[var(--fg-dim)] mt-1">
                      {t("docs.tips_autostart_desc")}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* ── 设置详解 ── */}
          <section className="mb-16" id="设置详解">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.settings_title")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">{t("docs.settings_desc")}</p>

            <div className="space-y-3">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">{t("docs.set_timer_title")}</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  {t("docs.set_timer_desc")}
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">{t("docs.set_discern_title")}</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  {t("docs.set_discern_desc")}
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">{t("docs.set_eye_title")}</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  {t("docs.set_eye_desc")}
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">{t("docs.set_stats_title")}</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  {t("docs.set_stats_desc")}
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">{t("docs.set_review_title")}</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  {t("docs.set_review_desc")}
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">{t("docs.set_sound_title")}</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  {t("docs.set_sound_desc")}
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">{t("docs.set_autostart_title")}</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  {t("docs.set_autostart_desc")}
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">{t("docs.set_silent_title")}</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  {t("docs.set_silent_desc")}
                </p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-1">{t("docs.set_minimize_title")}</h3>
                <p className="text-xs text-[var(--fg-dim)] leading-relaxed">
                  {t("docs.set_minimize_desc")}
                </p>
              </div>
            </div>
          </section>

          {/* ── 开发指南 ── */}
          <section className="mb-16" id="开发指南">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.dev_title")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">{t("docs.dev_desc")}</p>

            <div className="space-y-5">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.dev_env_title")}</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>{t("docs.dev_env_0")}</li>
                  <li>{t("docs.dev_env_1")}</li>
                  <li>{t("docs.dev_env_2")}</li>
                </ul>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.dev_quick_title")}</h3>
                <pre className="bg-[var(--surface)] rounded-lg p-4 text-xs font-mono text-[#b5651d] overflow-x-auto">
{`git clone https://github.com/kuangketongxue/library-remind.git
cd library-remind
C:\\Python314\\python.exe rest_reminder.py --silent`}
                </pre>
                <p className="text-[var(--fg-dim)] text-xs mt-3 leading-relaxed">
                  {t("docs.dev_quick_note")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.dev_struct_title")}</h3>
                <div className="space-y-2">
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">rest_reminder.py</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.dev_struct_0")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">storage.py</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.dev_struct_1")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">tray_card.py</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.dev_struct_2")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">feishu_calendar.py</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.dev_struct_3")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">vendor/</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.dev_struct_4")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0 w-44">CLAUDE.md / AGENTS.md</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.dev_struct_5")}</p>
                  </div>
                </div>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.dev_state_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.dev_state_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.dev_build_title")}</h3>
                <pre className="bg-[var(--surface)] rounded-lg p-4 text-xs font-mono text-[#b5651d] overflow-x-auto">
{`pyinstaller RestReminder.spec`}
                </pre>
                <p className="text-[var(--fg-dim)] text-xs mt-3 leading-relaxed">
                  {t("docs.dev_build_note")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.dev_code_title")}</h3>
                <ul className="text-[var(--fg-dim)] text-sm leading-relaxed space-y-1 list-disc list-inside">
                  <li>{t("docs.dev_code_0")}</li>
                  <li>{t("docs.dev_code_1")}</li>
                  <li>{t("docs.dev_code_2")}</li>
                  <li>{t("docs.dev_code_3")}</li>
                  <li>{t("docs.dev_code_4")}</li>
                </ul>
              </div>
            </div>
          </section>

          {/* ── Claude Code 接入指南 ── */}
          <section className="mb-16" id="claude-code">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.claude_title")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">{t("docs.claude_desc")}</p>

            <div className="space-y-5">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.claude_config_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.claude_config_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.claude_workflow_title")}</h3>
                <ol className="text-[var(--fg-dim)] text-sm leading-relaxed list-decimal list-inside space-y-2">
                  <li><code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">taskkill /F /IM python.exe</code></li>
                  <li><code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">C:\Python314\python.exe -c "import py_compile; py_compile.compile('rest_reminder.py')"</code></li>
                  <li><code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">C:\Python314\python.exe rest_reminder.py --silent</code></li>
                  <li><code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">tasklist | findstr python.exe</code></li>
                  <li><code className="bg-[var(--surface)] px-1 py-0.5 rounded text-xs font-mono">type crash.log</code></li>
                </ol>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.claude_note_title")}</h3>
                <div className="space-y-2">
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">Python 版本</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.claude_note_0")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">crash.log</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.claude_note_1")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">多实例</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.claude_note_2")}</p>
                  </div>
                  <div className="flex gap-3">
                    <span className="text-xs font-mono text-[var(--accent)] shrink-0">UI 修改</span>
                    <p className="text-xs text-[var(--fg-dim)] leading-relaxed">{t("docs.claude_note_3")}</p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* ── 更新日志 ── */}
          <section className="mb-16" id="更新日志">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.changelog_title")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">{t("docs.changelog_desc")}</p>

            <div className="space-y-6">
              <div className="changelog-entry latest pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.7</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-09</span>
                  <span className="text-xs bg-[var(--accent-soft)] text-[var(--accent)] px-2 py-0.5 rounded-full">最新</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>桌面应用关于页按钮加 emoji（官网🌐、更新日志📋、检查更新🔄）</li>
                  <li>官网新增 CN/EN/JP 三语言切换 + 日/夜模式</li>
                  <li>Navbar/Footer GitHub 链接改为真实 cat SVG 图标</li>
                  <li>新增唯一官方渠道声明横幅（防山寨/反诈提醒）</li>
                  <li>AI 服务不可用提示优化 + 单实例 Mutex stale lock 修复</li>
                  <li>官网 Hero 视频背景修复 + 公告弹窗逻辑修正</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.6</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>浏览器图标修复：favicon 换为 256x256 cute_icon.png</li>
                  <li>Contact 页面 framer-motion SSR 修复：内容不再透明不可见</li>
                  <li>Contact 页面使用 Gmail/WeChat 官方品牌图标</li>
                  <li>Hero 背景视频修复：静态图兜底 + 视频立即 autoPlay</li>
                  <li>公告弹窗每次访问弹出，文字颜色修复</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.5</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>AI 报告降级修复：服务不可用时显示本地数据摘要（学习时长/轮次/复盘）而非随机金句</li>
                  <li>Cloudflare Worker 重部署：AI 代理恢复正常</li>
                  <li>关终端不再退出应用：改用 pythonw.exe 后台启动</li>
                  <li>官网 Contact 等页面 404 修复：添加 fix-routes.js 构建后脚本</li>
                  <li>CI/CD 部署验证：自动测试所有页面和 AI 代理</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.4</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>AI 报告反幻觉修复：禁止编造老师姓名、学校、科目细节等虚构内容</li>
                  <li>所有结论必须引用具体数字</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.3</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>新增 /contact 联系页面：邮箱 + 微信二维码 + GitHub Issue 模板</li>
                  <li>新增 bug_report / feature_request / partnership 3 个 Issue 模板</li>
                  <li>文档页新增产品简介段 + 4 个数据卡片</li>
                  <li>导航栏新增「联系我们」链接</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.2</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>官网全面改版：暖奶油色背景 + WorkBuddy 风格 Footer + 三栏文档布局</li>
                  <li>导航栏新增「定价」链接 + 搜索按钮</li>
                  <li>Footer 重设计：Hero CTA + 4 栏导航（服务条款/文档指引/产品下载/联系我们）</li>
                  <li>文档页三栏布局：左侧导航 + 中间内容 + 右侧快速导航（滚动高亮）</li>
                  <li>文档页顶部搜索框（Enter 跳转匹配章节）</li>
                  <li>Navbar 文字适配深色背景（白色）</li>
                  <li>知识库清理：删除 7 个过期文件 + 新增 7 条经验记录</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.1</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>页面背景从纯白改为暖奶油色（#fdf6f0），长时间浏览不伤眼</li>
                  <li>CTA 横幅深棕渐变，白字清晰可见</li>
                  <li>底部粘性 CTA 栏适配暖色背景</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.2.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-06</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复 9 处 QFont CSS 字符串导致的主界面文字乱码（Georgia/Consolas 等字体失效回退）</li>
                  <li>修复飞书日历 lark-cli 路径亡址（指向已删 .workbuddy/ 目录）</li>
                  <li>AI 服务超时时自动 fallback 本地智慧语录（不再显示错误 toast，review 报告始终可用）</li>
                  <li>官网新增 pricing / privacy / rules / terms 法律合规 4 个独立页面</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.9</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-04</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>浮球 popup 飞书日程显示修复：root 重建 bug + 高度增大到 240</li>
                  <li>新增版本更新检查：启动后自动检测 GitHub 最新 release，有新版弹窗提示</li>
                  <li>修复 threading 模块未导入导致后台任务崩溃（影响 AI 报告 + 版本检查）</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.8</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-04</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复浮球 popup 关闭后再打开卡片空白</li>
                  <li>文档站 /docs 全面改版：Claude.ai 风格三栏布局</li>
                  <li>导航链接修复 + 硬编码颜色统一 + 死代码清理</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.7</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-04</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复 import copy 缺失导致设置保存崩溃</li>
                  <li>修复复盘弹窗 QSlider GC 崩溃（自动提交后评分丢失）</li>
                  <li>清理 _enter_rest() 重复通知</li>
                  <li>关于页 AI 服务动态展示真实 providers 列表</li>
                  <li>CLAUDE.md 与规格文档同步到 v6.x</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.6</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-03</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>设置保存防抖：300ms 内多次调用合并为一次磁盘写入</li>
                  <li>单实例锁删除 msvcrt 文件锁残留，仅用 Named Mutex</li>
                  <li>飞书日程 subprocess 改 Popen，stop() 可立即终止子进程</li>
                  <li>飞书日程缓存 24h→1h，避免跨天日程不刷新</li>
                  <li>修复邮件测试连点堆叠 QThread 崩溃、JSONStore 并发写丢 key</li>
                  <li>md_to_html 接受 theme 参数，light 主题报告不再显示 dark 底色</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.4</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-02</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复 AI 服务不可用：default_proxy 被禁用后重启仍不可用</li>
                  <li>修复设置页测试连接卡顿：HTTP 请求改后台线程，UI 不再冻结</li>
                  <li>浮球短点击切换显示/隐藏，右键菜单动态文案</li>
                  <li>托盘菜单新增浮球显示切换</li>
                  <li>浮球 popup 扩容到 260×200，22:00 进度条改为倒计时模式</li>
                  <li>飞书刷新按钮对比度修复，侧边栏矢量图标，GitHub 真实图标</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.3</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-02</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复计时漂移：引入 time.perf_counter() 统一计时源</li>
                  <li>修复临时文件泄漏：_TempFileManager 集中注册 + atexit 清理</li>
                  <li>增强日志归档：按日期自动归档旧日志</li>
                  <li>Sponsor 区重构：真实技术生态 + 文档 FAQ 赞助合作</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.1.2</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-07-01</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>修复趋势图完全空白（延迟加载后初始数据未加载）</li>
                  <li>修复设置 Tab 错误显示趋势内容（索引错位）</li>
                  <li>官网下载截图替换为 GitHub Releases 页面</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v6.0.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-30</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>主界面去置顶 + AI 服务自定义提供商</li>
                  <li>内置免费 AI（Cloudflare 代理，key 隐藏）</li>
                  <li>成就扩充 16→19 个，进度条优化</li>
                  <li>GitHub 自动备份 + 官网优化</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.6.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-30</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>成就显示优化：卡片式展示 + 进度条 + 当前进度文本</li>
                  <li>环境白噪音：30 秒循环、首尾 crossfade 消除循环断裂</li>
                  <li>邮件周报改用 Agent QQ 邮箱（agently-cli），移除 SMTP</li>
                  <li>关于界面字体放大，环境/数据/AI 服务信息清晰可见</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.5.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-29</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>成就/徽章系统：16 个成就，解锁 Toast 通知</li>
                  <li>GitHub 风格学习热力图：52 周 × 7 天，5 级颜色</li>
                  <li>环境白噪音：雨声/森林/咖啡厅/白噪音/棕噪音</li>
                  <li>每周邮件周报：SMTP 配置，HTML 格式 AI 学习报告</li>
                  <li>主题切换：深色/浅色/跟随系统</li>
                  <li>全局快捷键：Ctrl+Alt+P/S/B，Ctrl+1~5 切换 Tab</li>
                  <li>API Key 加密存储（XOR + 机器盐值）</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.4.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-29</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>飞书日程集成：实时显示当前/下一个日程</li>
                  <li>趋势时间选择器：近7/14/30天 + 自定义日期范围</li>
                  <li>AI API Key 配置界面、SenseNova 推理模型兼容</li>
                  <li>修复任务栏图标丢失、多实例启动竞态</li>
                  <li>「关于」「趋势」页面重新设计</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.1.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-26</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>主界面全面实时刷新：学习时长/轮次/休息时长/状态/倒计时每秒更新</li>
                  <li>修复复盘摘要空列表崩溃、连续打卡恢复逻辑错误</li>
                  <li>修复月趋势/季年趋势统计错误</li>
                  <li>删除死代码，移除失效窗口按钮</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v5.0.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-25</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>柱状图悬浮提示、复盘学科新增「其他」</li>
                  <li>AI 报告后台线程（QThread 异步），趋势分析全面重构</li>
                  <li>AI 报告字数提升至 400+ 字，增加 5 个分析章节</li>
                  <li>修复 AI 报告卡死、tooltip 不显示等 P0 bug</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v4.4.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-23</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>5 标签页主界面（今日/AI报告/趋势/设置/关于）</li>
                  <li>⚡ 浮球独立（60×60）、点击弹出信息面板</li>
                  <li>20-20-20 护眼浮窗、热力图、B站收藏夹</li>
                  <li>开源发布：移除 Pro 订阅系统，MIT 协议全部免费</li>
                </ul>
              </div>

              <div className="changelog-entry pl-6">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-bold">v4.3.0</span>
                  <span className="text-xs text-[var(--fg-dim)]">2026-06-21</span>
                </div>
                <ul className="text-[var(--fg-dim)] text-sm space-y-1 list-disc list-inside">
                  <li>固定 60 分钟学习 → 5 分钟请辨 → 5 分钟休息循环</li>
                  <li>每 3 轮自动播放护眼视频</li>
                  <li>休息期间弹出复盘评分（学科 + 标签 + 1-100 评分）</li>
                </ul>
              </div>
            </div>

            <p className="text-[var(--fg-dim)] text-sm mt-6">
              {t("docs.changelog_footer")}{" "}
              <a
                href="https://github.com/kuangketongxue/library-remind/blob/main/CHANGELOG.md"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[var(--accent)] hover:underline"
              >
                GitHub CHANGELOG.md
              </a>
            </p>
          </section>

          {/* ── 常见问题 ── */}
          <section className="mb-16" id="常见问题">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.faq_title")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">{t("docs.faq_desc")}</p>

            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_float_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">{t("docs.faq_float_desc")}</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_bili_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">{t("docs.faq_bili_desc")}</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_ai_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">{t("docs.faq_ai_desc")}</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_review_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">{t("docs.faq_review_desc")}</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_uninstall_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.faq_uninstall_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_lose_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">{t("docs.faq_lose_desc")}</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_platform_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">{t("docs.faq_platform_desc")}</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_internet_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">{t("docs.faq_internet_desc")}</p>
              </div>
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_streak_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">{t("docs.faq_streak_desc")}</p>
              </div>

              {/* ── 赞助合作 ── */}
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_sponsor_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.faq_sponsor_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_plan_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.faq_plan_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_launch_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.faq_launch_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.faq_benefit_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.faq_benefit_desc")}
                </p>
              </div>
            </div>
          </section>

          {/* ── 故障排除 ── */}
          <section className="mb-16" id="故障排除">
            <h2 className="text-2xl font-bold mb-1 font-display">{t("docs.troubleshoot_title")}</h2>
            <p className="text-[var(--fg-dim)] text-sm mb-6">{t("docs.troubleshoot_desc")}</p>

            <div className="space-y-4">
              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.ts_float_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">按以下步骤排查：</p>
                <ol className="text-xs text-[var(--fg-dim)] leading-relaxed list-decimal list-inside space-y-1">
                  <li>{t("docs.ts_float_0")}</li>
                  <li>{t("docs.ts_float_1")}</li>
                  <li>{t("docs.ts_float_2")}</li>
                  <li>{t("docs.ts_float_3")}</li>
                </ol>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.ts_ai_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">按以下步骤排查：</p>
                <ol className="text-xs text-[var(--fg-dim)] leading-relaxed list-decimal list-inside space-y-1">
                  <li>{t("docs.ts_ai_0")}</li>
                  <li>{t("docs.ts_ai_1")}</li>
                  <li>{t("docs.ts_ai_2")}</li>
                  <li>{t("docs.ts_ai_3")}</li>
                </ol>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.ts_drift_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.ts_drift_desc")}
                </p>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.ts_bili_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">按以下步骤排查：</p>
                <ol className="text-xs text-[var(--fg-dim)] leading-relaxed list-decimal list-inside space-y-1">
                  <li>{t("docs.ts_bili_0")}</li>
                  <li>{t("docs.ts_bili_1")}</li>
                  <li>{t("docs.ts_bili_2")}</li>
                  <li>{t("docs.ts_bili_3")}</li>
                </ol>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.ts_data_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed">
                  {t("docs.ts_data_desc")}
                </p>
              </div>
            </div>
          </section>

          {/* ── 底部导航 ── */}
          <nav className="border-t border-[var(--border)] pt-8 mt-16 flex flex-col sm:flex-row justify-between gap-4">
            <a href="#更新日志" className="group flex items-center gap-3 text-sm">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <div>
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.prev_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("docs.changelog_title")}</p>
              </div>
            </a>
            <a href="#" className="group flex items-center gap-3 text-sm sm:flex-row-reverse">
              <svg className="w-4 h-4 text-[var(--fg-muted)] group-hover:text-[var(--accent)] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
              <div className="sm:text-right">
                <p className="text-[var(--fg-muted)] text-xs">{t("nav.next_page")}</p>
                <p className="text-[var(--fg)] font-medium group-hover:text-[var(--accent)] transition-colors">{t("docs.nav_back")}</p>
              </div>
            </a>
          </nav>
        </div>

        {/* 右侧快速导航 */}
        <DocsTOC />

      </div>
    </main>
  );
}
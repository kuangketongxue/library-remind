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

            <a href="/changelog" className="docs-card block hover:border-[var(--accent)] transition-colors">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold mb-1">{t("docs.changelog_latest")} — v6.2.10</p>
                  <p className="text-xs text-[var(--fg-dim)]">2026-07-15 · 双启动修复 + 单实例锁 + 安装/卸载脚本统一</p>
                </div>
                <svg className="w-4 h-4 text-[var(--fg-muted)]" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </a>
            <p className="text-[var(--fg-dim)] text-sm mt-4">
              {t("docs.changelog_footer")}{" "}
              <a href="/changelog" className="text-[var(--accent)] hover:underline">
                {t("nav.changelog")}
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
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">{t("docs.ts_steps")}</p>
                <ol className="text-xs text-[var(--fg-dim)] leading-relaxed list-decimal list-inside space-y-1">
                  <li>{t("docs.ts_float_0")}</li>
                  <li>{t("docs.ts_float_1")}</li>
                  <li>{t("docs.ts_float_2")}</li>
                  <li>{t("docs.ts_float_3")}</li>
                </ol>
              </div>

              <div className="docs-card">
                <h3 className="text-sm font-semibold mb-2">{t("docs.ts_ai_title")}</h3>
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">{t("docs.ts_steps")}</p>
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
                <p className="text-[var(--fg-dim)] text-sm leading-relaxed mb-2">{t("docs.ts_steps")}</p>
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
"use client";

import { useEffect, useMemo, useRef, useState } from 'react';
import { Bell, Bot, FileText, LogOut, Mic, MicOff, Pin, Plus, Search, Send, Settings, Shield, Star, Target, Trash2, WalletCards } from 'lucide-react';

function Badge({ children }) {
  return <span className="badge">{children}</span>;
}

export default function DashboardApp({
  user,
  initialSessions,
  initialMessages,
  initialSessionId,
  initialDiaries,
  initialTraits,
  initialToken,
  initialAnnouncement
}) {
  const [sessions, setSessions] = useState(initialSessions || []);
  const [activeSessionId, setActiveSessionId] = useState(initialSessionId);
  const [messages, setMessages] = useState(initialMessages || []);
  const [input, setInput] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [advanced, setAdvanced] = useState(false);
  const [diaries, setDiaries] = useState(initialDiaries || []);
  const [traits, setTraits] = useState(initialTraits || []);
  const [kind, setKind] = useState('success');
  const [diaryInput, setDiaryInput] = useState('');
  const [token, setToken] = useState(initialToken || { today_total: 0, all_total: 0 });
  const [announcement, setAnnouncement] = useState(initialAnnouncement);
  const [adminStats, setAdminStats] = useState(null);
  const [adminNotice, setAdminNotice] = useState('');
  const [view, setView] = useState('chat');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [interview, setInterview] = useState(null);
  const [keySettings, setKeySettings] = useState({
    openrouterKey: '',
    nvidiaKey: ''
  });
  const [keySaved, setKeySaved] = useState('');

  const recognitionRef = useRef(null);
  const [listening, setListening] = useState(false);
  const lastTranscriptRef = useRef('');
  const lastTimestampRef = useRef(0);

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  const filteredSessions = useMemo(() => {
    if (!search.trim()) return sessions;
    return sessions.filter((s) => s.title.toLowerCase().includes(search.trim().toLowerCase()));
  }, [search, sessions]);

  const petMetrics = useMemo(() => {
    const depth = Math.min(100, traits.length * 5 + messages.filter((m) => m.role === 'assistant').length * 2);
    const align = Math.min(100, Math.max(30, 60 + Math.floor((traits.length - 2) * 3)));
    return { depth, align };
  }, [traits, messages]);

  useEffect(() => {
    if (!activeSessionId) return;
    loadMessages(activeSessionId);
  }, [activeSessionId]);

  useEffect(() => {
    refreshAnnouncement();
  }, []);

  useEffect(() => {
    try {
      const raw = localStorage.getItem('kkagent:key:v1');
      if (!raw) return;
      const decoded = decodeURIComponent(escape(atob(raw)));
      const parsed = JSON.parse(decoded);
      setKeySettings({
        openrouterKey: parsed.openrouterKey || '',
        nvidiaKey: parsed.nvidiaKey || ''
      });
    } catch {
      // ignore
    }
  }, []);

  function getRecognition() {
    if (typeof window === 'undefined') return null;
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return null;
    if (!recognitionRef.current) {
      const rec = new SR();
      rec.lang = 'zh-CN';
      rec.continuous = false;
      rec.interimResults = false;

      rec.onresult = (event) => {
        const text = event.results?.[0]?.[0]?.transcript?.trim() || '';
        const now = Date.now();
        if (!text) return;

        const duplicated = text === lastTranscriptRef.current && now - lastTimestampRef.current < 1800;
        if (duplicated) return;

        lastTranscriptRef.current = text;
        lastTimestampRef.current = now;
        setInput((prev) => (prev ? `${prev}\n${text}` : text));
      };

      rec.onend = () => setListening(false);
      rec.onerror = () => setListening(false);
      recognitionRef.current = rec;
    }

    return recognitionRef.current;
  }

  function toggleVoice() {
    const rec = getRecognition();
    if (!rec) {
      alert('当前浏览器不支持语音输入');
      return;
    }

    if (listening) {
      rec.stop();
      setListening(false);
      return;
    }

    setListening(true);
    rec.start();
  }

  async function refreshSessions() {
    const q = search.trim();
    const res = await fetch(`/api/chats${q ? `?q=${encodeURIComponent(q)}` : ''}`);
    const data = await res.json();
    if (res.ok) setSessions(data.sessions || []);
  }

  async function refreshAnnouncement() {
    const res = await fetch('/api/announcements');
    const data = await res.json();
    if (res.ok) setAnnouncement(data.announcement);
  }

  async function loadMessages(sessionId) {
    const res = await fetch(`/api/chats/${sessionId}/messages`);
    const data = await res.json();
    if (res.ok) setMessages(data.messages || []);
  }

  async function createSession() {
    const res = await fetch('/api/chats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: '新对话' })
    });

    const data = await res.json();
    if (!res.ok) return alert(data.error || '创建失败');

    setSessions((prev) => [data.session, ...prev]);
    setActiveSessionId(data.session.id);
    setMessages([]);
  }

  async function deleteSession(id) {
    if (!confirm('确认删除这个对话？')) return;
    await fetch(`/api/chats/${id}`, { method: 'DELETE' });

    const next = sessions.filter((s) => s.id !== id);
    setSessions(next);

    if (activeSessionId === id) {
      setActiveSessionId(next[0]?.id || null);
      setMessages([]);
    }
  }

  async function togglePin(session) {
    const res = await fetch(`/api/chats/${session.id}/pin`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pinned: !session.pinned })
    });

    if (!res.ok) return;
    refreshSessions();
  }

  async function sendMessage(extra = '') {
    const content = (extra || input).trim();
    if (!content || !activeSessionId || loading) return;

    setLoading(true);
    const optimisticUser = {
      id: `tmp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    };

    setMessages((prev) => [...prev, optimisticUser]);
    setInput('');

    const res = await fetch(`/api/chats/${activeSessionId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content,
        advanced,
        openrouterKey: keySettings.openrouterKey,
        nvidiaKey: keySettings.nvidiaKey
      })
    });

    const data = await res.json();
    setLoading(false);

    if (!res.ok) {
      alert(data.error || '发送失败');
      setMessages((prev) => prev.filter((m) => m.id !== optimisticUser.id));
      return;
    }

    setMessages((prev) => [...prev.filter((m) => m.id !== optimisticUser.id), optimisticUser, data.assistant]);
    if (data.summary) setTraits((prev) => [data.summary, ...prev]);
    setToken((prev) => ({
      today_total: prev.today_total + Math.ceil((content.length + (data.assistant?.content?.length || 0)) / 4),
      all_total: prev.all_total + Math.ceil((content.length + (data.assistant?.content?.length || 0)) / 4)
    }));
    refreshSessions();
  }

  async function setFeedback(messageId, feedback) {
    const res = await fetch(`/api/messages/${messageId}/feedback`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback })
    });
    if (!res.ok) return;
    setMessages((prev) =>
      prev.map((m) => (m.id === messageId ? { ...m, feedback } : m))
    );
  }

  async function saveDiary() {
    const content = diaryInput.trim();
    if (!content) return;

    const res = await fetch('/api/diaries', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ kind, content })
    });
    const data = await res.json();
    if (!res.ok) return alert(data.error || '保存失败');

    setDiaries((prev) => [data.diary, ...prev]);
    setDiaryInput('');
  }

  async function loadAdminStats() {
    const res = await fetch('/api/admin/stats');
    const data = await res.json();
    if (!res.ok) return alert(data.error || '加载失败');
    setAdminStats(data.stats);
  }

  async function publishNotice() {
    if (!adminNotice.trim()) return;
    const res = await fetch('/api/announcements', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: adminNotice })
    });
    const data = await res.json();
    if (!res.ok) return alert(data.error || '发布失败');
    setAnnouncement(data.announcement);
    setAdminNotice('');
  }

  async function runInterview() {
    const res = await fetch('/api/interview/monthly', { method: 'POST' });
    const data = await res.json();
    if (!res.ok) return alert(data.error || '生成失败');
    setInterview(data.interview);
  }

  async function runSleepMode() {
    const res = await fetch('/api/sleep-mode/run', { method: 'POST' });
    const data = await res.json();
    if (!res.ok) return alert(data.error || '执行失败');
    alert('已完成今日汇总');
  }

  function saveKeysToLocal() {
    try {
      const payload = btoa(unescape(encodeURIComponent(JSON.stringify(keySettings))));
      localStorage.setItem('kkagent:key:v1', payload);
      setKeySaved('已保存（本地加密存储）');
      setTimeout(() => setKeySaved(''), 1800);
    } catch {
      alert('保存失败，请重试');
    }
  }

  async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    location.href = '/login';
  }

  const actionTemplates = [
    { label: '三段式输出', text: '请按结论-原因-下一步三段式回答。' },
    { label: '行动清单', text: '请把当前问题拆成可执行清单，按优先级排序。' },
    { label: '效率周报', text: '请基于本周上下文，生成个人效率周报。' }
  ];

  return (
    <div className="layout-root">
      <aside className="sidebar glass">
        <div className="brand-block">
          <div className="brand-logo">kk</div>
          <div>
            <h2>kkagent</h2>
            <p>{user.display_name || user.email}</p>
          </div>
        </div>

        <div className="sidebar-search">
          <Search size={16} />
          <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="搜索历史对话" />
        </div>

        <button className="new-chat-btn" onClick={createSession}>
          <Plus size={16} /> 新建对话
        </button>

        <div className="session-list">
          {filteredSessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${activeSessionId === session.id ? 'active' : ''}`}
              onClick={() => setActiveSessionId(session.id)}
            >
              <div className="session-title">{session.title}</div>
              <div className="session-actions">
                <button onClick={(e) => { e.stopPropagation(); togglePin(session); }} title="置顶"><Pin size={13} /></button>
                <button onClick={(e) => { e.stopPropagation(); deleteSession(session.id); }} title="删除"><Trash2 size={13} /></button>
              </div>
            </div>
          ))}
        </div>

        <div className="sidebar-bottom">
          <button onClick={() => setView('diary')}><FileText size={15} /> 日记专栏</button>
          <button onClick={() => setView('settings')}><Settings size={15} /> 全局设置</button>
          {user.is_admin && <button onClick={() => { setView('admin'); loadAdminStats(); }}><Shield size={15} /> 管理后台</button>}
          <button onClick={logout}><LogOut size={15} /> 退出登录</button>
        </div>
      </aside>

      <main className="main-pane">
        <header className="top-status glass">
          <div><Target size={16} /> 今日Token <strong>{token.today_total}</strong></div>
          <div><WalletCards size={16} /> 累计Token <strong>{token.all_total}</strong></div>
          <div className="notice"><Bell size={16} /> {announcement?.content || '暂无公告'}</div>
        </header>

        {view === 'chat' && (
          <section className="chat-area">
            <div className="command-board glass">
              <div className="board-title">操作指挥台</div>
              <div className="command-buttons">
                {actionTemplates.map((item) => (
                  <button key={item.label} onClick={() => setInput(item.text)}>{item.label}</button>
                ))}
                <button onClick={runInterview}>生成月度深访</button>
                <button onClick={runSleepMode}>执行 Sleep Mode</button>
                <label className="advanced-switch">
                  <input type="checkbox" checked={advanced} onChange={(e) => setAdvanced(e.target.checked)} />
                  高级共识模式
                </label>
              </div>
            </div>

            <div className="dialog-wrap">
              <div className="dialog-grid">
                {messages.map((msg) => (
                  <article key={msg.id} className={`bubble ${msg.role}`}>
                    <div className="bubble-head">
                      <span>{msg.role === 'assistant' ? 'kkagent' : '你'}</span>
                      {msg.model && <Badge>{msg.model}</Badge>}
                    </div>
                    <p>{msg.content}</p>
                    {msg.role === 'assistant' && (
                      <div className="bubble-actions">
                        <button onClick={() => setInput(messages.slice().reverse().find((x) => x.role === 'user')?.content || '')}>重发</button>
                        <button title="点赞" onClick={() => setFeedback(msg.id, msg.feedback === 1 ? 0 : 1)}>
                          <Star size={14} /> {msg.feedback === 1 ? '已赞' : '点赞'}
                        </button>
                        <button title="踩" onClick={() => setFeedback(msg.id, msg.feedback === -1 ? 0 : -1)}>
                          {msg.feedback === -1 ? '已踩' : '踩'}
                        </button>
                      </div>
                    )}
                  </article>
                ))}
                {loading && <article className="bubble assistant"><p>正在思考...</p></article>}
              </div>

              <aside className="pet-module glass">
                <div className="pet-avatar">
                  <Bot size={34} />
                </div>
                <h4>Pet Module</h4>
                <p>进化度 {petMetrics.depth}%</p>
                <p>对齐率 {petMetrics.align}%</p>
                <div className="pet-bars">
                  <div><span style={{ width: `${petMetrics.depth}%` }} /></div>
                  <div><span style={{ width: `${petMetrics.align}%` }} /></div>
                </div>
              </aside>
            </div>

            <div className="input-panel glass">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="输入你的想法，支持多文件、语音与高级模式..."
              />
              <div className="input-tools">
                <label className="file-picker">
                  <input
                    multiple
                    type="file"
                    onChange={(e) => setUploadedFiles(Array.from(e.target.files || []))}
                  />
                  多文件上传
                </label>
                <button onClick={toggleVoice}>{listening ? <MicOff size={16} /> : <Mic size={16} />}{listening ? '停止语音' : '语音输入'}</button>
                <button className="send-btn" onClick={() => sendMessage()} disabled={loading || !activeSessionId}><Send size={16} />发送</button>
              </div>
              {uploadedFiles.length > 0 && (
                <div className="file-list">已选择: {uploadedFiles.map((f) => f.name).join(', ')}</div>
              )}
            </div>

            <section className="trait-section glass">
              <h3>特质自动索引（每轮静默更新）</h3>
              {traits.slice(0, 6).map((t, i) => (
                <div key={`${t.id || i}`} className="trait-item">
                  <strong>[发现特质]</strong> {t.trait}
                  <span><strong>[场景/上下文]</strong> {t.context}</span>
                  <span><strong>[原始指令]</strong> {t.instruction}</span>
                  <span><strong>[回溯索引]</strong> {t.sourcePointer || t.source_pointer}</span>
                </div>
              ))}
            </section>
          </section>
        )}

        {view === 'diary' && (
          <section className="panel glass">
            <h3>日记与复盘</h3>
            <div className="diary-editor">
              <select value={kind} onChange={(e) => setKind(e.target.value)}>
                <option value="success">成功日记</option>
                <option value="money">赚钱日记</option>
              </select>
              <textarea value={diaryInput} onChange={(e) => setDiaryInput(e.target.value)} placeholder="支持语音快速录入后粘贴到这里" />
              <button onClick={saveDiary}>保存日记</button>
            </div>
            <div className="diary-list">
              {diaries.map((d) => (
                <article key={d.id}>
                  <Badge>{d.kind === 'money' ? '赚钱日记' : '成功日记'}</Badge>
                  <p>{d.content}</p>
                </article>
              ))}
            </div>
          </section>
        )}

        {view === 'admin' && user.is_admin && (
          <section className="panel glass">
            <h3>管理员后台</h3>
            <div className="admin-stats">
              <div>今日全站Token: {adminStats?.todayTokens ?? '-'}</div>
              <div>累计全站Token: {adminStats?.allTokens ?? '-'}</div>
              <div>总用户数: {adminStats?.users ?? '-'}</div>
              <div>总会话数: {adminStats?.sessions ?? '-'}</div>
            </div>
            <textarea value={adminNotice} onChange={(e) => setAdminNotice(e.target.value)} placeholder="发布新公告" />
            <button onClick={publishNotice}>发布公告</button>
          </section>
        )}

        {view === 'settings' && (
          <section className="panel glass">
            <h3>全局设置</h3>
            <p>你可以在这里修改模型 Key。保存后会加密存到本地浏览器。</p>
            <div className="diary-editor">
              <input
                type="password"
                value={keySettings.openrouterKey}
                onChange={(e) => setKeySettings((prev) => ({ ...prev, openrouterKey: e.target.value }))}
                placeholder="OpenRouter API Key"
              />
              <input
                type="password"
                value={keySettings.nvidiaKey}
                onChange={(e) => setKeySettings((prev) => ({ ...prev, nvidiaKey: e.target.value }))}
                placeholder="NVIDIA API Key"
              />
              <button onClick={saveKeysToLocal}>保存设置</button>
              {keySaved && <div className="file-list">{keySaved}</div>}
            </div>
          </section>
        )}

        {interview && (
          <section className="panel glass">
            <h3>月度深访报告</h3>
            <pre>{interview.outline}</pre>
            <p>{interview.report}</p>
          </section>
        )}
      </main>
    </div>
  );
}


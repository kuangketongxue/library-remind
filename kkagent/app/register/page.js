"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');

    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, displayName })
    });

    const data = await res.json();
    setLoading(false);

    if (!res.ok) {
      setError(data.error || '注册失败');
      return;
    }

    router.push('/dashboard');
    router.refresh();
  }

  return (
    <main className="auth-shell">
      <section className="auth-card glass">
        <h1>创建 kkagent 账号</h1>
        <p>首个账号将自动成为管理员</p>
        <form onSubmit={handleSubmit}>
          <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="昵称" type="text" />
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="邮箱" type="email" required />
          <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="密码（至少6位）" type="password" required />
          {error && <div className="error-text">{error}</div>}
          <button disabled={loading}>{loading ? '创建中...' : '创建账号'}</button>
        </form>
        <a href="/login">已有账号？去登录</a>
      </section>
    </main>
  );
}


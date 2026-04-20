"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const router = useRouter();

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError('');

    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    setLoading(false);

    if (!res.ok) {
      setError(data.error || '登录失败');
      return;
    }

    router.push('/dashboard');
    router.refresh();
  }

  return (
    <main className="auth-shell">
      <section className="auth-card glass">
        <h1>kkagent</h1>
        <p>个人进化实验室</p>
        <form onSubmit={handleSubmit}>
          <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="邮箱" type="email" required />
          <input value={password} onChange={(e) => setPassword(e.target.value)} placeholder="密码" type="password" required />
          {error && <div className="error-text">{error}</div>}
          <button disabled={loading}>{loading ? '登录中...' : '登录'}</button>
        </form>
        <a href="/register">还没有账号？去注册</a>
      </section>
    </main>
  );
}


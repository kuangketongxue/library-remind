import './globals.css';

export const metadata = {
  title: 'kkagent | 个人进化实验室',
  description: '高频对话与深度访谈驱动个人成长'
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}



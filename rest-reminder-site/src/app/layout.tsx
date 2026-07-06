import type { Metadata } from "next";
import Navbar from "@/components/Navbar";
import AnnouncementModal from "@/components/AnnouncementModal";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rest Reminder — 免费开源 Windows久坐提醒软件 | 护眼番茄钟 | B站视频休息提醒",
  description: "免费开源的Windows桌面久坐提醒工具。48MB轻量安装，60分钟自动休息循环+请辨倒计时+5分钟休息+B站护眼视频。学习时长追踪、连续打卡、AI学习分析、趋势可视化。MIT协议，数据完全本地存储。",
  keywords: ["久坐提醒", "番茄钟", "护眼提醒", "Windows桌面工具", "开源免费", "学习计时", "工作休息提醒", "B站护眼视频", "桌面挂件", "考研", "久坐", "眼睛疲劳"],
  icons: { icon: "/favicon.png" },
  openGraph: {
    title: "Rest Reminder — 保护你的眼睛，从每一次休息开始",
    description: "桌面休息提醒挂件，48MB轻量安装，60分钟自动循环。学习时长追踪、AI学习分析、趋势可视化。MIT开源，数据完全本地。",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh" className="h-full antialiased">
      <body className="min-h-full flex flex-col bg-[var(--bg)] text-[var(--fg)]">
        <Navbar />
        <AnnouncementModal />
        <div className="pt-16 flex-1 flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}

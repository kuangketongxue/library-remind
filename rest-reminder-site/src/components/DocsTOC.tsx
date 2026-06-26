"use client";

export interface TocItem {
  id: string;
  label: string;
  level: number;
}

export default function DocsTOC({ items }: { items: TocItem[] }) {
  return (
    <aside className="hidden xl:block w-48 shrink-0">
      <div className="sticky top-24">
        <p className="text-xs font-semibold text-[var(--fg-muted)] uppercase tracking-wider mb-3">
          本页内容
        </p>
        <nav className="space-y-1">
          {items.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`block text-[13px] transition-colors ${
                item.level === 2
                  ? "text-[var(--fg)] font-medium"
                  : "text-[var(--fg-dim)] pl-3"
              }`}
            >
              {item.label}
            </a>
          ))}
        </nav>
      </div>
    </aside>
  );
}

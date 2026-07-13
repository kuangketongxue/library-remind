"use client";

import { useEffect } from "react";
import { useI18n } from "@/lib/i18n";

/**
 * Syncs document-level metadata to the current locale.
 * layout.tsx is a Server Component (static metadata for SEO crawlers),
 * so the live title/lang switch happens here on the client.
 */
export default function MetadataSync() {
  const { locale, t } = useI18n();

  useEffect(() => {
    document.title = t("site.title");

    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute("content", t("site.description"));
    }

    document.documentElement.lang = locale;
  }, [locale, t]);

  return null;
}

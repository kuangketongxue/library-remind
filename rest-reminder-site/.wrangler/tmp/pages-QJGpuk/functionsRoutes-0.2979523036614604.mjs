import { onRequestOptions as __api_ai_proxy_js_onRequestOptions } from "C:\\Users\\binlo\\Desktop\\休息提醒\\rest-reminder-site\\functions\\api\\ai-proxy.js"
import { onRequestPost as __api_ai_proxy_js_onRequestPost } from "C:\\Users\\binlo\\Desktop\\休息提醒\\rest-reminder-site\\functions\\api\\ai-proxy.js"

export const routes = [
    {
      routePath: "/api/ai-proxy",
      mountPath: "/api",
      method: "OPTIONS",
      middlewares: [],
      modules: [__api_ai_proxy_js_onRequestOptions],
    },
  {
      routePath: "/api/ai-proxy",
      mountPath: "/api",
      method: "POST",
      middlewares: [],
      modules: [__api_ai_proxy_js_onRequestPost],
    },
  ]
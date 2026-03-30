import { contextBridge } from 'electron'

contextBridge.exposeInMainWorld('goldApi', {
  getVersion: () => '0.1.0',
  fetchNow: async () => {
    try {
      const { default: fetch } = await import('node-fetch')
      const proxy = process.env.http_proxy || process.env.HTTP_PROXY || null
      let agent = undefined
      if (proxy) {
        const { HttpsProxyAgent } = await import('https-proxy-agent')
        agent = new HttpsProxyAgent(proxy)
      }
      const controller = new AbortController()
      const timer = setTimeout(() => controller.abort(), 10000)
      const resp = await fetch('https://m.cmbchina.com/api/rate/gold', { agent, signal: controller.signal })
      clearTimeout(timer)
      if (!resp.ok) {
        return { time: null, items: [], error: `HTTP ${resp.status}` }
      }
      const data = await resp.json()
      const time = data?.body?.time || null
      const raw = Array.isArray(data?.body?.data) ? data.body.data : []
      const items = raw
        .filter(it => it?.curPrice && it.curPrice !== '0')
        .map(it => ({
          name: it.variety,
          curPrice: it.curPrice,
          upDown: it.upDown,
          high: it.high,
          low: it.low
        }))
      return { time, items, error: null }
    } catch (e) {
      return { time: null, items: [], error: e?.message || String(e) }
    }
  }
})

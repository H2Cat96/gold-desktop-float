const { contextBridge, ipcRenderer } = require('electron')
const fs   = require('fs')
const path = require('path')
const os   = require('os')

const dataDir     = path.join(os.homedir(), '.desktop-float-gold')
const historyPath = path.join(dataDir, 'history.json')
fs.mkdirSync(dataDir, { recursive: true })

const PRODUCTS = [
  { code: 'Au9999',  name: '黄金9999' },
  { code: 'Au(T+D)', name: '黄金T+D'  },
  { code: 'Ag(T+D)', name: '白银T+D'  },
  { code: 'Au9995',  name: '黄金9995' },
  { code: 'Au100g',  name: '金条100g' },
]

const HEADERS = {
  'Accept': '*/*',
  'Accept-Language': 'zh-CN,zh;q=0.9',
  'Cache-Control': 'no-cache',
  'Pragma': 'no-cache',
  'Referer': 'https://finance.sina.com.cn/',
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

function getToday() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

function loadHistory() {
  try {
    if (fs.existsSync(historyPath)) return JSON.parse(fs.readFileSync(historyPath, 'utf8'))
  } catch (_) {}
  return {}
}

function saveToHistory(items) {
  const today = getToday()
  const now   = Date.now()
  const all   = loadHistory()
  if (!all[today]) all[today] = {}
  for (const it of items) {
    const arr  = all[today][it.name] || []
    const p    = parseFloat(it.curPrice)
    const last = arr[arr.length - 1]
    // 价格变化或距上次 ≥60s 时才写入新点，否则更新时间戳
    if (!last || last.p !== p || now - last.t > 60000) {
      arr.push({ t: now, p })
    } else {
      arr[arr.length - 1].t = now
    }
    all[today][it.name] = arr
  }
  try { fs.writeFileSync(historyPath, JSON.stringify(all)) } catch (_) {}
}

async function fetchSina() {
  const codes = PRODUCTS.map(p => p.code).join(',')
  // rn= 随机数是新浪客户端防缓存惯例，同时也能绕过部分访问限制
  const url   = `https://hq.sinajs.cn/rn=${Date.now()}&list=${codes}`
  const ctrl  = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 10000)
  try {
    const resp = await fetch(url, { signal: ctrl.signal, headers: HEADERS })
    clearTimeout(timer)
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    // 新浪返回 GB18030 编码
    const buf  = await resp.arrayBuffer()
    const text = new TextDecoder('gbk').decode(buf)
    const items = []
    const re = /hq_str_([^=\s]+)="([^"]*)"/g
    let m
    while ((m = re.exec(text)) !== null) {
      const code = m[1]
      const raw  = m[2]
      if (!raw) continue
      const prod = PRODUCTS.find(p => p.code === code)
      if (!prod) continue
      const parts = raw.split(',')
      const cur  = parseFloat(parts[3])
      const pre  = parseFloat(parts[2])
      const high = parseFloat(parts[4])
      const low  = parseFloat(parts[5])
      if (!cur || cur === 0) continue
      const chg = cur - pre
      const pct = pre ? chg / pre * 100 : 0
      items.push({
        name:     prod.name,
        code:     prod.code,
        curPrice: cur.toFixed(2),
        upDown:   `${chg >= 0 ? '+' : ''}${pct.toFixed(2)}%`,
        high:     high.toFixed(2),
        low:      low.toFixed(2),
        preClose: pre,
        time:     parts[11] || '',
      })
    }
    if (items.length) saveToHistory(items)
    return { error: null, items }
  } catch (e) {
    clearTimeout(timer)
    // 新浪失败时降级到招商银行
    return await fetchCmbFallback()
  }
}

async function fetchCmbFallback() {
  try {
    const ctrl  = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), 10000)
    const resp  = await fetch('https://m.cmbchina.com/api/rate/gold', {
      signal: ctrl.signal,
      headers: { 'User-Agent': HEADERS['User-Agent'] }
    })
    clearTimeout(timer)
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const data  = await resp.json()
    const raw   = Array.isArray(data?.body?.data) ? data.body.data : []
    const items = raw
      .filter(it => it?.curPrice && parseFloat(it.curPrice) !== 0)
      .map(it => ({
        name:     it.variety,
        code:     it.variety,
        curPrice: it.curPrice,
        upDown:   it.upDown,
        high:     it.high,
        low:      it.low,
        preClose: null,
        time:     data?.body?.time || '',
      }))
    if (items.length) saveToHistory(items)
    return { error: null, items }
  } catch (e) {
    return { error: e?.message || String(e), items: [] }
  }
}

contextBridge.exposeInMainWorld('winApi', {
  mouseEnter: () => ipcRenderer.send('mouse-enter'),
  mouseLeave: () => ipcRenderer.send('mouse-leave'),
})

contextBridge.exposeInMainWorld('goldApi', {
  getVersion:  () => '0.1.0',
  fetchAll:    fetchSina,
  getHistory:  (date) => {
    const all = loadHistory()
    return all[date || getToday()] || {}
  },
  getDates:    () => Object.keys(loadHistory()).sort(),
  getProducts: () => PRODUCTS,
})

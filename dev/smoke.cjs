// 离线 smoke test：假 window / 假 React / 假 ctx，验证客户端半区能加载、注册对槽位、字典齐全。
const fs = require('node:fs')
const path = require('node:path')

const FILE = path.join(__dirname, '..', 'client.js')
const code = fs.readFileSync(FILE, 'utf8')

let factory = null
global.window = {
  __ModuleLoader__: {
    load(entry) {
      if (typeof entry.factory !== 'function') throw new Error('factory missing')
      factory = entry.factory
    },
  },
  localStorage: {
    _v: new Map(),
    getItem(k) { return this._v.has(k) ? this._v.get(k) : null },
    setItem(k, v) { this._v.set(k, String(v)) },
  },
  addEventListener() {},
  removeEventListener() {},
  innerWidth: 1280,
  innerHeight: 800,
}
global.document = {
  addEventListener() {},
  removeEventListener() {},
  activeElement: null,
}
global.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve({ ok: true, value: { pages: [] } }) })
global.setInterval = () => 0
global.clearInterval = () => {}

// 迷你 React：只够工厂建组件，不渲染。
const React = {
  Fragment: 'Fragment',
  createElement: (type, props, ...children) => ({ type, props, children }),
  useState: (init) => [typeof init === 'function' ? init() : init, () => {}],
  useEffect: () => {},
  useRef: (init) => ({ current: init === undefined ? null : init }),
  Component: class {
    constructor(props) { this.props = props; this.state = {} }
    setState() {}
  },
}
const requireStub = (name) => {
  if (name === 'react') return React
  throw new Error('unexpected require: ' + name)
}

require('node:vm').runInThisContext(code, { filename: FILE })
if (typeof factory !== 'function') throw new Error('client.js did not register a factory')

const plugin = factory(requireStub)

const results = []
const ok = (name, cond, extra) => results.push([!!cond, name, extra])

ok('plugin exports inject', Array.isArray(plugin.inject), JSON.stringify(plugin.inject))
ok('inject has slots', plugin.inject.includes('slots'))
ok('inject has locale', plugin.inject.includes('locale'))

// 假 ctx：记录 locale 注册、slot 注册、快捷键注册
const dicts = {}
const registered = []
const shortcuts = []
const ctx = {
  effect(fn) { const d = fn(); return typeof d === 'function' ? d : () => {} },
  inject(deps, cb) {
    if (Array.isArray(deps) && deps.includes('shortcuts')) {
      cb({ effect: (fn) => { const d = fn(); return typeof d === 'function' ? d : () => {} }, shortcuts: { register: (cmd) => { shortcuts.push(cmd); return () => {} } } })
    } else {
      cb({})
    }
  },
  locale: {
    register(ns, dict) { dicts[ns] = dict; return () => {} },
    bind() { return (k) => k },
    getSnapshot() { return { active: 'zh' } },
    subscribe() { return () => {} },
  },
  slots: {
    inject(name, cb) { return cb() },
    register(options, component) {
      registered.push({ name: options.name, id: options.id, order: options.order, component })
      return () => {}
    },
  },
}

plugin.apply(ctx)

const slotNames = registered.map((r) => r.name)
ok('registers toggle slot', slotNames.includes('conversation.input.left'), slotNames.join(','))
ok('registers panel slot on shell.overlay', slotNames.includes('shell.overlay'), slotNames.join(','))
ok('no legacy overlay slot', !slotNames.includes('conversation.input.overlay'))
ok('both components are functions', registered.every((r) => typeof r.component === 'function'))

// 字典：中英 key 集合必须一致（缺一个就会显示成 key）
const NS_ID = 'dsh-prompt-input'
const zh = dicts[NS_ID] && dicts[NS_ID].zh
const en = dicts[NS_ID] && dicts[NS_ID].en
ok('dict registered', !!zh && !!en)
if (zh && en) {
  const zk = Object.keys(zh).sort()
  const ek = Object.keys(en).sort()
  const missingEn = zk.filter((k) => !(k in en))
  const missingZh = ek.filter((k) => !(k in zh))
  ok('zh/en keys match', missingEn.length === 0 && missingZh.length === 0, JSON.stringify({ missingEn, missingZh }))
  const needed = ['searchPlaceholder', 'noResults', 'searchCount', 'editCellShort']
  ok('new search keys present', needed.every((k) => k in zh && k in en), JSON.stringify(needed.filter((k) => !(k in zh) || !(k in en))))
  const p1Keys = ['previewMeta', 'previewHint', 'shortcutToggle']
  ok('P1 dict keys present', p1Keys.every((k) => k in zh && k in en), JSON.stringify(p1Keys.filter((k) => !(k in zh) || !(k in en))))
}

// 快捷键注册
ok('shortcut registered', shortcuts.length === 1, String(shortcuts.length))
if (shortcuts.length === 1) {
  const cmd = shortcuts[0]
  ok('shortcut id', cmd.id === NS_ID + '.toggle', cmd.id)
  const win = cmd.defaults && cmd.defaults['desktop:windows']
  ok('shortcut desktop default = Ctrl+Shift+K', !!win && win.code === 'KeyK' && win.modifiers.includes('primary') && win.modifiers.includes('shift'), JSON.stringify(win))
  ok('shortcut has label fn', typeof cmd.label === 'function')
  const passWithModal = cmd.resolve({ modal: 'anything' })
  ok('shortcut passes when a modal is open', passWithModal && passWithModal.status === 'pass', JSON.stringify(passWithModal))
  const noSession = cmd.resolve({ modal: null })
  ok('shortcut passes without session', noSession && noSession.status === 'pass', JSON.stringify(noSession))
}

let failed = 0
for (const [pass, name, extra] of results) {
  console.log((pass ? 'OK   ' : 'FAIL ') + name + (extra && !pass ? '  -> ' + extra : ''))
  if (!pass) failed++
}
console.log('\n' + (failed === 0 ? 'ALL PASS' : failed + ' FAILED'))
process.exit(failed === 0 ? 0 : 1)

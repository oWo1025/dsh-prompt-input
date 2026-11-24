/**
 * 离线验证 0.4.0 的预设迁移：把真实 presets.json 复制到临时 DSH_HOME，
 * 用假的 ctx 跑一次 apply，检查新路径是否生成、页数是否一致、旧文件是否还在。
 */
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')

const REAL = path.join(os.homedir(), '.dsh', 'quick-input', 'presets.json')
const INDEX = path.join(__dirname, '..', 'index.js')

function ok(name, pass, detail) {
  console.log(`${pass ? 'OK  ' : 'FAIL'} ${name}${detail ? '  -> ' + detail : ''}`)
  if (!pass) process.exitCode = 1
}

;(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'dsh-migrate-'))
  fs.mkdirSync(path.join(tmp, 'quick-input'), { recursive: true })
  fs.copyFileSync(REAL, path.join(tmp, 'quick-input', 'presets.json'))

  const source = JSON.parse(fs.readFileSync(REAL, 'utf8'))
  const sourcePages = Array.isArray(source.pages) ? source.pages.length : 0

  process.env.DSH_HOME = tmp
  const mod = await import('file://' + INDEX.replace(/\\/g, '/'))

  const logs = []
  const routes = []
  const ctx = {
    logger: () => ({
      info: (...a) => logs.push(['info', a.join(' ')]),
      warn: (...a) => logs.push(['warn', a.join(' ')]),
    }),
    inject: (_names, cb) =>
      cb({
        effect: (factory) => {
          factory()
        },
        webServer: {
          register: (spec) => {
            routes.push(spec.path)
            return () => {}
          },
        },
      }),
  }

  mod.apply(ctx, {})

  const nextFile = path.join(tmp, 'dsh-prompt-input', 'presets.json')
  const legacyFile = path.join(tmp, 'quick-input', 'presets.json')

  ok('新路径已生成', fs.existsSync(nextFile), nextFile)
  ok('旧文件保留', fs.existsSync(legacyFile))
  ok('路由前缀已改名', routes.includes('/dsh-prompt-input'), routes.join(','))

  if (fs.existsSync(nextFile)) {
    const next = JSON.parse(fs.readFileSync(nextFile, 'utf8'))
    ok('页数一致', next.pages.length === sourcePages, `${next.pages.length} vs ${sourcePages}`)
    ok('首格文本非空', Boolean(next.pages[0].cells.some((c) => c && c.text)), '')
  }

  // 幂等：再跑一次不应改变已有文件
  if (fs.existsSync(nextFile)) {
    const before = fs.readFileSync(nextFile, 'utf8')
    mod.apply(ctx, {})
    ok('重复启动不改写已有文件', fs.readFileSync(nextFile, 'utf8') === before)
  }

  console.log('\n--- 插件日志 ---')
  for (const [level, line] of logs) console.log(`[${level}] ${line}`)

  fs.rmSync(tmp, { recursive: true, force: true })
  console.log(`\n临时目录已清理: ${tmp}`)
})()

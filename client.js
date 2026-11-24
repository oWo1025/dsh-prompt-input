/**
 * 快捷输入 —— 浏览器半区。
 *
 * 这段代码不是被 import 的，而是被 DSH 的客户端模块加载器当成脚本文本取走、
 * 在页面里执行。约定：
 *   1. 调用 window.__ModuleLoader__.load({ id, factory })
 *   2. id 必须等于 package.json 里的包名
 *   3. factory(require) 里用 require('react') 拿 React（宿主模块表提供，不要自己装）
 *   4. factory 只负责返回插件对象，副作用放在 apply 里
 *
 * 它做三件事：
 *   - 在输入框工具行最左边画一个 ⊞（槽位 conversation.input.left）
 *   - 点开后，在输入框左上角浮出 3×3 九宫格（槽位 conversation.input.overlay）
 *   - 点某一格 → 把该格文字插到草稿的「光标处」（官方 inputActions.insertText）
 *
 * 不碰 document.body、不读别的插件的 DOM、不 require 任何 @deepseek-ai/* 包。
 */

window.__ModuleLoader__.load({
  id: 'dsh-prompt-input',
  factory(require) {
    const React = require('react')
    const h = React.createElement

    // ------------------------------------------------------------ 常量

    const TOGGLE_SLOT = 'conversation.input.left'
    const PANEL_SLOT = 'shell.overlay'
    const API = '/quick-input'

    /** 客户端构建号：页面加载时回报给宿主，`GET /quick-input/health` 里能看到跑的是哪一份。 */
    const CLIENT_BUILD = '0.3.2+build1'

    /** 文案命名空间：注册槽位时带上它，槽位就会把 `t` 交给组件。 */
    const NS = 'quick-input'

    /**
     * 中英文字典。DSH 的 locale 服务要求一次把两种语言都注册齐；
     * 缺 key 时会依次回退到 common 命名空间，最后直接显示 key 本身。
     * `{name}` 是占位符，由 t(key, { name }) 填。
     */
    const DICT = {
      zh: {
        toggleShow: '展开快捷输入（常驻在输入框左边）',
        toggleHide: '收起快捷输入',
        toggleAria: '快捷输入',
        panelAria: '快捷输入九宫格',
        prevPage: '上一页',
        nextPage: '下一页',
        addPage: '新增一页',
        addPageShort: '＋页',
        editPresets: '编辑预设',
        finishEdit: '完成编辑',
        done: '完成',
        collapse: '收起（也可点 ⊞）',
        pageName: '页名',
        deletePage: '删页',
        deletePageHint: '至少要保留一页',
        pageNumber: '第 {index} 页',
        pageHint: '{title} · 第 {index}/{total} 页',
        loading: '正在读取预设…',
        readFailed: '读预设失败：{message}',
        retry: '重试',
        retryRead: '读预设失败，重试',
        unknownError: '未知错误',
        unnamed: '未命名',
        emptyCell: '这一格还空着，点一下填内容',
        editCell: '改这一格：{text}',
        cellName: '名称',
        cellNamePlaceholder: '格子上显示的短标签',
        cellText: '内容',
        cellTextPlaceholder: '点击这一格时要插进输入框的文字',
        save: '保存',
        saving: '保存中…',
        clearCell: '清空此格',
        back: '返回',
        saved: '已保存',
        cleared: '已清空这一格',
        newPageReady: '新页已建好，填第一个格子吧',
        textRequired: '内容不能为空；想清空这一格请用右边那个按钮',
        pageGone: '这一页已经不存在了',
        inserted: '已插入：{text}',
        insertBusy: '正在发送，等这轮结束再点',
        insertInert: '当前输入框不可编辑',
        insertNoInput: '这个位置插不进去：输入框没接上',
        insertConflict: '草稿刚变过，再点一次',
        searchPlaceholder: '搜索 Prompt…',
        noResults: '没有匹配「{q}」',
        searchCount: '{n} 条结果 · ↑↓ 选择 · Enter 插入',
        editCellShort: '点击可编辑',
        previewMeta: '{page} · {n} 字',
        previewHint: '点击插入 · 拖动标题栏可移动位置',
        shortcutToggle: '打开 / 收起快捷输入',
        dragHint: '拖动这里移动面板（双击复位）',
        saveAsNew: '另存为新格',
        pageFull: '这一页满了（9 格），先腾一个格子',
        moveHint: '拖到别的格子或页签上可换位置（仅编辑态）',
        movedCell: '已移动',
        recentTab: '最近',
        tabsPrev: '向前翻页签',
        tabsNext: '向后翻页签',
        emptyPageTitle: '这一页还空着',
        editBarHint: '编辑中 · 拖动卡片调整顺序',
        emptyPageHint: '点底部的铅笔按钮添加第一条',
        recentHint: '最近点过的 prompt（自动保留 8 条，不可编辑）',
        moveFailed: '这次移动会丢内容，已取消',
      },
      en: {
        toggleShow: 'Show quick input (docked left of the composer)',
        toggleHide: 'Hide quick input',
        toggleAria: 'Quick input',
        panelAria: 'Quick input grid',
        prevPage: 'Previous page',
        nextPage: 'Next page',
        addPage: 'Add a page',
        addPageShort: '+ Page',
        editPresets: 'Edit presets',
        finishEdit: 'Finish editing',
        done: 'Done',
        collapse: 'Hide (or click ⊞)',
        pageName: 'Page name',
        deletePage: 'Delete',
        deletePageHint: 'Keep at least one page',
        pageNumber: 'Page {index}',
        pageHint: '{title} · page {index} of {total}',
        loading: 'Loading presets…',
        readFailed: 'Failed to load presets: {message}',
        retry: 'Retry',
        retryRead: 'Load failed — retry',
        unknownError: 'Unknown error',
        unnamed: 'Untitled',
        emptyCell: 'Empty cell — click to fill it',
        editCell: 'Edit cell: {text}',
        cellName: 'Name',
        cellNamePlaceholder: 'Short label shown on the cell',
        cellText: 'Text',
        cellTextPlaceholder: 'Text inserted into the composer when this cell is clicked',
        save: 'Save',
        saving: 'Saving…',
        clearCell: 'Clear cell',
        back: 'Back',
        saved: 'Saved',
        cleared: 'Cell cleared',
        newPageReady: 'New page created — fill in the first cell',
        textRequired: 'Text cannot be empty; use the button on the right to clear this cell',
        pageGone: 'That page no longer exists',
        inserted: 'Inserted: {text}',
        insertBusy: 'Sending — try again when this turn finishes',
        insertInert: 'The composer is not editable right now',
        insertNoInput: 'Cannot insert here: the composer is not connected',
        insertConflict: 'The draft just changed — click again',
        searchPlaceholder: 'Search prompts…',
        noResults: 'Nothing matches "{q}"',
        searchCount: '{n} results · ↑↓ to move · Enter to insert',
        editCellShort: 'click to edit',
        previewMeta: '{page} · {n} chars',
        previewHint: 'Click to insert · drag the header to move',
        shortcutToggle: 'Toggle quick input',
        dragHint: 'Drag here to move the panel (double-click to reset)',
        saveAsNew: 'Save as new cell',
        pageFull: 'This page is full (9 cells)',
        moveHint: 'Drag onto another card or a tab to move it (edit mode)',
        movedCell: 'Moved',
        recentTab: 'Recent',
        tabsPrev: 'Scroll tabs left',
        tabsNext: 'Scroll tabs right',
        emptyPageTitle: 'This page is empty',
        editBarHint: 'Editing · drag cards to reorder',
        emptyPageHint: 'Click the pencil button at the bottom to add one',
        recentHint: 'Recently inserted prompts (last 8, read-only)',
        moveFailed: 'That move would lose a cell — cancelled',
      },
    }

    /** 当前的界面语言（`en` / `zh` …），只用于"文件还不存在时种哪套示例"。 */
    let activeLocaleId = 'zh'
    /** `ctx.locale.bind(NS)` 拿到的翻译函数：给不是组件的那些函数兜底。 */
    let boundT = null

    /** 填 `{name}` 占位符。 */
    function format(template, params) {
      if (typeof template !== 'string') return ''
      if (!params) return template
      return template.replace(/\{(\w+)\}/g, (whole, key) => (params[key] === undefined ? whole : String(params[key])))
    }

    /** 中文兜底（拿不到 locale 服务时至少不会显示成 key）。 */
    function zhT(key, params) {
      return format(DICT.zh[key] ?? key, params)
    }

    /** 模块级取词：错误信息、短标签这些不在组件里的地方用它。 */
    function tr(key, params) {
      return (boundT ?? zhT)(key, params)
    }

    /** 组件取词：优先用槽位注入的 t（跟随 DSH 的语言设置），拿不到才退回模块级。 */
    function translator(props) {
      return props && typeof props.t === 'function' ? props.t : tr
    }

    const CELLS_PER_PAGE = 9
    const MAX_PAGES = 12
    const MAX_LABEL = 12
    const MAX_PAGE_TITLE = 12
    const MAX_CELL_TEXT = 2000

    /**
     * 气泡是「锚在 ⊞ 旁边的浮层」，不再和输入框卡片等高：
     * 宽度固定（窄窗口钳到视口内），高度上限固定，内容多了自己滚。
     */
    const PANEL_WIDTH = 420
    const PANEL_MAX_HEIGHT = 460
    /** 气泡与锚点之间的缝、以及离视口边缘的最小留白。 */
    const PANEL_GAP = 8
    const VIEWPORT_MARGIN = 12

    const CSS = `
.dsq-btn{box-sizing:border-box;width:28px;height:28px;flex:none;display:grid;place-items:center;padding:0;border:0;border-radius:var(--dsw-radius-sm,8px);background:transparent;color:var(--dsw-alias-label-secondary,#667085);cursor:pointer;transition:background-color .12s ease,color .12s ease,transform .12s ease}
.dsq-btn:active{transform:scale(.94)}
.dsq-btn:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));color:var(--dsw-alias-label-primary,#1f2328)}
.dsq-btn-on{color:var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe)));background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.1))}

.dsq-pop{position:fixed;z-index:60;box-sizing:border-box;display:flex;flex-direction:column;gap:10px;padding:10px;border-radius:var(--dsw-radius-lg,16px);background:var(--dsw-alias-bg-layer-2,#fff);color:var(--dsw-alias-label-primary,#1f2328);text-align:left;font-size:12px;line-height:16px;pointer-events:auto;overflow:hidden;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08));box-shadow:var(--dsw-elevation-panel,0 12px 32px rgba(16,24,40,.14));animation:dsq-in .14s ease-out}
@keyframes dsq-in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){.dsq-pop{animation:none}}

.dsq-head{display:flex;align-items:center;gap:6px;flex:none}
.dsq-searchwrap{position:relative;flex:1;min-width:0;display:flex}
.dsq-searchicon{position:absolute;left:9px;top:50%;transform:translateY(-50%);color:var(--dsw-alias-label-caption,#98a2b3);pointer-events:none}
.dsq-search{box-sizing:border-box;width:100%;height:30px;padding:0 10px 0 28px;border:1px solid transparent;border-radius:var(--dsw-radius-md,10px);background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.07));color:inherit;font-family:inherit;font-size:12px;line-height:16px;outline:none;transition:border-color .12s ease,background-color .12s ease}
.dsq-search::placeholder{color:var(--dsw-alias-label-secondary,#667085);opacity:.9}
.dsq-search:focus{border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))));background:var(--dsw-alias-bg-layer-2,#fff);box-shadow:0 0 0 3px color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 14%,transparent)}
/* 编辑态：搜索框让位给状态说明条 */
.dsq-editbar{flex:1;min-width:0;display:flex;align-items:center;gap:6px;height:30px;padding:0 10px;border:1px dashed color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 42%,transparent);border-radius:var(--dsw-radius-md,10px);background:color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 8%,transparent);color:var(--dsw-alias-label-primary,#1f2328);font-size:12px;line-height:16px}
.dsq-editbar-text{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.dsq-editbar svg{flex:none;color:var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe)))}
.dsq-x{box-sizing:border-box;flex:none;width:26px;height:26px;padding:0;border:0;border-radius:var(--dsw-radius-sm,8px);background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-size:15px;line-height:1;cursor:pointer}
.dsq-x:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));color:var(--dsw-alias-label-primary,#1f2328)}

/* 内容区：普通态定高 3 行（换页高度不变），编辑态才自适应并可滚 */
.dsq-body{flex:0 0 auto;min-height:0;display:flex;flex-direction:column;overflow:visible}
.dsq-body-auto{flex:1 1 auto;min-height:120px;overflow-y:auto;scrollbar-width:thin}
.dsq-grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-rows:52px;gap:6px;height:168px;overflow:visible}
.dsq-card{box-sizing:border-box;display:flex;flex-direction:column;gap:1px;align-items:flex-start;justify-content:flex-start;padding:7px 8px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08));border-radius:var(--dsw-radius-md,10px);background:transparent;color:inherit;font-family:inherit;font-size:12px;line-height:16px;text-align:left;cursor:pointer;overflow:hidden;transition:background-color .12s ease,border-color .12s ease,box-shadow .16s ease,transform .12s ease}
.dsq-card:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1));border-color:color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 24%,var(--dsw-alias-border-l2,rgba(0,0,0,.16)));box-shadow:0 6px 16px -10px color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 55%,transparent);transform:translateY(-1px)}
.dsq-card:active{transform:translateY(0) scale(.99);box-shadow:none}
.dsq-card:focus-visible{outline:none;border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))));box-shadow:0 0 0 2px color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 22%,transparent)}
.dsq-card-label{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;width:100%;overflow-wrap:anywhere;font-weight:600;letter-spacing:-.01em}
.dsq-card-sub{width:100%;font-size:10px;line-height:12px;color:var(--dsw-alias-label-caption,#98a2b3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.dsq-card-empty{align-items:center;justify-content:center;border-style:dashed;color:var(--dsw-alias-label-caption,#98a2b3);font-size:14px;font-weight:400}

.dsq-results{display:flex;flex-direction:column;gap:2px;height:168px;overflow-y:auto;padding-right:2px;scrollbar-width:thin}
.dsq-item{box-sizing:border-box;display:flex;align-items:center;gap:8px;height:34px;flex:none;padding:0 8px;border:0;border-radius:var(--dsw-radius-sm,8px);background:transparent;color:inherit;font-family:inherit;font-size:12px;text-align:left;cursor:pointer}
.dsq-item:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1))}
.dsq-item-on{background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.1));box-shadow:inset 2px 0 0 var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe)))}
.dsq-item-label{flex:none;max-width:46%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500}
.dsq-item-snippet{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--dsw-alias-label-secondary,#667085);font-size:11px}
.dsq-item-page{flex:none;font-size:10px;line-height:16px;color:var(--dsw-alias-label-caption,#98a2b3);padding:0 6px;border-radius:999px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08))}

/* 页签行（在底部）：位置固定，换页不会上下跳 */
.dsq-tabsrow{display:flex;align-items:center;gap:6px;flex:none;min-width:0;overflow:hidden}
.dsq-tabs{display:flex;align-items:center;gap:4px;flex:1 1 0;min-width:0;overflow-x:auto;scrollbar-width:none;padding:1px}
.dsq-tabs::-webkit-scrollbar{display:none}
.dsq-tab{box-sizing:border-box;flex:none;height:24px;padding:0 7px;border:1px solid transparent;border-radius:999px;background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-family:inherit;font-size:11px;line-height:22px;cursor:pointer;white-space:nowrap;transition:background-color .12s ease,color .12s ease,border-color .12s ease,transform .12s ease}
.dsq-tab:active{transform:scale(.96)}
.dsq-tab:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1));color:var(--dsw-alias-label-primary,#1f2328)}
.dsq-tab-on{background:color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 10%,transparent);border-color:color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 26%,transparent);color:var(--dsw-alias-label-primary,#1f2328);font-weight:600}
.dsq-tab:focus-visible{outline:none;border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))))}
.dsq-count{flex:0 1 auto;min-width:0;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px;line-height:16px;color:var(--dsw-alias-label-caption,#98a2b3);font-variant-numeric:tabular-nums}
.dsq-mini{box-sizing:border-box;flex:none;height:24px;min-width:24px;padding:0 7px;border:0;border-radius:var(--dsw-radius-sm,8px);background:transparent;color:var(--dsw-alias-label-secondary,#667085);font-family:inherit;font-size:12px;line-height:1;cursor:pointer}
.dsq-mini:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.12));color:var(--dsw-alias-label-primary,#1f2328)}
.dsq-mini:disabled{opacity:.45;cursor:default}
.dsq-mini-on{background:color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 14%,transparent);color:var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe)))}

/* 编辑态 */
.dsq-row{display:flex;align-items:center;gap:6px}
.dsq-row .dsq-input{flex:1;min-width:0;width:auto}
.dsq-row-label{flex:none;font-size:11px;color:var(--dsw-alias-label-secondary,#667085)}
.dsq-input,.dsq-textarea{box-sizing:border-box;width:100%;padding:6px 9px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.1));border-radius:var(--dsw-radius-sm,8px);background:var(--dsw-alias-bg-module-platform,rgba(127,127,127,.06));color:inherit;font-family:inherit;font-size:12px;line-height:18px;outline:none;transition:border-color .12s ease,background-color .12s ease}
.dsq-textarea{resize:vertical;min-height:96px;white-space:pre-wrap}
.dsq-input:focus,.dsq-textarea:focus{border-color:var(--dsw-alias-border-selected,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))));background:var(--dsw-alias-bg-layer-2,#fff)}
.dsq-actions{display:flex;align-items:center;gap:6px}
.dsq-action{box-sizing:border-box;flex:none;white-space:nowrap;height:28px;padding:0 12px;border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.1));border-radius:var(--dsw-radius-sm,8px);background:transparent;color:inherit;font-family:inherit;font-size:12px;line-height:18px;cursor:pointer}
.dsq-action:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1))}
.dsq-action-primary{border-color:transparent;background:var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe)));color:#fff}
.dsq-action-primary:hover{background:var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe)));opacity:.92}
.dsq-ok{color:var(--dsw-alias-state-success-primary,#12b76a)}
.dsq-err{color:var(--dsw-alias-state-error-primary,#d92d20)}
.dsq-muted{color:var(--dsw-alias-label-secondary,#667085)}

/* 半径约定：气泡 16 / 卡片 10 / 输入框与按钮 8 / 页签胶囊 999（全局只此一套） */

/* 拖拽：标题行被搜索框占满，所以左上角单独给一个六点把手 */
.dsq-grip{flex:none;width:16px;height:30px;display:grid;place-items:center;color:var(--dsw-alias-label-caption,#98a2b3);cursor:grab;border-radius:var(--dsw-radius-sm,8px);user-select:none;transition:background-color .12s ease,color .12s ease}
.dsq-grip:hover{background:var(--dsw-alias-interactive-bg-hover,rgba(127,127,127,.1));color:var(--dsw-alias-label-secondary,#667085)}
.dsq-grip:active{cursor:grabbing}
.dsq-card-drag{opacity:.45}
.dsq-card-over{border-color:var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe)));border-style:dashed}
.dsq-tab-over{background:color-mix(in srgb,var(--dsw-alias-brand-primary-new-color,var(--dsw-alias-brand-primary-new-colorprimary-new-color,var(--dsw-alias-brand-primary,#4d6bfe))) 18%,transparent);color:var(--dsw-alias-label-primary,#1f2328)}

/* 悬停预览：固定位置 + 不接收指针，鼠标可以径直移向下一张卡 */
.dsq-preview{position:fixed;z-index:61;box-sizing:border-box;padding:10px 12px;border-radius:var(--dsw-radius-md,12px);background:var(--dsw-alias-bg-layer-2,#fff);border:1px solid var(--dsw-alias-border-l1,rgba(0,0,0,.08));box-shadow:var(--dsw-elevation-panel,0 12px 32px rgba(16,24,40,.14));color:var(--dsw-alias-label-primary,#1f2328);font-size:12px;line-height:18px;pointer-events:none;overflow:hidden;animation:dsq-fade .12s ease-out}
@keyframes dsq-fade{from{opacity:0}to{opacity:1}}
@media (prefers-reduced-motion:reduce){.dsq-preview{animation:none}}
.dsq-preview-title{font-weight:600;margin-bottom:2px}
.dsq-preview-meta{font-size:10px;line-height:14px;color:var(--dsw-alias-label-caption,#98a2b3);margin-bottom:6px}
.dsq-preview-text{white-space:pre-wrap;overflow-wrap:anywhere;color:var(--dsw-alias-label-secondary,#667085);max-height:168px;overflow:hidden;-webkit-mask-image:linear-gradient(#000 74%,transparent);mask-image:linear-gradient(#000 74%,transparent)}
.dsq-preview-foot{margin-top:7px;font-size:10px;line-height:14px;color:var(--dsw-alias-label-caption,#98a2b3)}

/* 页签溢出：两端渐隐，提示"还有更多" */
.dsq-tabs-scroll{-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 12px,#000 calc(100% - 12px),transparent 100%);mask-image:linear-gradient(90deg,transparent 0,#000 12px,#000 calc(100% - 12px),transparent 100%)}

/* 空页：给一个可执行的空状态，而不是一片空白 */
.dsq-empty{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;height:168px;text-align:center;color:var(--dsw-alias-label-secondary,#667085);font-size:12px;line-height:18px}
.dsq-empty-title{font-weight:600;color:var(--dsw-alias-label-primary,#1f2328)}
`

    // ------------------------------------------------------------ 小工具

    /** 任何异常都变成一句能显示的话。 */
    function messageOf(error) {
      if (error instanceof Error && error.message) return error.message
      if (typeof error === 'string' && error !== '') return error
      return tr('unknownError')
    }

    /** 按鼠标/焦点事件不要抢走编辑器的光标（插入点靠它保住）。 */
    function keepFocus(event) {
      if (event && typeof event.preventDefault === 'function') event.preventDefault()
    }

    /** 去换行、限长的短标签。 */
    function toLabel(value, fallbackText) {
      const source = typeof value === 'string' && value.trim() !== '' ? value : fallbackText
      const flat = String(source || '').replace(/\s+/g, ' ').trim()
      if (flat === '') return tr('unnamed')
      return flat.length > MAX_LABEL ? `${flat.slice(0, MAX_LABEL - 1)}…` : flat
    }

    /** 把宿主给的文档收成页面数组；脏数据只会退化成空格子。 */
    function normalizeDoc(input) {
      const rawPages = input && Array.isArray(input.pages) ? input.pages : []
      const pages = []
      for (const rawPage of rawPages) {
        if (pages.length >= MAX_PAGES) break
        const rawCells = rawPage && Array.isArray(rawPage.cells) ? rawPage.cells : []
        const cells = []
        for (let i = 0; i < CELLS_PER_PAGE; i++) {
          const rawCell = rawCells[i]
          const text = rawCell && typeof rawCell.text === 'string' ? rawCell.text.slice(0, MAX_CELL_TEXT) : ''
          if (text.trim() === '') {
            cells.push(null)
            continue
          }
          cells.push({ label: toLabel(rawCell.label, text), text })
        }
        const flatTitle =
          rawPage && typeof rawPage.title === 'string' ? rawPage.title.replace(/\s+/g, ' ').trim() : ''
        pages.push({
          title: flatTitle === '' ? tr('pageNumber', { index: pages.length + 1 }) : flatTitle.slice(0, MAX_PAGE_TITLE),
          cells,
        })
      }
      return { pages }
    }

    function clonePages() {
      return store.doc.pages.map((page) => ({
        title: page.title,
        cells: page.cells.map((cell) => (cell ? { label: cell.label, text: cell.text } : null)),
      }))
    }

    // ------------------------------------------------------------ 开合状态

    /**
     * 气泡只在本次会话里记住开合：刷新页面/重开应用一律收起。
     * （旧版是「常驻面板」，会把这个状态写进 localStorage；气泡形态不这么做——
     *   刷新后自动弹出一个浮层是打扰，而不是恢复。）
     */
    function isOpen(sessionId) {
      return store.open.get(sessionId) === true
    }

    // ------------------------------------------------------------ 模块级共享状态

    /**
     * 两个槽位是两个独立注册项，靠这份模块级 store 通信。
     * 所有会话相关的键都用 sessionId，避免多个会话（侧边栏对话标签）串台。
     */
    const store = {
      open: new Map(),
      page: new Map(),
      /** 是否处于「编辑态」：格子的左键从「插入」变成「改这一格」。 */
      editMode: new Map(),
      /** 正在编辑哪一格：`{ page, cell }`，null 表示没在编辑器里。 */
      editing: new Map(),
      flash: new Map(),
      /** 是否停在虚拟的「最近」页。 */
      recentView: new Map(),
      doc: { status: 'idle', pages: [], error: '' },
      listeners: new Set(),
      emit() {
        for (const listener of Array.from(this.listeners)) {
          try {
            listener()
          } catch {
            /* 单个订阅者出错不该影响别人 */
          }
        }
      },
      subscribe(listener) {
        this.listeners.add(listener)
        return () => {
          this.listeners.delete(listener)
        }
      },
    }

    const flashTimers = new Map()

    // ------------------------------------------------------------ 跨槽位桥

    /**
     * ⊞ 挂在 `conversation.input.left`（会话作用域），拿得到 sessionId / inputActions；
     * 气泡挂在 `shell.overlay`（root 作用域），这些 props 都拿不到。
     * 两个半区同属一个包、同一个客户端模块，所以用这份模块级桥接传递。
     */
    const bridge = {
      sessionId: null,
      inputActions: null,
      phase: undefined,
      /** ⊞ 按钮节点：气泡靠它定位。 */
      node: null,
    }

    /** 每个会话各自的搜索态：`{ query, active }`。切会话不串台。 */
    const searchState = new Map()

    function readSearch(sessionId) {
      return searchState.get(sessionId) ?? { query: '', active: 0 }
    }

    function writeSearch(sessionId, patch) {
      searchState.set(sessionId, { ...readSearch(sessionId), ...patch })
    }

    // ------------------------------------------------------------ 最近使用

    /** 点过的 prompt 置顶，最多 8 条，按正文去重（同一条不会重复占位）。 */
    const RECENT_KEY = 'quick-input.recent.v1'
    const RECENT_MAX = 8

    function readRecent() {
      try {
        const raw = window.localStorage ? window.localStorage.getItem(RECENT_KEY) : null
        if (!raw) return []
        const list = JSON.parse(raw)
        if (!Array.isArray(list)) return []
        return list
          .filter((item) => item && typeof item.text === 'string' && typeof item.label === 'string')
          .slice(0, RECENT_MAX)
      } catch {
        return []
      }
    }

    function pushRecent(item) {
      if (!item || typeof item.text !== 'string' || item.text === '') return
      try {
        if (!window.localStorage) return
        const list = readRecent().filter((entry) => entry.text !== item.text)
        list.unshift({ label: item.label || '', text: item.text, page: item.page || '' })
        window.localStorage.setItem(RECENT_KEY, JSON.stringify(list.slice(0, RECENT_MAX)))
      } catch {
        /* 存不了就算了，不影响插入 */
      }
    }

    /** 一页页摊平成可搜索的条目。 */
    function flattenPages(pages) {
      const items = []
      pages.forEach((page, pageIndex) => {
        page.cells.forEach((cell, cellIndex) => {
          if (!cell) return
          items.push({ pageIndex, cellIndex, page: page.title, label: cell.label, text: cell.text })
        })
      })
      return items
    }

    /** 搜索：label 命中排在正文命中前面，同档按页序、格序。 */
    function searchPages(pages, query) {
      const q = String(query || '').trim().toLowerCase()
      if (q === '') return null
      const hits = []
      for (const item of flattenPages(pages)) {
        const inLabel = item.label.toLowerCase().indexOf(q) !== -1
        const inText = item.text.toLowerCase().indexOf(q) !== -1
        if (!inLabel && !inText) continue
        hits.push({ item, rank: inLabel ? 0 : 1 })
      }
      hits.sort(
        (a, b) =>
          a.rank - b.rank ||
          a.item.pageIndex - b.item.pageIndex ||
          a.item.cellIndex - b.item.cellIndex,
      )
      return hits.map((hit) => hit.item)
    }

    /** 一行摘要：压平空白后截断。 */
    function snippet(text) {
      const flat = String(text || '').replace(/\s+/g, ' ').trim()
      return flat.length > 64 ? `${flat.slice(0, 63)}…` : flat
    }

    /** 收起面板（两个半区共用）。 */
    function closePanel(sessionId) {
      store.open.set(sessionId, false)
      store.editing.set(sessionId, null)
      store.editMode.set(sessionId, false)
      store.flash.delete(sessionId)
      store.emit()
    }

    /** 在面板底部闪一条结果，2.4 秒后自动消失。 */
    function setFlash(sessionId, kind, text) {
      store.flash.set(sessionId, { kind, text })
      const previous = flashTimers.get(sessionId)
      if (previous !== undefined) clearTimeout(previous)
      flashTimers.set(
        sessionId,
        setTimeout(() => {
          flashTimers.delete(sessionId)
          store.flash.delete(sessionId)
          store.emit()
        }, 2400),
      )
      store.emit()
    }

    // ------------------------------------------------------------ 与宿主通信

    async function request(path, options) {
      const response = await fetch(`${API}${path}`, options)
      let body = null
      try {
        body = await response.json()
      } catch {
        body = null
      }
      if (!response.ok || !body || body.ok !== true) {
        const detail = body && (body.message || body.error) ? String(body.message || body.error) : ''
        throw new Error(detail === '' ? `HTTP ${response.status}` : detail)
      }
      return body.value
    }

    /** 拉一次预设；不 force 时已有数据就不重复拉。 */
    function ensureDoc(force) {
      if (store.doc.status === 'loading') return
      if (force !== true && store.doc.status === 'ready') return
      store.doc = { status: 'loading', pages: store.doc.pages, error: '' }
      store.emit()
      // 带上界面语言：预设文件还不存在时，宿主按它种一套对应语言的示例。
      request(`/presets?lang=${encodeURIComponent(activeLocaleId)}`)
        .then((value) => {
          store.doc = { status: 'ready', pages: normalizeDoc(value).pages, error: '' }
          store.emit()
        })
        .catch((error) => {
          // 读失败也保留上一次的页面：别的会话还开着面板时，不该跟着一起变空。
          store.doc = { status: 'error', pages: store.doc.pages, error: messageOf(error) }
          store.emit()
        })
    }

    /** 存一整份文档；成功后用宿主返回的规范化结果刷新本地。 */
    async function commit(pages) {
      const saved = await request('/presets', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ pages }),
      })
      store.doc = { status: 'ready', pages: normalizeDoc(saved).pages, error: '' }
      store.emit()
    }

    // ------------------------------------------------------------ 插入草稿

    /**
     * 把文字插到草稿的光标处。
     *
     * `insertText` 有两种失败原因，必须分开说：
     *   1. 正在发送/裁决（phase = adjudicating | submitting）——重试也没用，等这一轮结束；
     *   2. 草稿版本变了（用户刚好在打字）——重新抓一次光标再试，两次都失败才提示。
     * `phase` 来自槽位给的 useInput；拿不到就当未知，照常尝试。
     */
    function insertIntoDraft(inputActions, text, phase) {
      if (phase === 'adjudicating' || phase === 'submitting') {
        return { ok: false, reason: tr('insertBusy') }
      }
      if (phase === 'inert') return { ok: false, reason: tr('insertInert') }
      if (!inputActions || typeof inputActions.insertText !== 'function') {
        return { ok: false, reason: tr('insertNoInput') }
      }
      try {
        for (let attempt = 0; attempt < 2; attempt++) {
          const span = inputActions.captureInsertion()
          if (inputActions.insertText(text, span)) return { ok: true }
        }
        return { ok: false, reason: tr('insertConflict') }
      } catch (error) {
        return { ok: false, reason: messageOf(error) }
      }
    }

    /** 从 InputState 里只取 phase（原始值选择器，避免每次敲键都重渲染）。 */
    function selectPhase(state) {
      return state && typeof state.phase === 'string' ? state.phase : undefined
    }

    // ------------------------------------------------------------ 位置记忆

    /** 拖拽位移（相对锚点）按窗口宽度分档存，换分辨率不会飘到屏幕外。 */
    const POS_KEY = 'quick-input.pos.v1'

    function widthBucket() {
      const width = window.innerWidth || 1280
      return width < 900 ? 's' : width < 1400 ? 'm' : 'l'
    }

    function loadPos() {
      try {
        const raw = window.localStorage ? window.localStorage.getItem(POS_KEY) : null
        if (!raw) return null
        const all = JSON.parse(raw) || {}
        const value = all[widthBucket()]
        if (!value || typeof value.dx !== 'number' || typeof value.dy !== 'number') return null
        return { dx: value.dx, dy: value.dy }
      } catch {
        return null
      }
    }

    function savePos(value) {
      try {
        if (!window.localStorage) return
        const raw = window.localStorage.getItem(POS_KEY)
        const all = raw ? JSON.parse(raw) || {} : {}
        if (value === null) delete all[widthBucket()]
        else all[widthBucket()] = { dx: Math.round(value.dx), dy: Math.round(value.dy) }
        window.localStorage.setItem(POS_KEY, JSON.stringify(all))
      } catch {
        /* 存不了就算了 */
      }
    }

    // ------------------------------------------------------------ 气泡定位

    /**
     * 气泡位置：默认贴在 ⊞ 右边；右边放不下翻到左边；上下取空间大的一侧。
     * 用 fixed 定位——气泡在 shell.overlay 这一层，不受 composer 卡片裁剪。
     * 拖动过就叠加位移（dy 为正＝向下），并钳在视口内。
     */
    function popoverStyle(anchor, drag) {
      const vw = window.innerWidth || 1280
      const vh = window.innerHeight || 800
      const width = Math.max(300, Math.min(PANEL_WIDTH, vw - VIEWPORT_MARGIN * 2))
      let left = anchor.right + PANEL_GAP
      if (left + width > vw - VIEWPORT_MARGIN) left = anchor.left - PANEL_GAP - width
      left = Math.max(VIEWPORT_MARGIN, Math.min(left, vw - width - VIEWPORT_MARGIN))
      const above = anchor.top - VIEWPORT_MARGIN
      const below = vh - anchor.bottom - VIEWPORT_MARGIN
      const putAbove = above >= 240 || above >= below
      const space = Math.max(200, putAbove ? above : below)
      const style = { left: left, width: width, maxHeight: Math.min(PANEL_MAX_HEIGHT, space) }
      if (putAbove) style.bottom = Math.max(VIEWPORT_MARGIN, vh - anchor.top)
      else style.top = Math.max(VIEWPORT_MARGIN, anchor.bottom)

      if (drag) {
        const dx = Number(drag.dx) || 0
        const dy = Number(drag.dy) || 0
        style.left = Math.max(
          VIEWPORT_MARGIN - 40,
          Math.min(Number(style.left) + dx, vw - width - VIEWPORT_MARGIN + 40),
        )
        if (putAbove) {
          // bottom 越大越靠上，所以向下拖是减。
          style.bottom = Math.max(160, Math.min(Number(style.bottom) - dy, vh - VIEWPORT_MARGIN))
        } else {
          style.top = Math.max(VIEWPORT_MARGIN, Math.min(Number(style.top) + dy, vh - 160))
        }
      }
      return style
    }

    // ------------------------------------------------------------ hook 小工具

    /** 订阅 store：任何一处 emit 都让本组件重渲染。 */
    function useStore() {
      const [, bump] = React.useState(0)
      React.useEffect(
        () =>
          store.subscribe(() => {
            bump((n) => n + 1)
          }),
        [],
      )
    }

    // ------------------------------------------------------------ 图标

    /** 入口图标：两张叠起来的卡片 + 两行字，比九点阵更像「一叠 prompt 卡」。 */
    function GridIcon() {
      return h(
        'svg',
        { width: 16, height: 16, viewBox: '0 0 16 16', fill: 'none', stroke: 'currentColor', 'aria-hidden': 'true' },
        // 后面那张微微歪着：两卡等大会被读成"复制"，歪一点才是"一叠"。
        h(
          'g',
          { transform: 'rotate(-9 9.5 5.2)' },
          h('rect', {
            x: 4.6,
            y: 1.4,
            width: 9.2,
            height: 6.4,
            rx: 1.8,
            strokeWidth: 1.3,
            opacity: 0.42,
          }),
        ),
        h('rect', { x: 1.7, y: 6.4, width: 9.5, height: 6.6, rx: 1.9, strokeWidth: 1.3 }),
        h('path', {
          d: 'M4 9.2h4.4M4 11.3h2.8',
          strokeWidth: 1.2,
          strokeLinecap: 'round',
        }),
      )
    }

    /** 编辑：铅笔（描边风格，和其余图标统一 1.8 描边、14px 尺寸）。 */
    function PencilIcon() {
      return h(
        'svg',
        {
          width: 14,
          height: 14,
          viewBox: '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor',
          strokeWidth: 1.8,
          strokeLinecap: 'round',
          strokeLinejoin: 'round',
          'aria-hidden': 'true',
        },
        h('path', { d: 'M4 20h4L18.5 9.5a2.8 2.8 0 0 0-4-4L4 16v4z' }),
        h('path', { d: 'M13.5 6.5l4 4' }),
      )
    }

    /** 编辑完成。 */
    function CheckIcon() {
      return h(
        'svg',
        {
          width: 14,
          height: 14,
          viewBox: '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor',
          strokeWidth: 2,
          strokeLinecap: 'round',
          strokeLinejoin: 'round',
          'aria-hidden': 'true',
        },
        h('path', { d: 'M20 6L9 17l-5-5' }),
      )
    }

    /** 关闭。 */
    function CloseIcon() {
      return h(
        'svg',
        {
          width: 13,
          height: 13,
          viewBox: '0 0 24 24',
          fill: 'none',
          stroke: 'currentColor',
          strokeWidth: 1.9,
          strokeLinecap: 'round',
          'aria-hidden': 'true',
        },
        h('path', { d: 'M6 6l12 12M18 6L6 18' }),
      )
    }

    // ------------------------------------------------------------ ⊞ 开关

    function QuickToggle(props) {
      useStore()
      const t = translator(props)
      const sessionId = props.sessionId
      const open = isOpen(sessionId)
      const btnRef = React.useRef(null)
      // 只在槽位真的给了 useInput 时才订阅输入状态；拿不到当未知。
      const phase = typeof props.useInput === 'function' ? props.useInput(selectPhase) : undefined

      // 每次渲染都把最新的会话能力递给浮层（气泡在另一个作用域里）。
      React.useEffect(() => {
        bridge.sessionId = sessionId ?? null
        bridge.inputActions = props.inputActions ?? null
        bridge.phase = phase
        bridge.node = btnRef.current ?? bridge.node
      })

      return h(
        React.Fragment,
        null,
        h('style', null, CSS),
        h(
          'button',
          {
            ref: btnRef,
            type: 'button',
            className: open ? 'dsq-btn dsq-btn-on' : 'dsq-btn',
            style: { WebkitAppearance: 'none' },
            title: open ? t('toggleHide') : t('toggleShow'),
            'aria-label': t('toggleAria'),
            'aria-expanded': open ? 'true' : 'false',
            onMouseDown: keepFocus,
            onClick: () => {
              const next = open !== true
              // 先递能力再开面板：浮层的第一次渲染就能拿到 sessionId。
              bridge.sessionId = sessionId ?? null
              bridge.inputActions = props.inputActions ?? null
              bridge.phase = phase
              bridge.node = btnRef.current ?? bridge.node
              store.open.set(sessionId, next)
              if (next) ensureDoc(false)
              store.emit()
            },
          },
          h(GridIcon, null),
        ),
      )
    }

    // ------------------------------------------------------------ 单格编辑器

    /** 编辑一格：名称 + 内容；保存走 POST /quick-input/presets。 */
    function CellEditor(props) {
      const t = translator(props)
      const sessionId = props.sessionId
      const page = store.doc.pages[props.page]
      const original = page && page.cells[props.cell] ? page.cells[props.cell] : null
      const [label, setLabel] = React.useState(original ? original.label : '')
      const [text, setText] = React.useState(original ? original.text : '')
      const [busy, setBusy] = React.useState(false)
      const [error, setError] = React.useState('')

      const close = () => {
        store.editing.set(sessionId, null)
        store.emit()
      }

      const saveCell = async (value) => {
        if (busy) return
        setBusy(true)
        setError('')
        const pages = clonePages()
        const target = pages[props.page]
        if (!target) {
          setError(t('pageGone'))
          setBusy(false)
          return
        }
        target.cells[props.cell] = value
        try {
          await commit(pages)
          setFlash(sessionId, 'ok', value === null ? t('cleared') : t('saved'))
          close()
        } catch (failure) {
          setError(messageOf(failure))
        } finally {
          setBusy(false)
        }
      }

      const saveAsNew = async (value) => {
        if (busy) return
        setBusy(true)
        setError('')
        const pages = clonePages()
        const target = pages[props.page]
        if (!target) {
          setError(t('pageGone'))
          setBusy(false)
          return
        }
        const slot = target.cells.indexOf(null)
        if (slot < 0) {
          setError(t('pageFull'))
          setBusy(false)
          return
        }
        target.cells[slot] = value
        try {
          await commit(pages)
          setFlash(sessionId, 'ok', t('saved'))
          close()
        } catch (failure) {
          setError(messageOf(failure))
        } finally {
          setBusy(false)
        }
      }

      return h(
        'div',
        { className: 'dsq-actions', style: { flexDirection: 'column', alignItems: 'stretch', gap: 6 } },
        h('div', { className: 'dsq-row' }, h('span', { className: 'dsq-row-label' }, t('cellName'))),
        h('input', {
          className: 'dsq-input',
          value: label,
          maxLength: 40,
          placeholder: t('cellNamePlaceholder'),
          onChange: (event) => setLabel(event.target.value),
        }),
        h('div', { className: 'dsq-row' }, h('span', { className: 'dsq-row-label' }, t('cellText'))),
        h('textarea', {
          className: 'dsq-textarea',
          value: text,
          maxLength: MAX_CELL_TEXT,
          placeholder: t('cellTextPlaceholder'),
          onChange: (event) => setText(event.target.value),
        }),
        error !== '' ? h('div', { className: 'dsq-err' }, error) : null,
        h(
          'div',
          { className: 'dsq-actions' },
          h(
            'button',
            {
              type: 'button',
              className: 'dsq-action dsq-action-primary',
              disabled: busy,
              onClick: () => {
                if (text.trim() === '') {
                  setError(t('textRequired'))
                  return
                }
                saveCell({ label: label.trim() === '' ? toLabel('', text) : label.trim(), text })
              },
            },
            busy ? t('saving') : t('save'),
          ),
          original
            ? h(
                'button',
                { type: 'button', className: 'dsq-action', disabled: busy, onClick: () => saveCell(null) },
                t('clearCell'),
              )
            : null,
          h(
            'button',
            {
              type: 'button',
              className: 'dsq-action',
              disabled: busy,
              title: t('saveAsNew'),
              onClick: () => {
                if (text.trim() === '') {
                  setError(t('textRequired'))
                  return
                }
                saveAsNew({ label: label.trim() === '' ? toLabel('', text) : label.trim(), text })
              },
            },
            t('saveAsNew'),
          ),
          h('button', { type: 'button', className: 'dsq-action', disabled: busy, onClick: close }, t('back')),
        ),
      )
    }

    // ------------------------------------------------------------ 页名/删页

    /** 编辑态下的一行：改页名、删这一页。 */
    function PageRow(props) {
      const t = translator(props)
      const sessionId = props.sessionId
      const page = store.doc.pages[props.page]
      const [title, setTitle] = React.useState(page ? page.title : '')
      const [busy, setBusy] = React.useState(false)
      const [error, setError] = React.useState('')

      const rename = async () => {
        const next = title.replace(/\s+/g, ' ').trim()
        if (busy || !page || next === page.title) return
        setBusy(true)
        setError('')
        try {
          const pages = clonePages()
          pages[props.page].title = next
          await commit(pages)
        } catch (failure) {
          setError(messageOf(failure))
        } finally {
          setBusy(false)
        }
      }

      const removePage = async () => {
        if (busy || store.doc.pages.length <= 1) return
        setBusy(true)
        setError('')
        try {
          const pages = clonePages()
          pages.splice(props.page, 1)
          await commit(pages)
          store.page.set(sessionId, Math.max(0, props.page - 1))
          store.editing.set(sessionId, null)
          store.emit()
        } catch (failure) {
          setError(messageOf(failure))
        } finally {
          setBusy(false)
        }
      }

      return h(
        'div',
        { style: { display: 'flex', flexDirection: 'column', gap: 4 } },
        h('div', { className: 'dsq-row' }, h('span', { className: 'dsq-row-label' }, t('pageName'))),
        h(
          'div',
          { className: 'dsq-row' },
          h('input', {
            className: 'dsq-input',
            value: title,
            maxLength: 40,
            onChange: (event) => setTitle(event.target.value),
            onBlur: rename,
            onKeyDown: (event) => {
              if (event.key === 'Enter') rename()
            },
          }),
          h(
            'button',
            {
              type: 'button',
              className: 'dsq-action',
              disabled: busy || store.doc.pages.length <= 1,
              title: store.doc.pages.length <= 1 ? t('deletePageHint') : `${t('deletePage')}: ${store.doc.pages[props.page]?.title ?? ''}`,
              onClick: removePage,
            },
            t('deletePage'),
          ),
        ),
        error !== '' ? h('div', { className: 'dsq-err' }, error) : null,
      )
    }

    // ------------------------------------------------------------ 九宫格面板

    function QuickPanel(props) {
      useStore()
      const t = translator(props)
      const sessionId = bridge.sessionId
      const open = sessionId !== null && sessionId !== undefined && isOpen(sessionId)
      const [anchor, setAnchor] = React.useState(null)
      const [drag, setDrag] = React.useState(() => loadPos())
      const [preview, setPreview] = React.useState(null)
      const [cellDrag, setCellDrag] = React.useState(null)
      const timers = React.useRef({ show: 0, hide: 0, last: 0 })
      const rootRef = React.useRef(null)
      const tabsRef = React.useRef(null)
      const [tabsScrollable, setTabsScrollable] = React.useState(false)

      // 关掉面板就把预览和计时器一起清掉。
      React.useEffect(() => {
        if (open) return
        setPreview(null)
        const current = timers.current
        if (current.show) clearTimeout(current.show)
        if (current.hide) clearTimeout(current.hide)
        current.show = 0
        current.hide = 0
      }, [open])

      // 打开时量锚点；窗口变了、或者草稿长高把 ⊞ 顶走了，跟着重量。
      React.useEffect(() => {
        if (!open) return undefined
        const measure = () => {
          const node = bridge.node
          if (!node || typeof node.getBoundingClientRect !== 'function') return
          const rect = node.getBoundingClientRect()
          if (!rect || rect.width <= 0) return
          setAnchor((previous) => {
            if (
              previous &&
              previous.left === rect.left &&
              previous.top === rect.top &&
              previous.right === rect.right &&
              previous.bottom === rect.bottom
            ) {
              return previous
            }
            return { left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom }
          })
        }
        measure()
        const disposers = []
        if (typeof window.addEventListener === 'function') {
          window.addEventListener('resize', measure)
          disposers.push(() => window.removeEventListener('resize', measure))
        }
        // ⊞ 会被宿主布局改动（侧栏开合、草稿长高）挪走，低频跟一下就够了。
        const timer = setInterval(measure, 500)
        disposers.push(() => clearInterval(timer))
        return () => {
          for (const dispose of disposers) {
            try {
              dispose()
            } catch {
              /* 清理失败不影响界面 */
            }
          }
        }
      }, [open])

      // 页签溢出检测：溢出时给左右翻页按钮 + 两端渐隐，否则第 7 页根本看不到。
      React.useEffect(() => {
        if (!open) return undefined
        const measure = () => {
          const node = tabsRef.current
          if (!node) return
          const overflow = node.scrollWidth > node.clientWidth + 1
          setTabsScrollable((previous) => (previous === overflow ? previous : overflow))
        }
        measure()
        const disposers = []
        if (typeof window.ResizeObserver === 'function' && tabsRef.current) {
          try {
            const observer = new window.ResizeObserver(measure)
            observer.observe(tabsRef.current)
            disposers.push(() => observer.disconnect())
          } catch {
            /* 观察不了就靠定时器 */
          }
        }
        const timer = setInterval(measure, 700)
        disposers.push(() => clearInterval(timer))
        return () => {
          for (const dispose of disposers) {
            try {
              dispose()
            } catch {
              /* 忽略 */
            }
          }
        }
      }, [open, sessionId, store.doc.pages.length, store.recentView.get(sessionId)])

      // 当前页签始终滚在可视区内（切页 / 新增页 / 点「最近」之后）。
      React.useEffect(() => {
        if (!open) return
        const node = tabsRef.current
        if (!node) return
        const active = node.querySelector('[data-active="true"]')
        if (!active) return
        const left = active.offsetLeft
        const right = left + active.offsetWidth
        if (left < node.scrollLeft) node.scrollLeft = Math.max(0, left - 6)
        else if (right > node.scrollLeft + node.clientWidth) node.scrollLeft = right - node.clientWidth + 6
      }, [open, sessionId, store.page.get(sessionId), store.recentView.get(sessionId), store.doc.pages.length])

      // 点面板外关闭：面板外 + ⊞ 外才算外（和 DSH 菜单的判定一致）。
      React.useEffect(() => {
        if (!open) return undefined
        const onDown = (event) => {
          const root = rootRef.current
          const target = event.target
          if (root && typeof root.contains === 'function' && root.contains(target)) return
          if (bridge.node && typeof bridge.node.contains === 'function' && bridge.node.contains(target)) return
          closePanel(sessionId)
        }
        document.addEventListener('mousedown', onDown, true)
        return () => document.removeEventListener('mousedown', onDown, true)
      }, [open, sessionId])

      // Esc：只在焦点真的落在面板里时接管，绝不抢输入框的 Esc。
      React.useEffect(() => {
        if (!open) return undefined
        const onKey = (event) => {
          if (event.key !== 'Escape') return
          const root = rootRef.current
          if (!root || !root.contains(document.activeElement)) return
          event.preventDefault()
          event.stopPropagation()
          closePanel(sessionId)
        }
        document.addEventListener('keydown', onKey, true)
        return () => document.removeEventListener('keydown', onKey, true)
      }, [open, sessionId])

      if (!open) return null
      if (anchor === null) return null

      const pages = store.doc.pages
      const pageIndex =
        pages.length === 0 ? 0 : Math.min(Math.max(store.page.get(sessionId) ?? 0, 0), pages.length - 1)
      const page = pages[pageIndex]
      const editing = store.editing.get(sessionId) ?? null
      const editMode = store.editMode.get(sessionId) === true
      const recent = readRecent()
      const showRecent = store.recentView.get(sessionId) === true && recent.length > 0
      const flash = store.flash.get(sessionId) ?? null
      const search = readSearch(sessionId)
      const results = searchPages(pages, search.query) ?? []
      const active = Math.min(Math.max(search.active, 0), Math.max(results.length - 1, 0))

      const insert = (cell) => {
        stopPreview()
        const result = insertIntoDraft(bridge.inputActions, cell.text, bridge.phase)
        if (result.ok === true) {
          pushRecent({ label: cell.label, text: cell.text, page: cell.page })
          setFlash(sessionId, 'ok', t('inserted', { text: toLabel('', cell.text) }))
        } else {
          setFlash(sessionId, 'err', result.reason)
        }
      }

      // —— 悬停预览 ——
      // 450ms 首次、120ms 相邻切换、180ms 离开宽限；预览不接收指针，所以绝不挡鼠标。
      const hoverCapable = (() => {
        try {
          return typeof window.matchMedia === 'function' ? window.matchMedia('(hover: hover)').matches : true
        } catch {
          return true
        }
      })()

      const stopPreview = () => {
        const current = timers.current
        if (current.show) {
          clearTimeout(current.show)
          current.show = 0
        }
        if (current.hide) {
          clearTimeout(current.hide)
          current.hide = 0
        }
      }

      const hoverEnter = (event, cell) => {
        if (!hoverCapable) return
        const node = event && event.currentTarget ? event.currentTarget : null
        if (!node || typeof node.getBoundingClientRect !== 'function') return
        const rect = node.getBoundingClientRect()
        const root = rootRef.current
        const rootRect = root && root.getBoundingClientRect ? root.getBoundingClientRect() : rect
        const current = timers.current
        if (current.hide) {
          clearTimeout(current.hide)
          current.hide = 0
        }
        if (current.show) clearTimeout(current.show)
        const delay = Date.now() - (current.last || 0) < 600 ? 120 : 450
        current.show = setTimeout(() => {
          current.show = 0
          current.last = Date.now()
          setPreview({
            label: cell.label,
            text: cell.text,
            page: cell.page,
            top: rect.top,
            left: rootRect.left,
            right: rootRect.right,
          })
        }, delay)
      }

      const hoverLeave = () => {
        const current = timers.current
        if (current.show) {
          clearTimeout(current.show)
          current.show = 0
        }
        if (current.hide) clearTimeout(current.hide)
        current.hide = setTimeout(() => {
          current.hide = 0
          setPreview(null)
        }, 180)
      }

      // —— 拖拽（只有标题栏是把手） ——
      const onHeadPointerDown = (event) => {
        if (!event || event.button !== 0) return
        const target = event.target
        if (target && typeof target.closest === 'function' && target.closest('input,button,textarea')) return
        const startX = event.clientX
        const startY = event.clientY
        const base = drag || { dx: 0, dy: 0 }
        let latest = base
        let moved = false
        const onMove = (moveEvent) => {
          const dx = moveEvent.clientX - startX
          const dy = moveEvent.clientY - startY
          if (!moved && Math.abs(dx) + Math.abs(dy) < 4) return
          moved = true
          latest = { dx: base.dx + dx, dy: base.dy + dy }
          setDrag(latest)
        }
        const onUp = () => {
          document.removeEventListener('pointermove', onMove)
          document.removeEventListener('pointerup', onUp)
          if (moved) savePos(latest)
        }
        try {
          if (event.currentTarget && typeof event.currentTarget.setPointerCapture === 'function') {
            event.currentTarget.setPointerCapture(event.pointerId)
          }
        } catch {
          /* 捕获失败也能拖 */
        }
        document.addEventListener('pointermove', onMove)
        document.addEventListener('pointerup', onUp)
      }

      const resetPosition = () => {
        savePos(null)
        setDrag(null)
        setPreview(null)
      }

      // —— 编辑态：把格子拖到别的格子（同页重排）或页签（换页） ——
      const dropTargetAt = (x, y) => {
        try {
          const node = document.elementFromPoint(x, y)
          if (!node || typeof node.closest !== 'function') return null
          const cellNode = node.closest('[data-cell]')
          if (cellNode) return { kind: 'cell', index: Number(cellNode.getAttribute('data-cell')) }
          const pageNode = node.closest('[data-page]')
          if (pageNode) return { kind: 'page', index: Number(pageNode.getAttribute('data-page')) }
          return null
        } catch {
          return null
        }
      }

      const beginCellDrag = (event, index) => {
        if (!editMode || showRecent || !event || event.button !== 0) return
        const startX = event.clientX
        const startY = event.clientY
        let active = false
        let over = null
        const onMove = (moveEvent) => {
          const dx = moveEvent.clientX - startX
          const dy = moveEvent.clientY - startY
          if (!active && Math.abs(dx) + Math.abs(dy) < 6) return
          active = true
          over = dropTargetAt(moveEvent.clientX, moveEvent.clientY)
          setCellDrag({ from: index, over })
          setPreview(null)
        }
        const onUp = () => {
          document.removeEventListener('pointermove', onMove)
          document.removeEventListener('pointerup', onUp)
          setCellDrag(null)
          if (active && over) applyMove(index, over)
        }
        document.addEventListener('pointermove', onMove)
        document.addEventListener('pointerup', onUp)
      }

      const applyMove = async (fromIndex, target) => {
        const pagesNext = clonePages()
        const source = pagesNext[pageIndex]
        if (!source) return
        const cell = source.cells[fromIndex]
        if (!cell) return
        const destinationIndex = target.kind === 'page' ? target.index : pageIndex
        const destination = pagesNext[destinationIndex]
        if (!destination) return

        if (destinationIndex === pageIndex) {
          if (target.kind === 'cell' && target.index === fromIndex) return
          const list = source.cells.slice()
          list.splice(fromIndex, 1)
          list.push(null)
          list.splice(target.kind === 'cell' ? target.index : list.length - 1, 0, cell)
          list.length = CELLS_PER_PAGE
          source.cells = list
        } else {
          // 跨页只追加到第一个空格子，避免覆盖目标页的已有内容
          const slot = destination.cells.indexOf(null)
          if (slot < 0) {
            setFlash(sessionId, 'err', t('pageFull'))
            return
          }
          const from = source.cells.slice()
          from[fromIndex] = null
          source.cells = from
          const to = destination.cells.slice()
          to[slot] = cell
          to.length = CELLS_PER_PAGE
          destination.cells = to
        }

        // 防御：移动不该改变格子总数。数量对不上就中止，绝不静默丢内容。
        const countCells = (list) => list.reduce((sum, item) => sum + (item ? 1 : 0), 0)
        const before = pages.reduce((sum, item) => sum + countCells(item.cells), 0)
        const after = pagesNext.reduce((sum, item) => sum + countCells(item.cells), 0)
        if (before !== after) {
          setFlash(sessionId, 'err', t('moveFailed'))
          return
        }

        try {
          await commit(pagesNext)
          setFlash(sessionId, 'ok', t('movedCell'))
        } catch (failure) {
          setFlash(sessionId, 'err', messageOf(failure))
        }
      }

      const openEditor = (index) => {
        store.page.set(sessionId, pageIndex)
        store.editing.set(sessionId, { page: pageIndex, cell: index })
        store.emit()
      }

      const addPage = async () => {
        if (pages.length >= MAX_PAGES) return
        const next = clonePages()
        next.push({
          title: t('pageNumber', { index: pages.length + 1 }),
          cells: new Array(CELLS_PER_PAGE).fill(null),
        })
        try {
          await commit(next)
          store.page.set(sessionId, next.length - 1)
          store.editMode.set(sessionId, true)
          store.editing.set(sessionId, { page: next.length - 1, cell: 0 })
          setFlash(sessionId, 'ok', t('newPageReady'))
        } catch (failure) {
          setFlash(sessionId, 'err', messageOf(failure))
        }
      }

      /** 网格内的方向键：在卡片之间移动焦点（3 列）。 */
      const onGridKey = (event) => {
        const key = event.key
        if (key !== 'ArrowLeft' && key !== 'ArrowRight' && key !== 'ArrowUp' && key !== 'ArrowDown') return
        const buttons = Array.from(event.currentTarget.querySelectorAll('button'))
        const current = buttons.indexOf(document.activeElement)
        if (current < 0) return
        const delta = key === 'ArrowRight' ? 1 : key === 'ArrowLeft' ? -1 : key === 'ArrowDown' ? 3 : -3
        const next = current + delta
        if (next < 0 || next >= buttons.length) return
        event.preventDefault()
        buttons[next].focus()
      }

      const head = h(
        'div',
        { className: 'dsq-head' },
        h(
          'div',
          {
            className: 'dsq-grip',
            title: t('dragHint'),
            'aria-hidden': 'true',
            onPointerDown: onHeadPointerDown,
            onDoubleClick: resetPosition,
          },
          h(
            'svg',
            { width: 10, height: 14, viewBox: '0 0 10 14', fill: 'currentColor', 'aria-hidden': 'true' },
            [0, 1, 2].map((row) =>
              [0, 1].map((column) =>
                h('circle', { key: `${row}-${column}`, cx: 2 + column * 5, cy: 2 + row * 5, r: 1.5 }),
              ),
            ),
          ),
        ),
        h(
          'div',
          { className: 'dsq-searchwrap', style: editMode ? { display: 'none' } : undefined },
          h(
            'svg',
            {
              className: 'dsq-searchicon',
              width: 14,
              height: 14,
              viewBox: '0 0 24 24',
              fill: 'none',
              stroke: 'currentColor',
              strokeWidth: 2.2,
              'aria-hidden': 'true',
            },
            h('circle', { cx: 11, cy: 11, r: 7 }),
            h('path', { d: 'M20 20l-3.5-3.5' }),
          ),
          h('input', {
          className: 'dsq-search',
          type: 'search',
          value: search.query,
          placeholder: t('searchPlaceholder'),
          'aria-label': t('searchPlaceholder'),
          onChange: (event) => {
            setPreview(null)
            writeSearch(sessionId, { query: event.target.value, active: 0 })
            store.emit()
          },
          onKeyDown: (event) => {
            if (event.key === 'ArrowDown') {
              event.preventDefault()
              writeSearch(sessionId, { active: Math.min(active + 1, Math.max(results.length - 1, 0)) })
              store.emit()
            } else if (event.key === 'ArrowUp') {
              event.preventDefault()
              writeSearch(sessionId, { active: Math.max(active - 1, 0) })
              store.emit()
            } else if (event.key === 'Enter') {
              event.preventDefault()
              const hit = results[active]
              if (hit) insert(hit)
            } else if (event.key === 'Escape') {
              event.preventDefault()
              if (search.query !== '') {
                writeSearch(sessionId, { query: '', active: 0 })
                store.emit()
              } else {
                closePanel(sessionId)
              }
            }
          },
        }),
        ),
        editMode
          ? h(
              'div',
              { className: 'dsq-editbar', role: 'status' },
              h(PencilIcon, null),
              h('span', { className: 'dsq-editbar-text', title: t('editBarHint') }, t('editBarHint')),
            )
          : null,
        h(
          'button',
          {
            type: 'button',
            className: 'dsq-x',
            title: t('collapse'),
            'aria-label': t('collapse'),
            onMouseDown: keepFocus,
            onClick: () => closePanel(sessionId),
          },
          h(CloseIcon, null),
        ),
      )

      const tabs = h(
        'div',
        {
          ref: tabsRef,
          className: tabsScrollable ? 'dsq-tabs dsq-tabs-scroll' : 'dsq-tabs',
          role: 'tablist',
        },
        recent.length > 0
          ? h(
              'button',
              {
                key: 'tab-recent',
                type: 'button',
                role: 'tab',
                'aria-selected': showRecent ? 'true' : 'false',
                'data-active': showRecent ? 'true' : 'false',
                className: showRecent ? 'dsq-tab dsq-tab-on' : 'dsq-tab',
                title: t('recentHint'),
                onMouseDown: keepFocus,
                onClick: () => {
                  store.recentView.set(sessionId, true)
                  store.editMode.set(sessionId, false)
                  store.editing.set(sessionId, null)
                  store.emit()
                },
              },
              t('recentTab'),
            )
          : null,
        pages.map((item, index) =>
          h(
            'button',
            {
              key: `tab-${index}`,
              type: 'button',
              role: 'tab',
              'aria-selected': !showRecent && index === pageIndex ? 'true' : 'false',
              'data-active': !showRecent && index === pageIndex ? 'true' : 'false',
              'data-page': index,
              className:
                (!showRecent && index === pageIndex ? 'dsq-tab dsq-tab-on' : 'dsq-tab') +
                (cellDrag && cellDrag.over && cellDrag.over.kind === 'page' && cellDrag.over.index === index
                  ? ' dsq-tab-over'
                  : ''),
              title: t('pageHint', { title: item.title, index: index + 1, total: Math.max(pages.length, 1) }),
              onMouseDown: keepFocus,
              onKeyDown: (event) => {
                if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return
                const step = event.key === 'ArrowRight' ? 1 : -1
                const next = Math.min(Math.max(index + step, 0), pages.length - 1)
                if (next === index) return
                event.preventDefault()
                store.recentView.set(sessionId, false)
                store.page.set(sessionId, next)
                store.editing.set(sessionId, null)
                store.emit()
              },
              onClick: () => {
                store.recentView.set(sessionId, false)
                store.page.set(sessionId, index)
                store.editing.set(sessionId, null)
                store.emit()
              },
            },
            item.title,
          ),
        ),
      )

      const grid =
        page === undefined
          ? null
          : h(
              'div',
              { className: 'dsq-grid3', role: 'group', 'aria-label': t('panelAria'), onKeyDown: onGridKey },
              page.cells.map((cell, index) => {
                if (!cell) {
                  return editMode
                    ? h(
                        'button',
                        {
                          key: `c-${index}`,
                          type: 'button',
                          'data-cell': index,
                          className:
                            'dsq-card dsq-card-empty' +
                            (cellDrag && cellDrag.over && cellDrag.over.kind === 'cell' && cellDrag.over.index === index
                              ? ' dsq-card-over'
                              : ''),
                          title: t('emptyCell'),
                          onMouseDown: keepFocus,
                          onClick: () => openEditor(index),
                        },
                        '＋',
                      )
                    : null
                }
                return h(
                  'button',
                  {
                    key: `c-${index}`,
                    type: 'button',
                    'data-cell': index,
                    className:
                      'dsq-card' +
                      (cellDrag && cellDrag.from === index ? ' dsq-card-drag' : '') +
                      (cellDrag && cellDrag.over && cellDrag.over.kind === 'cell' && cellDrag.over.index === index
                        ? ' dsq-card-over'
                        : ''),
                    title: cell.text,
                    onMouseDown: keepFocus,
                    onPointerDown: (event) => beginCellDrag(event, index),
                    onMouseEnter: (event) =>
                      hoverEnter(event, {
                        label: cell.label,
                        text: cell.text,
                        page: page ? page.title : '',
                      }),
                    onMouseLeave: hoverLeave,
                    onClick: () =>
                      editMode
                        ? openEditor(index)
                        : insert({ label: cell.label, text: cell.text, page: page ? page.title : '' }),
                    onContextMenu: (event) => {
                      if (event && typeof event.preventDefault === 'function') event.preventDefault()
                      openEditor(index)
                    },
                  },
                  h('span', { className: 'dsq-card-label' }, cell.label),
                  editMode ? h('span', { className: 'dsq-card-sub' }, t('editCellShort')) : null,
                )
              }),
            )

      const recentGrid =
        recent.length === 0
          ? null
          : h(
              'div',
              { className: 'dsq-grid3', role: 'group', 'aria-label': t('recentTab') },
              recent.map((item, index) =>
                h(
                  'button',
                  {
                    key: `recent-${index}-${item.text.length}`,
                    type: 'button',
                    className: 'dsq-card',
                    title: item.text,
                    onMouseDown: keepFocus,
                    onMouseEnter: (event) => hoverEnter(event, item),
                    onMouseLeave: hoverLeave,
                    onClick: () => insert(item),
                  },
                  h('span', { className: 'dsq-card-label' }, item.label || toLabel('', item.text)),
                  h('span', { className: 'dsq-card-sub' }, item.page || ''),
                ),
              ),
            )

      const list = h(
        'div',
        { className: 'dsq-results', role: 'listbox', 'aria-label': t('searchPlaceholder') },
        results.length === 0
          ? h('div', { className: 'dsq-muted', style: { padding: '10px 8px' } }, t('noResults', { q: search.query }))
          : results.map((item, index) =>
              h(
                'button',
                {
                  key: `r-${item.pageIndex}-${item.cellIndex}`,
                  type: 'button',
                  role: 'option',
                  'aria-selected': index === active ? 'true' : 'false',
                  className: index === active ? 'dsq-item dsq-item-on' : 'dsq-item',
                  title: item.text,
                  onMouseDown: keepFocus,
                  onClick: () => insert(item),
                  onMouseEnter: () => {
                    if (index === active) return
                    writeSearch(sessionId, { active: index })
                    store.emit()
                  },
                },
                h('span', { className: 'dsq-item-label' }, item.label),
                h('span', { className: 'dsq-item-snippet' }, snippet(item.text)),
                h('span', { className: 'dsq-item-page' }, item.page),
              ),
            ),
      )

      let body = null
      if (store.doc.status === 'loading' && pages.length === 0) {
        body = h('div', { className: 'dsq-muted', style: { padding: '12px 8px' } }, t('loading'))
      } else if (store.doc.status === 'error' && pages.length === 0) {
        body = h(
          'div',
          { style: { display: 'flex', flexDirection: 'column', gap: 6, padding: '6px 4px' } },
          h('div', { className: 'dsq-err' }, t('readFailed', { message: store.doc.error })),
          h(
            'button',
            { type: 'button', className: 'dsq-action', onMouseDown: keepFocus, onClick: () => ensureDoc(true) },
            t('retry'),
          ),
        )
      } else if (editing !== null) {
        body = h(
          React.Fragment,
          null,
          h(PageRow, { key: `page-${pageIndex}`, sessionId, page: pageIndex, t }),
          h(CellEditor, {
            key: `cell-${pageIndex}-${editing.cell}`,
            sessionId,
            page: pageIndex,
            cell: editing.cell,
            t,
          }),
        )
      } else if (search.query !== '') {
        body = list
      } else if (showRecent) {
        body = recentGrid
      } else if (page && page.cells.every((cell) => !cell) && !editMode) {
        body = h(
          'div',
          { className: 'dsq-empty' },
          h('div', { className: 'dsq-empty-title' }, t('emptyPageTitle')),
          h('div', null, t('emptyPageHint')),
        )
      } else {
        body = grid
      }

      // 页签放在最后一行：气泡底部锚定，换页时这一行不会上下移动。
      const nudgeTabs = (direction) => {
        const node = tabsRef.current
        if (!node) return
        node.scrollLeft += direction * Math.max(80, Math.round(node.clientWidth * 0.6))
      }

      const tabsRow = h(
        'div',
        { className: 'dsq-tabsrow' },
        tabsScrollable
          ? h(
              'button',
              {
                type: 'button',
                className: 'dsq-mini',
                title: t('tabsPrev'),
                'aria-label': t('tabsPrev'),
                onMouseDown: keepFocus,
                onClick: () => nudgeTabs(-1),
              },
              '‹',
            )
          : null,
        tabs,
        tabsScrollable
          ? h(
              'button',
              {
                type: 'button',
                className: 'dsq-mini',
                title: t('tabsNext'),
                'aria-label': t('tabsNext'),
                onMouseDown: keepFocus,
                onClick: () => nudgeTabs(1),
              },
              '›',
            )
          : null,
        h(
          'span',
          {
            className: 'dsq-count',
            title: flash
              ? flash.text
              : t('pageHint', {
                  title: page ? page.title : '',
                  index: pageIndex + 1,
                  total: Math.max(pages.length, 1),
                }),
          },
          flash
            ? h('span', { className: flash.kind === 'ok' ? 'dsq-ok' : 'dsq-err' }, flash.text)
            : `${pageIndex + 1}/${Math.max(pages.length, 1)}`,
        ),
        editMode && pages.length < MAX_PAGES
          ? h(
              'button',
              {
                type: 'button',
                className: 'dsq-mini',
                title: t('addPage'),
                onMouseDown: keepFocus,
                onClick: addPage,
              },
              '＋',
            )
          : null,
        h(
          'button',
          {
            type: 'button',
            className: editMode ? 'dsq-mini dsq-mini-on' : 'dsq-mini',
            title: editMode ? t('finishEdit') : t('editPresets'),
            onMouseDown: keepFocus,
            onClick: () => {
              if (pages.length === 0) return
              store.editing.set(sessionId, null)
              store.editMode.set(sessionId, editMode !== true)
              if (editMode !== true) writeSearch(sessionId, { query: '', active: 0 })
              store.emit()
            },
          },
          editMode ? h(CheckIcon, null) : h(PencilIcon, null),
        ),
      )

      let previewNode = null
      if (preview !== null) {
        const vw = window.innerWidth || 1280
        const vh = window.innerHeight || 800
        const width = 300
        const gap = 10
        let left = preview.right + gap
        if (left + width > vw - VIEWPORT_MARGIN) left = preview.left - gap - width
        left = Math.max(VIEWPORT_MARGIN, Math.min(left, vw - width - VIEWPORT_MARGIN))
        const top = Math.max(VIEWPORT_MARGIN, Math.min(preview.top, vh - 240))
        const raw = String(preview.text || '')
        previewNode = h(
          'div',
          { className: 'dsq-preview', style: { left: left, top: top, width: width }, 'aria-hidden': 'true' },
          h('div', { className: 'dsq-preview-title' }, preview.label),
          h('div', { className: 'dsq-preview-meta' }, t('previewMeta', { page: preview.page, n: raw.length })),
          h('div', { className: 'dsq-preview-text' }, raw.length > 360 ? `${raw.slice(0, 360)}…` : raw),
          h('div', { className: 'dsq-preview-foot' }, t('previewHint')),
        )
      }

      return h(
        React.Fragment,
        null,
        h('style', null, CSS),
        h(
          'div',
          {
            ref: rootRef,
            className: 'dsq-pop',
            style: popoverStyle(anchor, drag),
            role: 'dialog',
            'aria-modal': 'false',
            'aria-label': t('panelAria'),
          },
          head,
          h('div', { className: editing !== null ? 'dsq-body dsq-body-auto' : 'dsq-body' }, body),
          tabsRow,
        ),
        previewNode,
      )
    }

    // ------------------------------------------------------------ 兜底

    /** 组件崩了就藏起来，绝不让整个槽位变空白。 */
    class Boundary extends React.Component {
      constructor(props) {
        super(props)
        this.state = { failed: false }
      }
      static getDerivedStateFromError() {
        return { failed: true }
      }
      componentDidCatch(error) {
        try {
          console.error('[quick-input] 界面渲染失败：', error)
        } catch {
          /* 忽略 */
        }
      }
      render() {
        return this.state.failed ? null : this.props.children
      }
    }

    function GuardedToggle(props) {
      return h(Boundary, null, h(QuickToggle, props))
    }

    function GuardedPanel(props) {
      return h(Boundary, null, h(QuickPanel, props))
    }

    // ------------------------------------------------------------ 插件对象

    /** 向宿主报到：这样 `GET /quick-input/health` 能证明页面正在跑哪一份客户端代码。 */
    function announceBuild() {
      postHello({ version: CLIENT_BUILD })
    }

    /**
     * 把版面实测数字回报给宿主（只在数据变化时发一次）。
     * 面板在真实页面里落在哪、为什么降级，靠这个在 `/quick-input/health` 里读出来。
     */
    let lastLayoutKey = ''
    function reportLayout(layout) {
      const key = JSON.stringify(layout)
      if (key === lastLayoutKey) return
      lastLayoutKey = key
      postHello({ version: CLIENT_BUILD, layout })
    }

    function postHello(payload) {
      try {
        const call = fetch(`${API}/hello`, {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify(payload),
        })
        if (call && typeof call.catch === 'function') call.catch(() => {})
      } catch {
        /* 报到失败不影响界面 */
      }
    }

    return {
      // locale 是客户端核心服务：注册中英字典、并把命名空间交给槽位（组件因此拿到 t）。
      inject: ['slots', 'locale'],
      apply(ctx) {
        const locale = ctx.locale
        if (locale && typeof locale.register === 'function') {
          ctx.effect(() => locale.register(NS, DICT))
          if (typeof locale.bind === 'function') boundT = locale.bind(NS)
          const sync = () => {
            try {
              const snapshot =
                typeof locale.getSnapshot === 'function' ? locale.getSnapshot() : locale.getLocale()
              if (snapshot && typeof snapshot.active === 'string' && snapshot.active !== '') {
                if (snapshot.active !== activeLocaleId) {
                  activeLocaleId = snapshot.active
                  // 语言变了：让已经挂着的面板/按钮立刻用新语言重渲染一次。
                  store.emit()
                }
              }
            } catch {
              /* 拿不到语言就保持默认（中文兜底） */
            }
          }
          sync()
          if (typeof locale.subscribe === 'function') ctx.effect(() => locale.subscribe(sync))
        }
        ctx.slots.inject(TOGGLE_SLOT, () =>
          ctx.slots.register({ name: TOGGLE_SLOT, id: 'quick-input-toggle', order: 4, locale: NS }, GuardedToggle),
        )
        ctx.slots.inject(PANEL_SLOT, () =>
          ctx.slots.register({ name: PANEL_SLOT, id: 'quick-input-panel', order: 20, locale: NS }, GuardedPanel),
        )
        // 全局快捷键（可选服务）：Ctrl/Cmd+Shift+K 开合面板。
        // 用 ctx.inject 而不是 inject 数组，profile 里没有 shortcuts 时插件照常工作。
        try {
          if (typeof ctx.inject === 'function') {
            ctx.inject(['shortcuts'], (scoped) => {
              scoped.effect(() => {
                const shortcuts = scoped.shortcuts
                if (!shortcuts || typeof shortcuts.register !== 'function') return () => {}
                try {
                  return shortcuts.register({
                  id: 'quick-input.toggle',
                  label: () => tr('shortcutToggle'),
                  aliases: ['quick input', 'quick phrases', 'prompt pad', '快捷输入'],
                  defaults: {
                    'desktop:macos': { code: 'KeyK', modifiers: ['primary', 'shift'] },
                    'desktop:windows': { code: 'KeyK', modifiers: ['primary', 'shift'] },
                    'desktop:linux': { code: 'KeyK', modifiers: ['primary', 'shift'] },
                    'web:macos': { code: 'KeyK', modifiers: ['primary', 'alt'] },
                    'web:windows': { code: 'KeyK', modifiers: ['primary', 'alt'] },
                    'web:linux': { code: 'KeyK', modifiers: ['primary', 'alt'] },
                  },
                  regions: ['page', 'editable'],
                  modals: [],
                  resolve: ({ modal }) => {
                    if (modal !== null && modal !== undefined) return { status: 'pass' }
                    const session = bridge.sessionId
                    if (session === null || session === undefined) return { status: 'pass' }
                    return {
                      status: 'handled',
                      run: () => {
                        const next = !isOpen(session)
                        store.open.set(session, next)
                        if (next) ensureDoc(false)
                        store.emit()
                      },
                    }
                  },
                  })
                } catch (error) {
                  // 键位与别的命令冲突时 register 会抛错；快捷键没了不影响面板本身。
                  console.warn('[quick-input] 快捷键注册失败：', error)
                  return () => {}
                }
              }, 'quick-input: shortcut')
            })
          }
        } catch {
          /* 没有快捷键服务就跳过，不影响面板 */
        }
        announceBuild()
      },
    }
  },
})

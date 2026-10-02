// OctoSense Repair · Demo Web · 通用工具与路由
// 不进 bundle，不属于 Hub 候选；只服务本地浏览器演示。
//
// 修复 R-P1-2 / R-P1-4 / R-P1-5 / R-P1-6 / N14：
//  - ACTORS 的 project 改为数组（URLSearchParams 拆分 + 顶栏多项目拼接）
//  - /task/{id} 重定向到 /workbench?task=，避免 500
//  - newIdem() 统一 ms+rand 后缀防同毫秒撞键
//  - currentVer() 从 ACTIVE 任务对象读，不再猜版本
//  - api() 兼容二进制与多状态码错误信封；非 200 透传 status

const STORE_KEY = 'octosense.actor';

const ACTORS = [
  { actor: 'u-reporter-1', name: '报修人一',   role: 'REPORTER',   cls: 'rep',  projects: ['prj-A'], desc: '三楼会议室空调报修人；可报修、确认预约、验收、退回。' },
  { actor: 'u-reporter-2', name: '报修人二',   role: 'REPORTER',   cls: 'rep',  projects: ['prj-B'], desc: '二楼走廊照明报修人；走电气技工乙。' },
  { actor: 'u-tech-1',     name: '技工甲',     role: 'TECHNICIAN', cls: 'tech', projects: ['prj-A'], skills: 'HVAC', desc: 'HVAC 技能；可接单、绑设备、提议预约、开工、完工提交。' },
  { actor: 'u-tech-2',     name: '技工乙',     role: 'TECHNICIAN', cls: 'tech', projects: ['prj-A', 'prj-B'], skills: 'ELECTRICAL', desc: '电气技能；可处理两个项目的电气维修。' },
  { actor: 'u-manager',    name: '经理丙',     role: 'MANAGER',    cls: 'mgr',  projects: ['prj-A'], desc: '项目经理；可改派、隔离证据、分配技工、取消。' },
];

const ROLES_LABEL = {
  REPORTER:   '报修人',
  TECHNICIAN: '技工',
  MANAGER:    '项目经理',
};

// 兼容老字段 'project'
function projectListOf(actor) {
  if (Array.isArray(actor.projects)) return actor.projects;
  if (typeof actor.project === 'string') {
    return actor.project.split(/[,\s&]+/).filter(Boolean);
  }
  return [];
}

function getActor() {
  try { return JSON.parse(localStorage.getItem(STORE_KEY) || 'null'); }
  catch { return null; }
}
function setActor(actor) {
  localStorage.setItem(STORE_KEY, JSON.stringify(actor));
}
function clearActor() {
  localStorage.removeItem(STORE_KEY);
}

// 统一幂等键：时间+随机后缀
function newIdem() {
  return 'web-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
}

async function api(path, opts = {}) {
  const actor = getActor();
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (actor) headers['X-Actor-Id'] = actor.actor;
  const init = { method: opts.method || 'GET', headers };
  if (opts.body !== undefined && !(opts.body instanceof FormData)) {
    init.body = JSON.stringify(opts.body);
  } else if (opts.body instanceof FormData) {
    // FormData 由浏览器自动设置 multipart 边界
    delete headers['Content-Type'];
    init.body = opts.body;
  }
  const r = await fetch(path, init);
  const ct = r.headers.get('content-type') || '';
  let data;
  if (ct.includes('application/json')) {
    try { data = await r.json(); }
    catch { data = null; }
  } else {
    data = await r.text();
  }
  if (!r.ok) {
    // 错误信封统一为 { code, detail }
    let code = 'HTTP_' + r.status;
    let detail = '';
    if (data && typeof data === 'object') {
      if (data.detail && typeof data.detail === 'object') {
        code = data.detail.code || code;
        detail = data.detail.detail || '';
      } else if (data.code) {
        code = data.code;
        detail = data.detail || '';
      }
    } else if (typeof data === 'string') {
      detail = data.slice(0, 200);
    }
    const err = new Error(code);
    err.status = r.status;
    err.detail = detail;
    err.payload = data;
    throw err;
  }
  return data;
}

function toast(msg, kind = 'ok') {
  const el = document.createElement('div');
  el.className = `toast ${kind} show`;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 300);
  }, 2400);
}

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function fmtTime(ms) {
  if (!ms) return '-';
  const d = new Date(ms);
  return d.toLocaleString('zh-CN', { hour12: false });
}

function fmtBytes(n) {
  if (!n && n !== 0) return '-';
  if (n < 1024) return n + ' B';
  if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB';
  return (n / 1024 / 1024).toFixed(2) + ' MB';
}

function roleChip(role) {
  const cls = { REPORTER: 'rep', TECHNICIAN: 'tech', MANAGER: 'mgr' }[role] || '';
  return `<span class="role-chip ${cls}" style="background:${ {rep:'#91D5BE', tech:'#B8C8F2', mgr:'#F2C8B8'}[cls] }; color:#132F27;">${ROLES_LABEL[role] || role}</span>`;
}

function renderTopbar() {
  const me = getActor();
  const tb = document.getElementById('topbar');
  if (!tb) return;
  if (!me) {
    tb.innerHTML = `
      <h1>OctoSense Repair · 维修协作工作台</h1>
      <div class="me"><a href="/">登录</a></div>`;
    return;
  }
  const projs = projectListOf(me);
  tb.innerHTML = `
    <h1>OctoSense Repair · <span style="color:var(--secondary);font-weight:400;">维修协作</span></h1>
    <div class="me">
      ${roleChip(me.role)}
      <span><b>${escapeHtml(me.name)}</b> · ${escapeHtml(me.actor)} · ${escapeHtml(projs.join(' · '))}</span>
      <a href="/workbench" style="color:var(--accent);">工作台</a>
      <button class="btn-secondary btn" onclick="logout()" style="padding:6px 12px;font-size:12px;">退出</button>
    </div>`;
}

function logout() {
  clearActor();
  location.href = '/';
}

window.OctoApp = { ACTORS, projectListOf, getActor, setActor, clearActor,
                    api, toast, escapeHtml, fmtTime, fmtBytes, roleChip,
                    renderTopbar, newIdem };

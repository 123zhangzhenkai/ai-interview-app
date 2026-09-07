/* =====================================================
   offerAI 智能面试官 · 前端逻辑（原生 JS）
   对接后端 http://127.0.0.1:8000/api/v1
   -----------------------------------------------------
   说明：
   - 登录/注册走后端 /auth，账号为手机号
   - AI 面试：后端暂未提供"面试官"专用接口，前端用
     /ai/chat（DeepSeek）+ 面试官 system 人设 + 完整上下文
     连续调用实现"AI 提问 -> 我回答 -> AI 追问/点评"
   - 面试记录（完整消息）保存在浏览器 localStorage
   ===================================================== */

const API_BASE = 'http://127.0.0.1:8000/api/v1';

/* ---------- 工具 ---------- */
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

const TOKEN_KEY = 'offerai_token';
const PHONE_KEY = 'offerai_phone';
const STORE_KEY = 'offerai_sessions';

const getToken = () => localStorage.getItem(TOKEN_KEY);
function setAuth(token, phone) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(PHONE_KEY, phone);
}
const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(PHONE_KEY);
};

function flash(text) {
  const el = $('#auth-err');
  if (el) { el.textContent = text; setTimeout(() => { if (el.textContent === text) el.textContent = ''; }, 5000); }
}

/* ---------- 请求封装（统一 { code, message, data }） ---------- */
async function request(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = 'Bearer ' + token;

  let resp;
  try {
    resp = await fetch(API_BASE + path, { method, headers, body: body ? JSON.stringify(body) : undefined });
  } catch (e) {
    throw new Error('无法连接后端 ' + API_BASE + '，请确认服务已启动');
  }
  let data = null;
  try { data = await resp.json(); } catch (e) { /* 忽略非 JSON */ }

  if (!resp.ok) {
    const msg = (data && data.message) ? data.message : ('HTTP ' + resp.status);
    if (resp.status === 401) { clearAuth(); location.reload(); }
    throw new Error(msg);
  }
  if (data && data.code !== 0) throw new Error(data.message || '业务处理失败');
  return data ? data.data : null;
}

/* =====================================================
   状态与本地持久化
   ===================================================== */
let authMode = 'login';   // login | register
let sessions = [];        // [{ id, job, time, done, messages:[{role,content}] }]
let activeId = null;      // 当前打开会话 id
let busy = false;

function currentSession() { return sessions.find((s) => s.id === activeId) || null; }

function loadStore() { try { sessions = JSON.parse(localStorage.getItem(STORE_KEY)) || []; } catch (e) { sessions = []; } }
function saveStore() { localStorage.setItem(STORE_KEY, JSON.stringify(sessions)); }
function normalizeSession() {
  if (!sessions.length) return;
  sessions.forEach((s) => {
    if (typeof s.messages === 'undefined') s.messages = [];
    if (typeof s.done === 'undefined') s.done = false;
  });
  saveStore();
}

/* =====================================================
   视图切换
   ===================================================== */
function showLogin() { $('#view-login').hidden = false; $('#view-app').hidden = true; }
function showApp() {
  $('#view-login').hidden = true;
  $('#view-app').hidden = false;
  $('#cur-phone').textContent = localStorage.getItem(PHONE_KEY) || '';
  loadStore();
  normalizeSession();
  renderHistory();
  showStartView();
  // 复位到「模拟面试」视图
  if (typeof profileView !== 'undefined') {
    profileView.hidden = true;
    navBtns.forEach((b) => b.classList.toggle('active', b.dataset.view === 'interview'));
  }
}

/* ---------- 登录 / 注册 ---------- */
function setAuthMode(mode) {
  authMode = mode;
  $('#tab-login').classList.toggle('active', mode === 'login');
  $('#tab-reg').classList.toggle('active', mode === 'register');
  $('#pwd2-row').hidden = mode !== 'register';
  $('#reg-tip').hidden = mode !== 'register';
  $('#auth-submit').textContent = mode === 'login' ? '登 录' : '注 册';
  flash('');
}
$('#tab-login').addEventListener('click', () => setAuthMode('login'));
$('#tab-reg').addEventListener('click', () => setAuthMode('register'));

$('#auth-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const phone = $('#f-phone').value.trim();
  const pwd = $('#f-pwd').value;
  if (!/^1\d{10}$/.test(phone)) return flash('请输入正确的 11 位手机号');
  if (pwd.length < 6) return flash('密码至少 6 位');

  const btn = $('#auth-submit');
  btn.disabled = true;
  try {
    if (authMode === 'login') {
      const data = await request('/auth/login', { method: 'POST', body: { phone, password: pwd } });
      setAuth(data.access_token, phone);
      showApp();
    } else {
      const pwd2 = $('#f-pwd2').value;
      if (pwd2 !== pwd) return flash('两次输入的密码不一致');
      // 验证码后端未接入短信服务，此处传占位值
      const data = await request('/auth/register', {
        method: 'POST', body: { phone, password: pwd, code: '000000' }
      });
      setAuth(data.access_token, phone);
      showApp();
    }
  } catch (err) {
    flash(err.message);
  } finally {
    btn.disabled = false;
  }
});

$('#btn-logout').addEventListener('click', () => { clearAuth(); showLogin(); });

/* =====================================================
   主视图（开始面试 / 聊天）
   ===================================================== */
const startView = $('#start-view');
const chatView = $('#chat-view');
const chatBody = $('#chat-body');
const answerInput = $('#answer-input');

function showStartView() {
  activeId = null;
  busy = false;
  startView.hidden = false;
  chatView.hidden = true;
  renderHistory();
}

function chatViewSetup(session) {
  $('#chat-job').textContent = session.job + ' · AI 面试官';
  $('#chat-status').textContent = session.done ? '已结束' : '模拟面试中';
  const endBtn = $('#btn-end');
  endBtn.textContent = session.done ? '已结束' : '结束面试';
  endBtn.disabled = session.done;
  answerInput.disabled = session.done;
  answerInput.placeholder = session.done ? '本场面试已结束，可新建面试' : '输入你的回答，Enter 发送';
  if (!session.done) answerInput.focus();
}

/* 推荐岗位点选 */
$$('#job-chips .chip').forEach((chip) => {
  chip.addEventListener('click', () => { $('#job-input').value = chip.textContent; });
});

/* 打开一场面试（进入聊天视图） */
function openSession(id) {
  const s = sessions.find((x) => x.id === id);
  if (!s) return;
  activeId = id;
  startView.hidden = true;
  chatView.hidden = false;
  chatViewSetup(s);
  renderMessages();
  renderHistory();
}

/* ---------- 开始面试 ---------- */
$('#btn-start').addEventListener('click', () => {
  const job = $('#job-input').value.trim();
  if (!job) { alert('请先输入目标岗位'); return; }

  const s = {
    id: 's' + Date.now(),
    job,
    time: Date.now(),
    done: false,
    messages: []
  };
  sessions.unshift(s);
  saveStore();

  // 本地开场白（后续追问与点评由 DeepSeek 生成）
  s.messages.push({ role: 'assistant', content: `你好，我是本次【${job}】岗位的面试官。${job}岗主要考察专业技能、项目经验与问题解决能力。请先做个自我介绍吧。` });
  saveStore();

  openSession(s.id);
  $('#job-input').value = '';
});

/* ---------- AI 面试官人设（每轮请求都会带上） ---------- */
function buildSystemPrompt(session) {
  return `你是资深 HR 面试官，正在为【${session.job}】岗位进行模拟面试。
规则：
1. 用中文交流，语气专业、亲切、适度鼓励。
2. 你只能扮演面试官，不要替我回答。
3. 每次只提一个问题，根据我的回答做简短点评后再问下一个，必要时追问细节、让其举例。
4. 问题围绕该岗位由浅入深：自我介绍、项目经验、专业技能、场景题、职业规划。
5. 只有当我明确说"结束面试"时，才输出整体总结：分维度评分（专业能力/表达沟通/逻辑思维/岗位匹配，满分10）+ 3条改进建议 + 鼓励。在那之前绝不提前总结。`;
}

/* ---------- 发送回答 ---------- */
async function sendAnswer() {
  const session = currentSession();
  if (busy || !session || session.done) return;
  const text = answerInput.value.trim();
  if (!text) return;

  answerInput.value = '';
  addMessage('user', text);
  setBusy(true);
  const typingEl = showTyping();

  try {
    const msgs = session.messages.map((m) => ({ role: m.role, content: m.content }));
    const data = await request('/ai/chat', {
      method: 'POST',
      body: {
        temperature: 0.7,
        messages: [{ role: 'system', content: buildSystemPrompt(session) }, ...msgs]
      }
    });
    typingEl.remove();
    addMessage('assistant', (data && data.content) ? data.content : '(AI 未返回内容)');
  } catch (err) {
    typingEl.remove();
    addMessage('assistant', '⚠️ ' + err.message);
  } finally {
    setBusy(false);
  }
}

/* ---------- 结束面试并总结 ---------- */
async function endInterview() {
  const session = currentSession();
  if (busy || !session || session.done) return;
  if (!confirm('确定结束本场面试，并让 AI 输出整体点评吗？')) return;

  setBusy(true);
  const typingEl = showTyping();
  try {
    const msgs = session.messages.map((m) => ({ role: m.role, content: m.content }));
    const data = await request('/ai/chat', {
      method: 'POST',
      body: {
        temperature: 0.4,
        messages: [
          { role: 'system', content: `你是刚才【${session.job}】岗位面试的面试官。现在面试已结束，请用中文输出正式总结，包含：1) 整体评价；2) 分维度评分（专业能力/表达沟通/逻辑思维/岗位匹配，各满分 10 分）；3) 3 条最重要的改进建议；4) 对候选人的鼓励。` },
          ...msgs
        ]
      }
    });
    typingEl.remove();
    session.done = true;
    saveStore();
    addMessage('assistant', (data && data.content) ? data.content : '(AI 未返回内容)');
  } catch (err) {
    typingEl.remove();
    addMessage('assistant', '⚠️ ' + err.message);
  } finally {
    chatViewSetup(session);
    setBusy(false);
  }
}

/* =====================================================
   消息渲染
   ===================================================== */
function addMessage(role, content) {
  const s = currentSession();
  if (s) { s.messages.push({ role, content }); saveStore(); }
  const el = document.createElement('div');
  el.className = 'msg ' + (role === 'user' ? 'user' : 'ai');
  el.innerHTML = (role === 'user' ? '' : '<span class="avatar">AI</span>')
    + '<div class="bubble">' + esc(content) + '</div>';
  chatBody.appendChild(el);
  scrollBottom();
}

function showTyping() {
  const el = document.createElement('div');
  el.className = 'msg ai';
  el.innerHTML = '<span class="avatar">AI</span><div class="bubble typing"><i></i><i></i><i></i></div>';
  chatBody.appendChild(el);
  scrollBottom();
  return el;
}

function renderMessages() {
  chatBody.innerHTML = '';
  const s = currentSession();
  if (!s) return;
  s.messages.forEach((m) => {
    const el = document.createElement('div');
    el.className = 'msg ' + (m.role === 'user' ? 'user' : 'ai');
    el.innerHTML = (m.role === 'user' ? '' : '<span class="avatar">AI</span>')
      + '<div class="bubble">' + esc(m.content) + '</div>';
    chatBody.appendChild(el);
  });
  scrollBottom();
}

function scrollBottom() { chatBody.scrollTop = chatBody.scrollHeight; }

function setBusy(v) {
  busy = v;
  const s = currentSession();
  answerInput.disabled = !!v || (!!s && s.done);
  $('#btn-end').disabled = !!v || (!!s && s.done);
  if (!v && !answerInput.disabled) answerInput.focus();
}

/* ---------- 历史列表 ---------- */
function fmtTime(t) {
  const d = new Date(t);
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getMonth() + 1}月${d.getDate()}日 ${p(d.getHours())}:${p(d.getMinutes())}`;
}

function renderHistory() {
  const ul = $('#history-list');
  ul.innerHTML = '';
  if (!sessions.length) {
    ul.innerHTML = '<li class="empty-history">还没有面试记录<br />先开启你的第一场面试吧</li>';
    return;
  }
  sessions.forEach((s) => {
    const li = document.createElement('li');
    li.className = 'history-item' + (s.id === activeId ? ' active' : '');
    li.innerHTML = `
      <span class="h-count">${s.messages.length} 条</span>
      <div class="h-title">${esc(s.job)}${s.done ? '<span class="h-done">已结束</span>' : ''}</div>
      <div class="h-meta">${fmtTime(s.time)}</div>`;
    li.addEventListener('click', () => { if (!busy) openSession(s.id); });
    ul.appendChild(li);
  });
}

/* =====================================================
   求职信息登记模块
   ===================================================== */
const DRAFT_KEY = 'offerai_resume_draft';
const profileView = $('#profile-view');
const profileMsg = $('#profile-msg');
let profileLoaded = false; // 是否已从后端拉取过当前档案

function showProfileMsg(text, type) {
  profileMsg.textContent = text || '';
  profileMsg.className = 'pf-tip-msg' + (type === 'ok' ? ' ok' : (type === 'err' ? ' err' : ''));
}

/* ---------- 顶部导航：面试 / 求职信息登记 ---------- */
const navBtns = $$('#topnav .topnav-item');
function switchView(view) {
  navBtns.forEach((b) => b.classList.toggle('active', b.dataset.view === view));
  if (view === 'profile') {
    startView.hidden = true;
    chatView.hidden = true;
    profileView.hidden = false;
    if (!profileLoaded) loadProfileFromServer();
    else renderFromDraftOrMemory();
  } else {
    profileView.hidden = true;
    const hasOpen = !!currentSession();
    startView.hidden = hasOpen;
    chatView.hidden = !hasOpen;
  }
}
navBtns.forEach((b) => b.addEventListener('click', () => switchView(b.dataset.view)));

/* ---------- 动态子表：增删 ---------- */
function cloneTemplate(id) {
  const tpl = document.getElementById(id);
  return tpl.content.firstElementChild.cloneNode(true);
}

function appendDynamicRow(listId, tplId) {
  const list = document.getElementById(listId);
  list.appendChild(cloneTemplate(tplId));
}
function bindDynamicRowActions() {
  document.querySelectorAll('#edu-list, #work-list, #cert-list').forEach((list) => {
    list.addEventListener('click', (e) => {
      if (e.target.classList.contains('pf-del')) {
        const row = e.target.closest('.pf-row');
        if (row) row.remove();
      }
    });
  });
}
$('#btn-add-edu').addEventListener('click', () => appendDynamicRow('edu-list', 'tpl-edu'));
$('#btn-add-work').addEventListener('click', () => appendDynamicRow('work-list', 'tpl-work'));
$('#btn-add-cert').addEventListener('click', () => appendDynamicRow('cert-list', 'tpl-cert'));

/* ---------- 读取 / 回填表单 ---------- */
function valOrNull(v) { return (v === undefined || v === null || String(v).trim() === '') ? null : String(v).trim(); }
function numOrNull(v) { const n = parseFloat(v); return Number.isFinite(n) ? n : null; }

/* 主档 + 偏好 + 补充 的常规字段收集（data-f / data-p / data-e） */
function readScalar(scope, attrPrefix) {
  const out = {};
  scope.querySelectorAll('[' + attrPrefix + ']').forEach((el) => {
    const key = attrPrefix.replace('data-', ''); // data-f -> f
    out[el.dataset[key]] = valOrNull(el.value);
  });
  return out;
}

function collectJobProfile() {
  const wrap = $('#profile-view .profile-wrap');

  const rawProfile = readScalar(wrap, 'data-f');
  // 薪资：页面填 K，落库存元（×1000）
  const p = {
    real_name: rawProfile.real_name,
    gender: rawProfile.gender ? Number(rawProfile.gender) : null,
    age: rawProfile.age ? Number(rawProfile.age) : null,
    phone: rawProfile.phone,
    email: rawProfile.email,
    target_position: rawProfile.target_position,
    target_city: rawProfile.target_city,
    expected_salary_min: numOrNull(rawProfile.expected_salary_min) != null ? numOrNull(rawProfile.expected_salary_min) * 1000 : null,
    expected_salary_max: numOrNull(rawProfile.expected_salary_max) != null ? numOrNull(rawProfile.expected_salary_max) * 1000 : null,
    available_date: rawProfile.available_date,
    job_seeker_type: rawProfile.job_seeker_type,
  };

  const rawPref = readScalar(wrap, 'data-p');
  const prefs = {};
  ['target_industry', 'company_type', 'interview_round_pref', 'interview_style'].forEach((k) => { prefs[k] = rawPref[k]; });
  ['accept_overtime', 'accept_business_trip', 'accept_relocation'].forEach((k) => {
    prefs[k] = rawPref[k] === 'true' ? true : (rawPref[k] === 'false' ? false : null);
  });

  const rawExtra = readScalar(wrap, 'data-e');
  const extras = { self_assessment: rawExtra.self_assessment, career_plan: rawExtra.career_plan, hobbies: rawExtra.hobbies };

  // 技能：逗号分隔 → user_skills 多条
  const skills = [];
  wrap.querySelectorAll('[data-sk]').forEach((el) => {
    (el.value || '').split(/[,，]/).map((s) => s.trim()).filter(Boolean).forEach((name) => {
      skills.push({ skill_type: el.dataset.sk, skill_name: name });
    });
  });

  const educations = [];
  document.querySelectorAll('#edu-list .pf-row').forEach((row) => {
    const r = {};
    row.querySelectorAll('[data-d]').forEach((el) => { r[el.dataset.d] = valOrNull(el.value); });
    educations.push(r);
  });

  const work_experiences = [];
  document.querySelectorAll('#work-list .pf-row').forEach((row) => {
    const r = {};
    row.querySelectorAll('[data-d]').forEach((el) => { r[el.dataset.d] = valOrNull(el.value); });
    work_experiences.push(r);
  });

  const certificates = [];
  document.querySelectorAll('#cert-list .pf-row').forEach((row) => {
    const r = {};
    row.querySelectorAll('[data-d]').forEach((el) => { r[el.dataset.d] = valOrNull(el.value); });
    if (r.cert_name && r.cert_type) certificates.push(r); // 名称与类型都填才算一条
  });

  return {
    profile: p,
    educations: educations.filter((e) => e.school || e.major || e.degree),
    work_experiences: work_experiences.filter((w) => w.company_name || w.position),
    skills,
    certificates,
    preferences: prefs,
    extras,
  };
}

/* 子表行数据回填 */
function fillRows(listId, tplId, rows, keyLabels) {
  const list = document.getElementById(listId);
  list.innerHTML = '';
  rows.forEach((row) => {
    const node = cloneTemplate(tplId);
    node.querySelectorAll('[data-d]').forEach((el) => {
      const key = el.dataset.d;
      let val = row[key];
      if (val !== undefined && val !== null) {
        if (el.type === 'date') val = String(val).slice(0, 10);
        el.value = val;
      }
    });
    list.appendChild(node);
  });
}

function fillJobProfile(data) {
  const wrap = $('#profile-view .profile-wrap');
  if (data.profile) {
    const pf = data.profile;
    wrap.querySelectorAll('[data-f]').forEach((el) => {
      const key = el.dataset.f;
      let v = pf[key];
      if (v === undefined || v === null) return;
      if (key === 'expected_salary_min' || key === 'expected_salary_max') {
        const n = Number(v) / 1000;
        el.value = Number.isInteger(n) ? String(n) : String(Math.round(n * 10) / 10);
        return;
      }
      if (key === 'age' || key === 'gender') { el.value = String(v); return; }
      el.value = v;
    });
  }
  if (data.preferences) {
    wrap.querySelectorAll('[data-p]').forEach((el) => {
      const v = data.preferences[el.dataset.p];
      if (v === undefined || v === null) return;
      el.value = typeof v === 'boolean' ? String(v) : String(v);
    });
  }
  if (data.extras) {
    wrap.querySelectorAll('[data-e]').forEach((el) => {
      const v = data.extras[el.dataset.e];
      if (v !== undefined && v !== null) el.value = v;
    });
  }
  // 技能回填：按类型分组为逗号串
  if (data.skills) {
    const byType = {};
    data.skills.forEach((s) => { (byType[s.skill_type] = byType[s.skill_type] || []).push(s.skill_name); });
    wrap.querySelectorAll('[data-sk]').forEach((el) => {
      const arr = byType[el.dataset.sk] || [];
      el.value = arr.join(', ');
    });
  }
  fillRows('edu-list', 'tpl-edu', data.educations || []);
  fillRows('work-list', 'tpl-work', data.work_experiences || []);
  fillRows('cert-list', 'tpl-cert', data.certificates || []);
}

/* ---------- 数据来源策略：远程档案 / 本地草稿 / 空 ---------- */
function renderFromDraftOrMemory() {
  const draft = localStorage.getItem(DRAFT_KEY);
  if (draft) {
    try { fillJobProfile(JSON.parse(draft)); showProfileMsg('已载入本地草稿，可继续编辑后提交', ''); return; }
    catch (e) { localStorage.removeItem(DRAFT_KEY); }
  }
}
async function loadProfileFromServer() {
  try {
    const data = await request('/job-profile', { method: 'GET' });
    profileLoaded = true;
    if (data && (data.profile || (data.educations && data.educations.length) || (data.work_experiences && data.work_experiences.length) || data.preferences || data.extras)) {
      fillJobProfile(data);
      showProfileMsg('已载入现有档案，可直接编辑修改', '');
    } else {
      renderFromDraftOrMemory();
    }
  } catch (err) {
    profileLoaded = true;
    showProfileMsg(err.message, 'err');
  }
}

/* ---------- 校验必填 ---------- */
function validateProfile() {
  const wrap = $('#profile-view .profile-wrap');
  let firstBad = null;
  const required = [
    ['real_name', '请填写姓名'],
    ['phone', '请填写联系电话']
  ];
  wrap.querySelectorAll('[data-f]').forEach((el) => { el.classList.remove('invalid'); });
  required.forEach(([key, msg]) => {
    const el = wrap.querySelector('[data-f="' + key + '"]');
    if (!el || !String(el.value).trim()) {
      if (el) el.classList.add('invalid');
      if (!firstBad) firstBad = msg;
    }
  });
  if (firstBad) showProfileMsg(firstBad, 'err');
  return !firstBad;
}

/* ---------- 保存草稿 ---------- */
$('#btn-draft').addEventListener('click', () => {
  localStorage.setItem(DRAFT_KEY, JSON.stringify(collectJobProfile()));
  showProfileMsg('草稿已保存到本地', 'ok');
});

/* ---------- 提交保存 ---------- */
$('#btn-save-profile').addEventListener('click', async () => {
  if (!validateProfile()) return;
  const btn = $('#btn-save-profile');
  btn.disabled = true;
  try {
    const payload = collectJobProfile();
    await request('/job-profile', { method: 'PUT', body: payload });
    profileLoaded = true;
    localStorage.removeItem(DRAFT_KEY);
    showProfileMsg('保存成功', 'ok');
  } catch (err) {
    showProfileMsg(err.message, 'err');
  } finally {
    btn.disabled = false;
  }
});

bindDynamicRowActions();

/* ---------- 事件绑定（面试） ---------- */
answerInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); sendAnswer(); } });
$('#btn-send').addEventListener('click', sendAnswer);
$('#btn-end').addEventListener('click', endInterview);



/* ---------- 启动 ---------- */
(function init() {
  if (getToken()) {
    showApp();
  } else {
    showLogin();
  }
})();

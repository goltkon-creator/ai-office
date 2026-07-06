const AGENTS = {
  xenon: { name: 'XENON', role: 'Оркестратор' },
  copywriter: { name: 'КОПИРАЙТЕР', role: 'Текст' },
  structurer: { name: 'СТРУКТУРАТОР', role: 'Блоки Tilda' },
  finalizer: { name: 'ФИНАЛИЗАТОР', role: 'Результат' }
};

let ws = null;
let currentResult = '';

function connect() {
  const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${protocol}//${location.host}/ws`);

  ws.onopen = () => {
    setConnected(true);
    addLog('system', 'Подключён к AI-офису');
    ws.send(JSON.stringify({ type: 'get_history' }));
  };

  ws.onclose = () => {
    setConnected(false);
    addLog('system', 'Соединение потеряно. Переподключение...');
    setTimeout(connect, 3000);
  };

  ws.onerror = () => {
    setConnected(false);
  };

  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    handleMessage(msg);
  };
}

function handleMessage(msg) {
  switch (msg.type) {
    case 'task_started':
      addLog('xenon', `Задача #${msg.task_id} запущена`);
      break;

    case 'agent_update':
      updateAgent(msg.agent, msg.status, msg.message);
      addLog(msg.agent, msg.message || msg.status);
      break;

    case 'result':
      currentResult = msg.content;
      showResult(msg.content);
      resetAgents();
      document.getElementById('send-btn').disabled = false;
      addLog('xenon', 'Готово! Результат получен.');
      ws.send(JSON.stringify({ type: 'get_history' }));
      break;

    case 'history':
      renderHistory(msg.tasks);
      break;

    case 'error':
      addLog('system', `Ошибка: ${msg.message}`);
      document.getElementById('send-btn').disabled = false;
      resetAgents();
      break;
  }
}

function updateAgent(agentId, status, message) {
  const card = document.getElementById(`agent-${agentId}`);
  if (!card) return;

  card.className = `workstation ${status}`;

  const statusEl = card.querySelector('.ws-status');
  if (statusEl) {
    statusEl.className = `ws-status ${status}`;
    const labels = { idle: 'ПРОСТОЙ', working: 'РАБОТАЕТ', done: 'ГОТОВО' };
    statusEl.textContent = labels[status] || status;
  }

  const msgEl = card.querySelector('.ws-msg');
  if (msgEl && message) msgEl.textContent = message;
}

function resetAgents() {
  Object.keys(AGENTS).forEach(id => {
    updateAgent(id, 'idle', '');
    const card = document.getElementById(`agent-${id}`);
    if (card) {
      const msg = card.querySelector('.ws-msg');
      if (msg) msg.textContent = '';
    }
  });
}

function sendTask() {
  const ta = document.getElementById('brief-input');
  const brief = ta.value.trim();
  if (!brief || !ws || ws.readyState !== WebSocket.OPEN) return;

  resetAgents();
  hideResult();
  document.getElementById('send-btn').disabled = true;

  ws.send(JSON.stringify({ type: 'task', content: brief }));
  addLog('xenon', 'Задача принята: ' + brief.slice(0, 40) + '...');

  // Switch to log tab
  showTab('log');
}

function addLog(agent, message) {
  const wrap = document.getElementById('log-wrap');
  const time = new Date().toLocaleTimeString('ru', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  const el = document.createElement('div');
  el.className = 'log-entry';
  el.innerHTML = `
    <span class="log-time">${time}</span>
    <span class="log-agent">[${(AGENTS[agent]?.name || agent).toUpperCase()}]</span>
    <span>${escapeHtml(message)}</span>
  `;
  wrap.appendChild(el);
  wrap.scrollTop = wrap.scrollHeight;
}

function showResult(content) {
  const el = document.getElementById('result-content');
  el.textContent = content;
  showTab('result');
}

function hideResult() {
  document.getElementById('result-content').textContent = '';
}

function copyResult() {
  if (!currentResult) return;
  navigator.clipboard.writeText(currentResult).then(() => {
    const btn = document.getElementById('copy-btn');
    btn.textContent = 'СКОПИРОВАНО!';
    setTimeout(() => btn.textContent = 'КОПИРОВАТЬ', 2000);
  });
}

function renderHistory(tasks) {
  const list = document.getElementById('history-list');
  list.innerHTML = '';
  if (!tasks.length) {
    list.innerHTML = '<div style="color:#555;font-size:7px;padding:8px">Нет истории</div>';
    return;
  }
  tasks.forEach(t => {
    const el = document.createElement('div');
    el.className = 'history-item';
    const date = new Date(t.created_at).toLocaleString('ru');
    el.innerHTML = `
      <div class="history-brief">${escapeHtml(t.brief.slice(0, 60))}${t.brief.length > 60 ? '...' : ''}</div>
      <div class="history-meta">#${t.id} · ${date} · ${t.status.toUpperCase()}</div>
    `;
    el.onclick = () => {
      if (t.result) {
        currentResult = t.result;
        showResult(t.result);
      }
    };
    list.appendChild(el);
  });
}

function showTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelector(`.tab[data-tab="${name}"]`).classList.add('active');
  document.getElementById(`tab-${name}`).classList.add('active');
}

function setConnected(yes) {
  const dot = document.getElementById('conn-dot');
  const label = document.getElementById('conn-label');
  dot.className = 'status-dot' + (yes ? ' connected' : '');
  label.textContent = yes ? 'ПОДКЛЮЧЁН' : 'НЕТ СОЕДИНЕНИЯ';
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  connect();

  document.getElementById('send-btn').onclick = sendTask;

  document.getElementById('copy-btn').onclick = copyResult;

  document.getElementById('brief-input').addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') sendTask();
  });

  document.querySelectorAll('.tab').forEach(tab => {
    tab.onclick = () => showTab(tab.dataset.tab);
  });
});

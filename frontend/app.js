// ========================
// 智能外呼机器人 Web 控制台
// ========================

let API_URL = localStorage.getItem('apiUrl') || 'http://maoni.icu:5000';
let configNoticeDismissed = false;

// ─── 工具函数 ───────────────────────────────────────

async function api(path, options = {}) {
    const url = API_URL + path;
    const defaults = {
        headers: { 'Content-Type': 'application/json' },
    };
    if (options.body) defaults.body = JSON.stringify(options.body);
    const cfg = { ...defaults, ...options };
    try {
        const res = await fetch(url, cfg);
        const ct = res.headers.get('content-type') || '';
        let data;
        if (ct.includes('application/json')) {
            data = await res.json();
        } else {
            const text = await res.text();
            throw new Error(`服务器返回非JSON响应 (${res.status})。请检查后端日志: ${text.slice(0, 200)}`);
        }
        if (!res.ok) throw new Error(data.error || data.message || `HTTP ${res.status}`);
        return data;
    } catch (e) {
        // 检测凭据错误
        const msg = e.message || '';
        if ((msg.includes('InvalidCredentials') || msg.includes('credentials') || msg.includes('非JSON') || msg.includes('403') || msg.includes('401')) && !configNoticeDismissed) {
            document.getElementById('configNotice').style.display = 'block';
            configNoticeDismissed = true;
        }
        toast(e.message, 'error');
        throw e;
    }
}

function toast(msg, type = 'info') {
    const container = document.getElementById('toastContainer');
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = msg;
    container.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

function setStatusBadge(status) {
    const map = {
        'Running': 'status-running', 'Active': 'status-running',
        'Completed': 'status-completed', 'Published': 'status-published',
        'Paused': 'status-paused', 'Failed': 'status-failed',
        'Pending': 'status-pending', 'Created': 'status-created',
        'Cancelled': 'status-cancelled',
    };
    return `<span class="status-badge ${map[status] || ''}">${status || '-'}</span>`;
}

function progressBar(completed, total) {
    const pct = total > 0 ? Math.round(completed / total * 100) : 0;
    return `<div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:${pct}%"></div></div><span class="progress-text">${completed}/${total} (${pct}%)</span>`;
}

function genSessionId() {
    return 'sess_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

function now() {
    return new Date().toLocaleTimeString('zh-CN');
}

// ─── 页面导航 ───────────────────────────────────────

const pageTitles = {
    dashboard: '控制台',
    instances: '实例管理',
    scripts: '话术管理',
    'job-groups': '任务管理',
    dialogue: '对话测试',
    statistics: '数据统计',
};

function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const el = document.getElementById('page-' + page);
    if (el) el.style.display = 'block';
    const nav = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (nav) nav.classList.add('active');
    document.getElementById('pageTitle').textContent = pageTitles[page] || page;

    // 加载对应页面数据
    switch (page) {
        case 'dashboard': loadDashboard(); break;
        case 'instances': loadInstances(); break;
        case 'scripts': loadScripts(); break;
        case 'job-groups': loadJobGroups(); break;
        case 'dialogue': initDialogue(); break;
        case 'statistics': break; // 手动查询
    }
}

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', e => {
        e.preventDefault();
        navigateTo(item.dataset.page);
    });
});

// ─── 健康检查 ───────────────────────────────────────

function saveApiUrl() {
    const input = document.getElementById('apiUrl');
    let url = input.value.trim().replace(/\/$/, '');
    if (!url) { toast('请输入 API 地址', 'error'); return; }
    API_URL = url;
    localStorage.setItem('apiUrl', url);
    toast('API 地址已保存', 'success');
}

async function checkHealth() {
    try {
        const data = await api('/health');
        const bar = document.getElementById('healthBar');
        bar.className = 'health-bar ok';
        bar.innerHTML = `<span class="health-status">✅ 服务正常 — ${data.region} — ${data.timestamp}</span>`;
        toast('服务正常', 'success');
    } catch (e) {
        const bar = document.getElementById('healthBar');
        bar.className = 'health-bar error';
        bar.innerHTML = `<span class="health-status">❌ 服务异常 — ${e.message}</span>`;
        toast('服务异常: ' + e.message, 'error');
    }
}

// ─── 仪表盘 ─────────────────────────────────────────

async function loadDashboard() {
    // 加载统计数据
    try {
        const instances = await api('/instances');
        const instList = instances.Instances?.Instance || [];
        document.getElementById('stat-total-jobs').textContent = instList.length;
    } catch (e) { /* ignore */ }

    try {
        const scripts = await api('/scripts');
        const sList = scripts.Scripts?.Script || [];
        document.getElementById('stat-scripts').textContent = sList.length;
    } catch (e) { /* ignore */ }

    // 加载最近任务
    try {
        const groups = await api('/job-groups');
        const list = groups.JobGroups?.JobGroup || [];
        const tbody = document.getElementById('dashRecentJobs');
        if (list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="placeholder-text">暂无任务组</td></tr>';
            return;
        }
        tbody.innerHTML = list.slice(0, 10).map(g => {
            const prog = g.Progress || {};
            const total = prog.TotalJobs || 0;
            const completed = prog.TotalCompleted || 0;
            return `<tr>
                <td>${g.JobGroupId || '-'}</td>
                <td>${g.JobGroupName || '-'}</td>
                <td>${setStatusBadge(g.Status)}</td>
                <td>${total}</td>
                <td>${completed}</td>
                <td>${g.CreationTime || '-'}</td>
                <td><div class="action-group">
                    <button class="btn btn-sm btn-success" onclick="startJob('${g.JobGroupId}')">启动</button>
                    <button class="btn btn-sm btn-outline" onclick="viewProgress('${g.JobGroupId}')">进度</button>
                </div></td>
            </tr>`;
        }).join('');
    } catch (e) {
        document.getElementById('dashRecentJobs').innerHTML = '<tr><td colspan="7" class="placeholder-text">加载失败</td></tr>';
    }
}

async function startJob(id) {
    try {
        await api(`/job-groups/${id}/start`, { method: 'POST' });
        toast('任务已启动', 'success');
        loadDashboard();
    } catch (e) { /* handled in api() */ }
}

async function viewProgress(id) {
    try {
        const p = await api(`/job-groups/${id}/progress`);
        showProgressModal(p);
    } catch (e) { /* handled */ }
}

function showProgressModal(p) {
    const pct = p.total > 0 ? Math.round(p.completed / p.total * 100) : 0;
    document.getElementById('modalTitle').textContent = '任务进度';
    document.getElementById('modalBody').innerHTML = `
        <div class="stats-summary">
            <div class="summary-item"><div class="label">任务组</div><div class="value">${p.job_group_id || '-'}</div></div>
            <div class="summary-item"><div class="label">名称</div><div class="value">${p.name || '-'}</div></div>
            <div class="summary-item"><div class="label">状态</div><div class="value">${setStatusBadge(p.status)}</div></div>
        </div>
        <div class="stats-summary">
            <div class="summary-item"><div class="label">总数</div><div class="value">${p.total}</div></div>
            <div class="summary-item"><div class="label">已完成</div><div class="value" style="color:var(--green)">${p.completed}</div></div>
            <div class="summary-item"><div class="label">待执行</div><div class="value" style="color:var(--orange)">${p.pending}</div></div>
            <div class="summary-item"><div class="label">运行中</div><div class="value" style="color:var(--blue)">${p.running}</div></div>
            <div class="summary-item"><div class="label">失败</div><div class="value" style="color:var(--red)">${p.failed}</div></div>
        </div>
        <div style="margin-top:12px">
            <div class="progress-bar-wrap" style="height:10px;width:100%"><div class="progress-bar-fill" style="width:${pct}%"></div></div>
            <span class="progress-text">${pct}%</span>
        </div>
    `;
    document.getElementById('modalFooter').innerHTML = '<button class="btn btn-primary" onclick="closeModal()">关闭</button>';
    openModal();
}

// ─── 实例管理 ───────────────────────────────────────

async function loadInstances() {
    try {
        const data = await api('/instances');
        const list = data.Instances?.Instance || [];
        const tbody = document.getElementById('instancesTable');
        if (list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="placeholder-text">暂无实例</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(i => `<tr>
            <td>${i.InstanceId || '-'}</td>
            <td>${i.InstanceName || '-'}</td>
            <td>${setStatusBadge(i.Status)}</td>
            <td>${i.RegionId || '-'}</td>
            <td>-</td>
            <td><button class="btn btn-sm btn-outline" onclick="describeInstance('${i.InstanceId}')">详情</button></td>
        </tr>`).join('');
    } catch (e) {
        document.getElementById('instancesTable').innerHTML = '<tr><td colspan="6" class="placeholder-text">加载失败，请检查 API 配置</td></tr>';
    }
}

async function describeInstance(id) {
    try {
        const data = await api(`/instances/${id}`);
        const info = data.Instance || {};
        document.getElementById('modalTitle').textContent = '实例详情';
        document.getElementById('modalBody').innerHTML = Object.entries(info)
            .filter(([k, v]) => v != null)
            .map(([k, v]) => `<div style="margin-bottom:8px"><strong>${k}:</strong> ${typeof v === 'object' ? JSON.stringify(v) : v}</div>`)
            .join('');
        document.getElementById('modalFooter').innerHTML = '<button class="btn btn-primary" onclick="closeModal()">关闭</button>';
        openModal();
    } catch (e) { /* handled */ }
}

// ─── 话术管理 ───────────────────────────────────────

async function loadScripts() {
    try {
        const data = await api('/scripts');
        const list = data.Scripts?.Script || [];
        const tbody = document.getElementById('scriptsTable');
        if (list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="placeholder-text">暂无话术</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(s => `<tr>
            <td>${s.ScriptId || '-'}</td>
            <td>${s.ScriptName || '-'}</td>
            <td>${s.ScriptDescription || '-'}</td>
            <td>${setStatusBadge(s.Status)}</td>
            <td>${s.IsDebugged ? '✅' : '❌'}</td>
            <td>${s.IsPublished ? '✅' : '❌'}</td>
            <td><div class="action-group">
                <button class="btn btn-sm btn-outline" onclick="viewScript('${s.ScriptId}')">查看</button>
                ${!s.IsPublished ? `<button class="btn btn-sm btn-success" onclick="publishScript('${s.ScriptId}')">发布</button>` : ''}
            </div></td>
        </tr>`).join('');
    } catch (e) {
        document.getElementById('scriptsTable').innerHTML = '<tr><td colspan="7" class="placeholder-text">加载失败</td></tr>';
    }
}

async function viewScript(id) {
    try {
        const data = await api(`/scripts/${id}`);
        const info = data.Script || data.script || {};
        document.getElementById('modalTitle').textContent = '话术详情';
        document.getElementById('modalBody').innerHTML = `
            <div class="form-group"><label>ID</label><div>${info.ScriptId || '-'}</div></div>
            <div class="form-group"><label>名称</label><div>${info.ScriptName || '-'}</div></div>
            <div class="form-group"><label>描述</label><div>${info.ScriptDescription || '-'}</div></div>
            <div class="form-group"><label>内容</label><textarea readonly style="min-height:200px">${info.ScriptContent || '无'}</textarea></div>
        `;
        document.getElementById('modalFooter').innerHTML = '<button class="btn btn-primary" onclick="closeModal()">关闭</button>';
        openModal();
    } catch (e) { /* handled */ }
}

async function publishScript(id) {
    try {
        await api(`/scripts/${id}/publish`, { method: 'POST' });
        toast('话术已发布', 'success');
        loadScripts();
    } catch (e) { /* handled */ }
}

function showCreateScriptModal() {
    document.getElementById('modalTitle').textContent = '创建话术';
    document.getElementById('modalBody').innerHTML = `
        <div class="form-group"><label>话术名称</label><input type="text" id="newScriptName" placeholder="客户回访-v1"></div>
        <div class="form-group"><label>描述</label><input type="text" id="newScriptDesc" placeholder="简要描述"></div>
        <div class="form-group"><label>话术内容 (JSON)</label><textarea id="newScriptContent" placeholder='{ "type": "flow", "nodes": [...] }'></textarea></div>
    `;
    document.getElementById('modalConfirm').onclick = async () => {
        const name = document.getElementById('newScriptName').value.trim();
        const desc = document.getElementById('newScriptDesc').value.trim();
        const content = document.getElementById('newScriptContent').value.trim();
        if (!name || !content) { toast('请填写名称和内容', 'error'); return; }
        try {
            await api('/scripts', {
                method: 'POST',
                body: { name, script_content: content, script_description: desc },
            });
            toast('话术创建成功', 'success');
            closeModal();
            loadScripts();
        } catch (e) { /* handled */ }
    };
    openModal();
}

// ─── 任务管理 ───────────────────────────────────────

async function loadJobGroups() {
    try {
        const data = await api('/job-groups');
        const list = data.JobGroups?.JobGroup || [];
        const tbody = document.getElementById('jobGroupsTable');
        if (list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="placeholder-text">暂无任务组</td></tr>';
            return;
        }
        tbody.innerHTML = list.map(g => {
            const prog = g.Progress || {};
            const total = prog.TotalJobs || 0;
            const completed = prog.TotalCompleted || 0;
            const failed = prog.TotalFailed || 0;
            return `<tr>
                <td>${g.JobGroupId || '-'}</td>
                <td>${g.JobGroupName || '-'}</td>
                <td>${g.ScriptId || '-'}</td>
                <td>${setStatusBadge(g.Status)}</td>
                <td>${progressBar(completed, total)}</td>
                <td>${total}</td>
                <td>${completed}</td>
                <td>${failed}</td>
                <td><div class="action-group">
                    ${g.Status !== 'Running' ? `<button class="btn btn-sm btn-success" onclick="startJob('${g.JobGroupId}')">启动</button>` : ''}
                    ${g.Status === 'Running' ? `<button class="btn btn-sm btn-outline" onclick="pauseJob('${g.JobGroupId}')">暂停</button>` : ''}
                    <button class="btn btn-sm btn-outline" onclick="viewProgress('${g.JobGroupId}')">进度</button>
                    <button class="btn btn-sm btn-danger" onclick="cancelJob('${g.JobGroupId}')">取消</button>
                </div></td>
            </tr>`;
        }).join('');
    } catch (e) {
        document.getElementById('jobGroupsTable').innerHTML = '<tr><td colspan="9" class="placeholder-text">加载失败</td></tr>';
    }
}

async function pauseJob(id) {
    try {
        await api(`/job-groups/${id}/pause`, { method: 'POST' });
        toast('任务已暂停', 'success');
        loadJobGroups();
    } catch (e) { /* handled */ }
}

async function cancelJob(id) {
    if (!confirm('确定要取消该任务吗？')) return;
    try {
        await api(`/job-groups/${id}/cancel`, { method: 'POST' });
        toast('任务已取消', 'success');
        loadJobGroups();
    } catch (e) { /* handled */ }
}

function showBatchJobModal() {
    document.getElementById('modalTitle').textContent = '创建批量外呼任务';
    document.getElementById('modalBody').innerHTML = `
        <div class="form-group"><label>任务名称</label><input type="text" id="batchJobName" placeholder="回访任务-0614"></div>
        <div class="form-group"><label>话术ID</label><input type="text" id="batchScriptId" placeholder="script_xxx"></div>
        <div class="form-group"><label>联系人 (每行一个, 格式: phone,name)</label>
            <textarea id="batchContacts" placeholder="13800138001,张三&#10;13800138002,李四" style="min-height:150px;font-family:monospace"></textarea>
        </div>
    `;
    document.getElementById('modalConfirm').onclick = async () => {
        const name = document.getElementById('batchJobName').value.trim();
        const scriptId = document.getElementById('batchScriptId').value.trim();
        const contactsText = document.getElementById('batchContacts').value.trim();
        if (!name || !scriptId || !contactsText) { toast('请填写所有字段', 'error'); return; }
        const contacts = contactsText.split('\n').filter(l => l.trim()).map(line => {
            const parts = line.split(',');
            return { phone: parts[0].trim(), name: parts[1]?.trim() || '' };
        });
        try {
            const data = await api('/jobs/batch', {
                method: 'POST',
                body: { name, script_id: scriptId, contacts },
            });
            toast(`任务创建成功，共 ${data.total} 人`, 'success');
            closeModal();
            loadJobGroups();
        } catch (e) { /* handled */ }
    };
    openModal();
}

// ─── 对话测试 ───────────────────────────────────────

let dialogueSessionId = '';
let dialogueCaller = '';
let dialogueCallee = '';

function initDialogue() {
    if (!dialogueSessionId) {
        document.getElementById('dialogueSessionId').value = genSessionId();
    }
    document.getElementById('dialogueMessages').innerHTML = '<p class="placeholder-text">点击"新会话"或发送消息开始对话</p>';
}

function resetDialogue() {
    dialogueSessionId = genSessionId();
    document.getElementById('dialogueSessionId').value = dialogueSessionId;
    document.getElementById('dialogueMessages').innerHTML = '';
    toast('新会话已开始', 'info');
}

function addMessage(role, text) {
    const container = document.getElementById('dialogueMessages');
    const div = document.createElement('div');
    div.className = `msg msg-${role}`;
    const avatar = role === 'bot' ? '🤖' : '👤';
    div.innerHTML = `
        <div class="msg-avatar">${avatar}</div>
        <div>
            <div class="msg-content">${escapeHtml(text)}</div>
            <div class="msg-meta">${now()}</div>
        </div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

async function sendDialogue() {
    const input = document.getElementById('dialogueInput');
    const text = input.value.trim();
    if (!text) return;

    dialogueSessionId = document.getElementById('dialogueSessionId').value.trim() || genSessionId();
    dialogueCaller = document.getElementById('dialogueCaller').value.trim() || '13800138000';
    dialogueCallee = document.getElementById('dialogueCallee').value.trim() || '13900139000';

    input.value = '';
    addMessage('user', text);

    try {
        const data = await api('/dialogue', {
            method: 'POST',
            body: {
                session_id: dialogueSessionId,
                utterance: text,
                calling_number: dialogueCaller,
                called_number: dialogueCallee,
            },
        });
        const reply = data.reply || data.Reply || data.content || data.Content || JSON.stringify(data);
        addMessage('bot', reply);
    } catch (e) {
        addMessage('bot', `请求失败: ${e.message}`);
    }
}

// ─── 数据统计 ───────────────────────────────────────

async function loadStatistics() {
    const id = document.getElementById('statJobGroupId').value.trim();
    if (!id) { toast('请输入任务组ID', 'error'); return; }

    document.getElementById('statsSummary').innerHTML = '<div class="loading">加载中...</div>';

    try {
        const data = await api(`/statistics/${id}`);
        const colors = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];
        document.getElementById('statsSummary').innerHTML = `
            <div class="stats-summary">
                <div class="summary-item"><div class="label">总任务数</div><div class="value">${data.total_jobs || 0}</div></div>
                <div class="summary-item"><div class="label">已完成</div><div class="value" style="color:var(--green)">${data.completed_jobs || 0}</div></div>
                <div class="summary-item"><div class="label">失败</div><div class="value" style="color:var(--red)">${data.failed_jobs || 0}</div></div>
                <div class="summary-item"><div class="label">完成率</div><div class="value">${data.completion_rate || 0}%</div></div>
                <div class="summary-item"><div class="label">成功率</div><div class="value" style="color:var(--green)">${data.success_rate || 0}%</div></div>
                <div class="summary-item"><div class="label">平均时长</div><div class="value">${data.average_duration_seconds || 0}s</div></div>
            </div>
        `;

        // 状态分布图
        const dist = data.status_distribution || {};
        const maxVal = Math.max(...Object.values(dist), 1);
        let chartHtml = '<div class="status-bar-chart"><h4 style="margin-bottom:12px">状态分布</h4>';
        Object.entries(dist).forEach(([key, val], i) => {
            const pct = (val / maxVal * 100).toFixed(0);
            chartHtml += `<div class="bar-row">
                <span class="bar-label">${key}</span>
                <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${colors[i % colors.length]}">${val}</div></div>
                <span class="bar-value">${val}</span>
            </div>`;
        });
        chartHtml += '</div>';
        document.getElementById('statusChart').innerHTML = chartHtml;
    } catch (e) {
        document.getElementById('statsSummary').innerHTML = `<p class="placeholder-text">查询失败: ${e.message}</p>`;
    }
}

function dismissConfigNotice() {
    document.getElementById('configNotice').style.display = 'none';
    configNoticeDismissed = true;
}

// 模态框

function openModal() {
    document.getElementById('modalOverlay').style.display = 'flex';
}

function closeModal() {
    document.getElementById('modalOverlay').style.display = 'none';
    // 恢复默认 footer
    document.getElementById('modalFooter').innerHTML = `
        <button class="btn btn-outline" onclick="closeModal()">取消</button>
        <button class="btn btn-primary" id="modalConfirm">确定</button>
    `;
}

// 点击遮罩关闭
document.getElementById('modalOverlay').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
});

// ─── 初始化 ─────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    // 加载保存的 API 地址
    document.getElementById('apiUrl').value = API_URL;
    // 进入仪表盘
    navigateTo('dashboard');
    // 自动检查健康
    checkHealth();
});

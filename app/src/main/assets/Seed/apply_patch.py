with open('/workspace/BE/English_v1.3.2.html', 'r') as f:
    content = f.read()

# 1. Replace wrong list rendering in finishPractice
old = '''  // 错题列表（每条错误记录单独一行）
  var ws = document.getElementById('wrongSection');
  var wl = document.getElementById('wrongList');
  wl.innerHTML = '';
  if (state.wrongRecords.length > 0) {
    ws.style.display = 'block';
    state.wrongRecords.forEach(function(r) {
      var div = document.createElement('div');
      div.className = 'w-item';
      var skipTag = r.isSkip ? ' [跳过]' : '';
      div.innerHTML =
        '<div class="wi-l"><span class="wi-ch">' + escHtml(r.chinese) + '</span>' + skipTag +
        '<br><span class="wi-ok">正确: ' + escHtml(r.answer) + '</span>' +
        ' <span class="wi-user">你答: ' + escHtml(r.userInput) + '</span></div>';
      wl.appendChild(div);
    });
  } else {
    ws.style.display = 'none';
  }'''

new = '''  // 错题列表（合并同一题目的多次错误，点击展开）
  var ws = document.getElementById('wrongSection');
  var wl = document.getElementById('wrongList');
  wl.innerHTML = '';
  if (state.wrongRecords.length > 0) {
    ws.style.display = 'block';
    var groups = {};
    state.wrongRecords.forEach(function(r) {
      if (!groups[r.index]) groups[r.index] = [];
      groups[r.index].push(r);
    });
    Object.keys(groups).forEach(function(idx) {
      var attempts = groups[idx];
      var first = attempts[0];
      var groupDiv = document.createElement('div');
      groupDiv.className = 'w-group';
      var badge = attempts.length > 1 ? ' <span style="font-size:11px;color:#888">尝试' + attempts.length + '次</span>' : '';
      groupDiv.innerHTML =
        '<div class="w-group-header" onclick="this.classList.toggle(\\'expanded\\');this.nextElementSibling.classList.toggle(\\'show\\')">' +
        '<span class="w-g-title">' + escHtml(first.chinese) + ' ' + escHtml(first.answer) + '</span>' +
        badge +
        '<span class="w-g-arrow">▼</span></div>' +
        '<div class="w-group-body">' +
        attempts.map(function(a, i) {
          var label = a.isSkip ? '跳过' : '第' + (i + 1) + '次';
          return '<div class="w-attempt"><span class="wa-label">' + label + '</span> 答案: <span class="wa-wrong">' + escHtml(a.userInput) + '</span></div>';
        }).join('') +
        '</div>';
      wl.appendChild(groupDiv);
    });
  } else {
    ws.style.display = 'none';
  }'''

content = content.replace(old, new)

# 2. Add CSS for expandable wrong items
old_css_end = '\n</style>'
group_css = '''
/* ===== Expandable Wrong Items ===== */
.w-group{margin-bottom:8px}
.w-group-header{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:var(--sub-bg);border-radius:8px 8px 0 0;border-left:3px solid #dc3545;cursor:pointer;font-size:13px;user-select:none;transition:background .15s}
.w-group-header:hover{background:var(--hover-bg)}
.w-group-header .w-g-title{font-weight:600;color:var(--text);flex:1}
.w-group-header .w-g-arrow{font-size:12px;color:#999;transition:transform .2s}
.w-group-header.expanded .w-g-arrow{transform:rotate(180deg)}
.w-group-body{display:none;background:var(--card-bg);border-radius:0 0 8px 8px;border:1px solid var(--border);border-top:none;overflow:hidden}
.w-group-body.show{display:block}
.w-attempt{padding:8px 14px;font-size:12px;border-bottom:1px solid var(--border);line-height:1.6}
.w-attempt:last-child{border-bottom:none}
.w-attempt .wa-label{color:#888;font-size:11px}
.w-attempt .wa-wrong{color:#dc3545}
'''
content = content.replace(old_css_end, group_css + '\n</style>')

# 3. Update conversion tool prompt
old_prompt = "    + '规则：\\n1. 从输入中提取中英文对照信息\\n2. chinese填中文，answer填英文\\n3. type判断：单词用word，短语用phrase，句子用sentence\\n4. 只输出JSON，不要解释';"
new_prompt = "    + '规则：\\n1. 从输入中提取中英文对照信息\\n2. chinese填中文，answer填英文\\n3. type判断：单词用word，短语用phrase，句子用sentence\\n4. 只输出JSON，不要解释\\n5. 重要：如果句子中包含多段对话（如A:...B:...），请拆分每条对话为独立的question\\n6. 重要：如果句子中包含\\\"/\\\"或\\\"或\\\"分隔的不同内容，请拆分为多个独立的question\\n7. 每条对话或每个选项作为独立的question，type均设为sentence';"
content = content.replace(old_prompt, new_prompt)

# 4. Update integrity promise text
old_integrity = '''      <strong>📖 练习须知</strong><br><br>
      亲爱的同学，学习是一个诚实面对自己的过程。<br><br>
      本次默写练习期望你<strong>独立完成</strong>，不查阅资料、不切换页面搜索答案。<br>
      练习过程中已开启<strong>切屏检测</strong>，切换页面将被记录。<br><br>
      ✅ 诚实练习能真实反映你的掌握情况<br>
      ✅ 发现薄弱环节才能更有针对性地提高<br>
      ✅ 每一次诚信都是对自己的尊重<br><br>
      请认真对待，祝练习顺利！🎯'''
new_integrity = '''      <strong>📖 练习须知</strong><br><br>
      亲爱的同学，学习是一个诚实面对自己的过程。<br><br>
      本次默写练习期望你<strong>独立完成</strong>，不查阅资料、不切换页面搜索答案。<br>
      练习过程中已开启<strong>切屏检测</strong>，切换页面将被记录。<br><br>
      <strong>📋 答题规则</strong><br>
      • 每题有 <strong>2次答题机会</strong>（可在管理面板调整），第一次错误可修改后再次提交<br>
      • 第二次无论对错均进入下一题<br>
      • 每场练习允许对 <strong>20% 的题目</strong>申请 AI 复核（可在管理面板调整）<br>
      • 如对判分有异议，可在下一题页面点击"申请复核"<br><br>
      ✅ 诚实练习能真实反映你的掌握情况<br>
      ✅ 发现薄弱环节才能更有针对性地提高<br>
      ✅ 每一次诚信都是对自己的尊重<br><br>
      请认真对待，祝练习顺利！🎯'''
content = content.replace(old_integrity, new_integrity)

# 5. Add dispute banner HTML and CSS, plus dispute modal
# Add dispute banner before keyboard
old_kb_start = '  <!-- ===== Virtual Keyboard ===== -->'
new_html_with_banner = '''  <!-- ===== Dispute Banner ===== -->
  <div class="dispute-banner" id="disputeBanner" style="display:none">
    <div class="db-text" id="disputeText"></div>
    <div class="db-actions">
      <button class="btn btn-outline" onclick="showDisputeModal()" id="btnDispute" style="padding:6px 16px;font-size:12px;border-color:#6f42c1;color:#6f42c1">有异议，申请复核</button>
      <button class="btn btn-secondary" onclick="hideDisputeBanner()" style="padding:6px 16px;font-size:12px">忽略</button>
    </div>
  </div>

  <!-- ===== Virtual Keyboard ===== -->'''
content = content.replace(old_kb_start, new_html_with_banner)

# 6. Add dispute-related CSS
old_css = '\n</style>'
dispute_css = '''
/* ===== Dispute Banner ===== */
.dispute-banner{background:#f3e8ff;border:2px solid #6f42c1;border-radius:12px;padding:12px 16px;margin:10px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.dispute-banner .db-text{font-size:13px;color:#4a1d96;line-height:1.5;flex:1;min-width:200px}
.dispute-banner .db-actions{display:flex;gap:6px}

/* ===== Dispute Modal ===== */
.dispute-modal .modal-box .m-icon{text-align:center;font-size:40px;margin-bottom:8px}
.dispute-modal .modal-box h3{text-align:center}
.d-status{padding:12px;border-radius:8px;margin:10px 0;font-size:13px;text-align:center;line-height:1.6}
.d-status.loading{background:#f3e8ff;color:#6f42c1}
.d-status.success{background:#d4edda;color:#155724}
.d-status.error{background:#f8d7da;color:#721c24}
'''
content = content.replace(old_css, dispute_css + '\n</style>')

# 7. Add dispute modal HTML before </body>
old_body_end = '</body>'
dispute_modal = '''<!-- ===== Dispute Modal ===== -->
<div class="modal-overlay dispute-modal" id="disputeModal">
  <div class="modal-box">
    <div class="m-icon">🤔</div>
    <h3>申请复核</h3>
    <p style="font-size:13px;color:#666;text-align:center;margin:6px 0">系统将把您的答案提交给 AI 进行复核</p>
    <div class="d-status" id="disputeStatus" style="display:none"></div>
    <div class="q-actions" id="disputeActions">
      <button class="btn btn-secondary" onclick="closeDisputeModal()">取消</button>
      <button class="btn btn-primary" onclick="submitDispute()" style="background:#6f42c1">确认复核</button>
    </div>
  </div>
</div>

</body>'''
content = content.replace(old_body_end, dispute_modal)

# 8. Add dispute JS functions before console.log
old_console = "console.log('📝 英语默写 loaded');"
dispute_js = '''// ===== 复核功能 =====
function showDisputeBanner() {
  if (!state.lastWrong) return;
  if (state.disputeCount >= state.maxDisputes) return;
  var banner = document.getElementById('disputeBanner');
  var text = document.getElementById('disputeText');
  text.textContent = '上一题[' + state.lastWrong.chinese + ']你的答案是[' + state.lastWrong.userInput + ']，正确是[' + state.lastWrong.answer + ']。有异议？(剩余' + (state.maxDisputes - state.disputeCount) + '次)';
  banner.style.display = 'flex';
}

function hideDisputeBanner() {
  document.getElementById('disputeBanner').style.display = 'none';
}

function showDisputeModal() {
  document.getElementById('disputeStatus').style.display = 'none';
  document.getElementById('disputeActions').style.display = 'flex';
  document.getElementById('disputeModal').classList.add('show');
}

function closeDisputeModal() {
  document.getElementById('disputeModal').classList.remove('show');
}

function submitDispute() {
  var status = document.getElementById('disputeStatus');
  var actions = document.getElementById('disputeActions');
  status.style.display = 'block';
  status.className = 'd-status loading';
  status.textContent = 'AI复核中...';
  actions.style.display = 'none';

  var baseUrl = localStorage.getItem('aiBaseUrl') || 'https://api.openai.com/v1';
  var apiKey = localStorage.getItem('aiApiKey') || '';
  var model = localStorage.getItem('aiModel') || 'gpt-4o-mini';

  if (!apiKey) {
    showDisputeError('请先配置AI API Key');
    return;
  }
  if (baseUrl.endsWith('/')) baseUrl = baseUrl.slice(0, -1);
  if (!baseUrl.endsWith('/v1')) baseUrl += '/v1';

  var prompt = '你是一位英语复核老师。\\n题目：' + state.lastWrong.chinese + '\\n标准答案：' + state.lastWrong.answer + '\\n学生答案：' + state.lastWrong.userInput + '\\n请以JSON回复(is_correct true/false, explanation简短说明)。注意：忽略大小写和标点后一致或拼写小疏漏但可识别，应判正确。';

  fetch(baseUrl + '/chat/completions', {
    method: 'POST',
    headers: {'Content-Type':'application/json','Authorization':'Bearer ' + apiKey},
    body: JSON.stringify({
      model: model,
      messages: [
        {role: 'system', content: '你是一个公正的英语复核老师。'},
        {role: 'user', content: prompt}
      ],
      temperature: 0.1,
      max_tokens: 500
    })
  })
  .then(function(resp) { return resp.json(); })
  .then(function(data) {
    var content = data.choices?.[0]?.message?.content || '';
    var jsonMatch = content.match(/{[\\s\\S]*?}/);
    if (jsonMatch) {
      var result = JSON.parse(jsonMatch[0]);
      if (result.is_correct !== undefined) {
        var idx = state.lastWrong.index;
        state.disputeCount++;
        hideDisputeBanner();
        state.lastWrong = null;
        closeDisputeModal();
        alert('第' + (idx + 1) + '题，经复核后确认' + (result.is_correct ? '正确' : '错误'));
        return;
      }
    }
    showDisputeError('复核程序异常，请保持安静，待测试完成后复核。');
  })
  .catch(function(err) {
    showDisputeError('复核程序异常，请保持安静，待测试完成后复核。');
  });
}

function showDisputeError(msg) {
  var status = document.getElementById('disputeStatus');
  var actions = document.getElementById('disputeActions');
  status.className = 'd-status error';
  status.textContent = msg;
  actions.style.display = 'flex';
}

// 点击遮罩关闭
document.getElementById('disputeModal').addEventListener('click', function(e) {
  if (e.target === this) closeDisputeModal();
});

console.log('📝 英语默写 loaded');'''
content = content.replace(old_console, dispute_js)

# 9. Update admin panel config
# Add maxAttempts and disputeRatio to admin panel HTML
old_admin_fields = '''    <label>单次练习允许切屏次数</label>
    <input type="number" id="adminAllowedCount" min="0" max="99" value="3">
    <div class="admin-hint">设为 0 表示一次都不允许切屏</div>

    <div class="admin-check">
      <input type="checkbox" id="adminShowWarning" checked>
      <label for="adminShowWarning">切屏返回时显示提示</label>
    </div>

    <div class="admin-check">
      <input type="checkbox" id="adminAutoEnd">
      <label for="adminAutoEnd">超过允许次数自动结束练习</label>
    </div>

    <label>切屏提示文字 <span style="font-weight:400;color:var(--sub-text)">（支持 {count} 变量）</span></label>
    <textarea id="adminWarningText" rows="2">⚠️ 检测到切屏行为（共 {count} 次），请保持专注！</textarea>
    <div class="admin-hint">提示中的 {count} 会自动替换为实际切屏次数</div>

    <div class="admin-status" id="adminStatus"></div>'''

new_admin_fields = '''    <label>单次练习允许切屏次数</label>
    <input type="number" id="adminAllowedCount" min="0" max="99" value="3">
    <div class="admin-hint">设为 0 表示一次都不允许切屏</div>

    <div class="admin-check">
      <input type="checkbox" id="adminShowWarning" checked>
      <label for="adminShowWarning">切屏返回时显示提示</label>
    </div>

    <div class="admin-check">
      <input type="checkbox" id="adminAutoEnd">
      <label for="adminAutoEnd">超过允许次数自动结束练习</label>
    </div>

    <label>切屏提示文字 <span style="font-weight:400;color:var(--sub-text)">（支持 {count} 变量）</span></label>
    <textarea id="adminWarningText" rows="2">检测到切屏行为（共 {count} 次），请保持专注！</textarea>
    <div class="admin-hint">提示中的 {count} 会自动替换为实际切屏次数</div>

    <hr style="border:none;border-top:1px solid var(--border);margin:14px 0">

    <label>单题容错次数</label>
    <input type="number" id="adminMaxAttempts" min="1" max="5" value="2">
    <div class="admin-hint">每题可答错的次数，第1次错可修改再答，默认2次</div>

    <label>允许复核比例 (%)</label>
    <input type="number" id="adminDisputeRatio" min="0" max="50" value="20">
    <div class="admin-hint">每场练习允许申请AI复核的题目比例，默认20%</div>

    <div class="admin-status" id="adminStatus"></div>'''
content = content.replace(old_admin_fields, new_admin_fields)

# 10. Update getSwitchConfig to include new fields
old_switch = '''function getSwitchConfig() {
  var def = {allowedCount: 3, showWarning: true, autoEnd: false, warningText: '⚠️ 检测到切屏行为（共 {count} 次），请保持专注！'};
  try { return Object.assign({}, def, JSON.parse(localStorage.getItem('beSwitchConfig') || '{}')); }
  catch(e) { return def; }'''
new_switch = '''function getSwitchConfig() {
  var def = {allowedCount: 3, showWarning: true, autoEnd: false, warningText: '检测到切屏行为（共 {count} 次），请保持专注！', maxAttempts: 2, disputeRatio: 20};
  try { return Object.assign({}, def, JSON.parse(localStorage.getItem('beSwitchConfig') || '{}')); }
  catch(e) { return def; }'''
content = content.replace(old_switch, new_switch)

# 11. Update openAdminPanel
old_open = '''function openAdminPanel() {
  var cfg = getSwitchConfig();
  document.getElementById('adminAllowedCount').value = cfg.allowedCount;
  document.getElementById('adminShowWarning').checked = cfg.showWarning;
  document.getElementById('adminAutoEnd').checked = cfg.autoEnd;
  document.getElementById('adminWarningText').value = cfg.warningText;
  document.getElementById('adminStatus').textContent = '';'''
new_open = '''function openAdminPanel() {
  var cfg = getSwitchConfig();
  document.getElementById('adminAllowedCount').value = cfg.allowedCount;
  document.getElementById('adminShowWarning').checked = cfg.showWarning;
  document.getElementById('adminAutoEnd').checked = cfg.autoEnd;
  document.getElementById('adminWarningText').value = cfg.warningText;
  document.getElementById('adminMaxAttempts').value = cfg.maxAttempts || 2;
  document.getElementById('adminDisputeRatio').value = cfg.disputeRatio || 20;
  document.getElementById('adminStatus').textContent = '';'''
content = content.replace(old_open, new_open)

# 12. Update saveAdminConfig
old_save = '''function saveAdminConfig() {
  var cfg = {
    allowedCount: parseInt(document.getElementById('adminAllowedCount').value) || 3,
    showWarning: document.getElementById('adminShowWarning').checked,
    autoEnd: document.getElementById('adminAutoEnd').checked,
    warningText: document.getElementById('adminWarningText').value.trim() || '检测到切屏行为（共 {count} 次），请保持专注！'
  };
  localStorage.setItem('beSwitchConfig', JSON.stringify(cfg));'''
new_save = '''function saveAdminConfig() {
  var cfg = {
    allowedCount: parseInt(document.getElementById('adminAllowedCount').value) || 3,
    showWarning: document.getElementById('adminShowWarning').checked,
    autoEnd: document.getElementById('adminAutoEnd').checked,
    warningText: document.getElementById('adminWarningText').value.trim() || '检测到切屏行为（共 {count} 次），请保持专注！',
    maxAttempts: parseInt(document.getElementById('adminMaxAttempts').value) || 2,
    disputeRatio: parseInt(document.getElementById('adminDisputeRatio').value) || 20
  };
  localStorage.setItem('beSwitchConfig', JSON.stringify(cfg));'''
content = content.replace(old_save, new_save)

# Write back
with open('/workspace/BE/English_v1.3.2.html', 'w') as f:
    f.write(content)

print("✅ All patches applied successfully!")
print(f"File size: {len(content)} bytes")

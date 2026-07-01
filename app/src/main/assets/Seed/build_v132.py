with open('/workspace/BE/English_v1.3.2.html', 'r') as f:
    content = f.read()

# 1. State - add attempt tracking
content = content.replace(
    'totalOriginal: 0,\n  switchCount: 0\n};',
    'totalOriginal: 0,\n  switchCount: 0,\n  attemptCount: 0,\n  maxAttempts: 2,\n  lastWrong: null,\n  disputeCount: 0,\n  maxDisputes: 0\n};'
)

# 2. doStartPractice - add init
content = content.replace(
    'state.switchCount = 0;',
    'state.switchCount = 0;\n  state.attemptCount = 0;\n  state.lastWrong = null;\n  state.disputeCount = 0;\n  var scfg = getSwitchConfig();\n  state.maxAttempts = scfg.maxAttempts || 2;\n  state.maxDisputes = Math.max(1, Math.floor(allQuestions.length * (scfg.disputeRatio || 20) / 100));'
)

# 3. submitAnswer - two attempts
old_submit = '''function submitAnswer() {
  if (state.locked) return;
  var input = document.getElementById('answerInput');
  var userAns = input.value.trim();
  var q = state.questions[state.currentIdx];
  var fb = document.getElementById('feedback');

  if (!userAns) {
    fb.textContent = '请输入答案';
    fb.className = 'q-feedback wrong';
    input.focus();
    return;
  }

  var isCorrect = userAns.toLowerCase() === q.answer.toLowerCase();

  if (isCorrect) {
    // 正确 -> 进入下一题
    input.className = 'correct';
    fb.textContent = '正确！';
    fb.className = 'q-feedback correct';
    state.locked = true;
    document.getElementById('btnSubmit').disabled = true;
    document.getElementById('btnDontKnow').disabled = true;
    document.getElementById('kbShift').classList.add('disabled');
    document.querySelectorAll('#keyboard .kb-key[data-key]').forEach(function(k){k.classList.add('disabled')});
    input.disabled = true;
    setTimeout(function() { nextQuestion(); }, 600);
  } else {
    // 错误 -> 记录错误
    state.wrongRecords.push({
      chinese: q.chinese,
      answer: q.answer,
      userInput: userAns,
      index: state.currentIdx,
      isSkip: false
    });
    state.everWrong.add(state.currentIdx);
    state.totalWrongCount++;
    document.getElementById('wrongCountDisplay').textContent = 'X ' + state.totalWrongCount;

    input.className = 'wrong';
    fb.textContent = '不正确';
    fb.className = 'q-feedback wrong';
    input.focus();
  }
}'''
new_submit = '''function submitAnswer() {
  if (state.locked) return;
  var input = document.getElementById('answerInput');
  var userAns = input.value.trim();
  var q = state.questions[state.currentIdx];
  var fb = document.getElementById('feedback');

  if (!userAns) {
    fb.textContent = '请输入答案';
    fb.className = 'q-feedback wrong';
    input.focus();
    return;
  }

  state.attemptCount++;
  var isCorrect = userAns.toLowerCase() === q.answer.toLowerCase();

  if (isCorrect) {
    input.className = 'correct';
    fb.textContent = '正确！';
    fb.className = 'q-feedback correct';
    lockQuestion();
    setTimeout(function() { nextQuestion(); }, 600);
  } else if (state.attemptCount < state.maxAttempts) {
    input.className = 'wrong';
    fb.textContent = '不正确，还有第二次机会';
    fb.className = 'q-feedback wrong';
    input.focus();
  } else {
    state.wrongRecords.push({chinese: q.chinese, answer: q.answer, userInput: userAns, index: state.currentIdx, isSkip: false});
    state.everWrong.add(state.currentIdx);
    state.totalWrongCount++;
    document.getElementById('wrongCountDisplay').textContent = 'X ' + state.totalWrongCount;
    state.lastWrong = {chinese: q.chinese, answer: q.answer, userInput: userAns, index: state.currentIdx};
    input.className = 'wrong';
    fb.textContent = '错误，进入下一题';
    fb.className = 'q-feedback wrong';
    lockQuestion();
    setTimeout(function() { nextQuestion(); }, 800);
  }
}

function lockQuestion() {
  state.locked = true;
  document.getElementById('btnSubmit').disabled = true;
  document.getElementById('btnDontKnow').disabled = true;
  document.getElementById('kbShift').classList.add('disabled');
  document.querySelectorAll('#keyboard .kb-key[data-key]').forEach(function(k){k.classList.add('disabled')});
  document.getElementById('answerInput').disabled = true;
}'''
content = content.replace(old_submit, new_submit)

# 4. confirmSkip - update
content = content.replace(
    'state.totalWrongCount++;\n  nextQuestion();',
    'state.totalWrongCount++;\n  state.attemptCount = state.maxAttempts;\n  document.getElementById(\'wrongCountDisplay\').textContent = \'X \' + state.totalWrongCount;\n  state.lastWrong = {chinese: q.chinese, answer: q.answer, userInput: \'（跳过）\', index: state.currentIdx};\n  lockQuestion();\n  setTimeout(function() { nextQuestion(); }, 400);'
)

# 5. nextQuestion - add dispute banner
content = content.replace(
    '} else {\n    renderQuestion();\n  }',
    '} else {\n    renderQuestion();\n    if (state.lastWrong && state.lastWrong.index === state.currentIdx - 1) { showDisputeBanner(); }\n  }'
)

# 6. finishPractice - grouped wrong list
old_wrong = '''  // 错题列表（每条错误记录单独一行）
  var ws = document.getElementById('wrongSection');
  var wl = document.getElementById('wrongList');
  wl.innerHTML = '';
  if (state.wrongRecords.length > 0) {
    ws.style.display = 'block';
    state.wrongRecords.forEach(function(r) {\n      var div = document.createElement('div');
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

new_wrong = '''  // 错题列表（合并同一题目的多次错误，点击展开）
  var ws = document.getElementById('wrongSection');
  var wl = document.getElementById('wrongList');
  wl.innerHTML = '';
  if (state.wrongRecords.length > 0) {
    ws.style.display = 'block';
    var groups = {};
    state.wrongRecords.forEach(function(r) { if (!groups[r.index]) groups[r.index] = []; groups[r.index].push(r); });
    Object.keys(groups).forEach(function(idx) {
      var attempts = groups[idx];
      var first = attempts[0];
      var gd = document.createElement('div');
      gd.className = 'w-group';
      var badge = attempts.length > 1 ? ' <span style="font-size:11px;color:#888">尝试' + attempts.length + '次</span>' : '';
      gd.innerHTML = '<div class="w-group-header" onclick="this.classList.toggle(\\'expanded\\');this.nextElementSibling.classList.toggle(\\'show\\')">' +
        '<span class="w-g-title">' + escHtml(first.chinese) + ' ' + escHtml(first.answer) + '</span>' + badge +
        '<span class="w-g-arrow">▼</span></div>' +
        '<div class="w-group-body">' +
        attempts.map(function(a, i) { return '<div class="w-attempt"><span class="wa-label">' + (a.isSkip ? '跳过' : '第' + (i+1) + '次') + '</span> ' + escHtml(a.userInput) + '</div>'; }).join('') +
        '</div>';
      wl.appendChild(gd);
    });
  } else { ws.style.display = 'none'; }'''
content = content.replace(old_wrong, new_wrong)

# 7. CSS for group and dispute
old_css_end = '\n</style>'
new_css = '''
/* ===== Expandable Wrong Items ===== */
.w-group{margin-bottom:8px}
.w-group-header{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:var(--sub-bg);border:1px solid var(--border);border-radius:8px;border-left:3px solid #dc3545;cursor:pointer;font-size:13px;user-select:none}
.w-group-header:hover{background:var(--hover-bg)}
.w-group-header .w-g-title{font-weight:600;color:var(--text);flex:1}
.w-group-header .w-g-arrow{font-size:12px;color:#999;transition:transform .2s}
.w-group-header.expanded .w-g-arrow{transform:rotate(180deg)}
.w-group-body{display:none;background:var(--card-bg);border:1px solid var(--border);border-top:none;border-radius:0 0 8px 8px}
.w-group-body.show{display:block}
.w-attempt{padding:8px 14px;font-size:12px;border-bottom:1px solid var(--border)}
.w-attempt:last-child{border-bottom:none}
.w-attempt .wa-label{color:#888;font-size:11px}

/* ===== Dispute Banner ===== */
.dispute-banner{background:#f3e8ff;border:2px solid #6f42c1;border-radius:12px;padding:12px 16px;margin:10px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.dispute-banner .db-text{font-size:13px;color:#4a1d96;line-height:1.5;flex:1;min-width:200px}
.dispute-banner .db-actions{display:flex;gap:6px}

/* ===== Dispute Modal ===== */
.d-status{padding:12px;border-radius:8px;margin:10px 0;font-size:13px;text-align:center}
.d-status.loading{background:#f3e8ff;color:#6f42c1}
.d-status.error{background:#f8d7da;color:#721c24}
'''
content = content.replace(old_css_end, new_css + '\n</style>')

# 8. Dispute banner HTML before keyboard
content = content.replace(
    '  <!-- ===== Virtual Keyboard ===== -->',
    '  <!-- ===== Dispute Banner ===== -->\n  <div class="dispute-banner" id="disputeBanner" style="display:none">\n    <div class="db-text" id="disputeText"></div>\n    <div class="db-actions">\n      <button class="btn btn-outline" onclick="showDisputeModal()" id="btnDispute" style="padding:6px 16px;font-size:12px;border-color:#6f42c1;color:#6f42c1">有异议，申请复核</button>\n      <button class="btn btn-secondary" onclick="hideDisputeBanner()" style="padding:6px 16px;font-size:12px">忽略</button>\n    </div>\n  </div>\n\n  <!-- ===== Virtual Keyboard ===== -->'
)

# 9. Dispute modal HTML before /body
content = content.replace(
    '</body>',
    '<!-- ===== Dispute Modal ===== -->\n<div class="modal-overlay dispute-modal" id="disputeModal">\n  <div class="modal-box">\n    <div class="m-icon">🤔</div>\n    <h3>申请复核</h3>\n    <p style="font-size:13px;color:#666;text-align:center;margin:6px 0">系统将把您的答案提交给AI进行复核</p>\n    <div class="d-status" id="disputeStatus" style="display:none"></div>\n    <div class="q-actions" id="disputeActions">\n      <button class="btn btn-secondary" onclick="closeDisputeModal()">取消</button>\n      <button class="btn btn-primary" onclick="submitDispute()" style="background:#6f42c1">确认复核</button>\n    </div>\n  </div>\n</div>\n\n</body>'
)

# 10. Dispute JS functions before console.log
content = content.replace(
    "console.log('📝 英语默写 loaded');",
    '''// ===== 复核功能 =====
function showDisputeBanner() {
  if (!state.lastWrong || state.disputeCount >= state.maxDisputes) return;
  var b = document.getElementById('disputeBanner');
  document.getElementById('disputeText').textContent = '上一题[' + state.lastWrong.chinese + '] 你答[' + state.lastWrong.userInput + '] 正确[' + state.lastWrong.answer + '] 剩余复核' + (state.maxDisputes - state.disputeCount) + '次';
  b.style.display = 'flex';
}
function hideDisputeBanner() { document.getElementById('disputeBanner').style.display = 'none'; }
function showDisputeModal() {
  document.getElementById('disputeStatus').style.display = 'none';
  document.getElementById('disputeActions').style.display = 'flex';
  document.getElementById('disputeModal').classList.add('show');
}
function closeDisputeModal() { document.getElementById('disputeModal').classList.remove('show'); }
function submitDispute() {
  var st = document.getElementById('disputeStatus');
  var ac = document.getElementById('disputeActions');
  st.style.display = 'block'; st.className = 'd-status loading'; st.textContent = 'AI复核中...';
  ac.style.display = 'none';
  var bu = localStorage.getItem('aiBaseUrl') || 'https://api.openai.com/v1';
  var ak = localStorage.getItem('aiApiKey') || '';
  var md = localStorage.getItem('aiModel') || 'gpt-4o-mini';
  if (!ak) { showDisputeError('请先配置AI API Key'); return; }
  if (bu.endsWith('/')) bu = bu.slice(0, -1);
  if (!bu.endsWith('/v1')) bu += '/v1';
  var prompt = '你是一位英语复核老师。\\n题目：' + state.lastWrong.chinese + '\\n标准答案：' + state.lastWrong.answer + '\\n学生答案：' + state.lastWrong.userInput + '\\n请以JSON回复(is_correct true/false, explanation简短)。忽略大小写和标点后一致或拼写小疏漏但可识别应判正确。';
  fetch(bu + '/chat/completions', {
    method: 'POST',
    headers: {'Content-Type':'application/json','Authorization':'Bearer ' + ak},
    body: JSON.stringify({model: md, messages: [{role:'system', content:'公正的英语复核老师'},{role:'user', content:prompt}], temperature: 0.1, max_tokens: 500})
  }).then(function(r){return r.json();}).then(function(d){
    var c = d.choices?.[0]?.message?.content || '';
    var m = c.match(/{[\\\\s\\\\S]*?}/);
    if (m) {
      var r2 = JSON.parse(m[0]);
      if (r2.is_correct !== undefined) {
        var idx = state.lastWrong.index;
        state.disputeCount++; hideDisputeBanner(); state.lastWrong = null; closeDisputeModal();
        alert('第' + (idx+1) + '题，经复核后确认' + (r2.is_correct ? '正确' : '错误'));
        return;
      }
    }
    showDisputeError('复核程序异常，请保持安静，待测试完成后复核。');
  }).catch(function(e){showDisputeError('复核程序异常，请保持安静，待测试完成后复核。');});
}
function showDisputeError(m) {
  var st = document.getElementById('disputeStatus');
  document.getElementById('disputeActions').style.display = 'flex';
  st.className = 'd-status error'; st.textContent = m;
}
document.getElementById('disputeModal').addEventListener('click', function(e) { if (e.target === this) closeDisputeModal(); });

console.log('📝 英语默写 loaded');'''
)

# 11. Admin panel - add config fields
content = content.replace(
    '切屏提示文字 <span style="font-weight:400;color:var(--sub-text)">（支持 {count} 变量）</span>',
    '切屏提示文字 <span style="font-weight:400;color:var(--sub-text)">（支持 {count} 变量）</span>'
)
# Add new fields after warning text hint
old_hint = '提示中的 {count} 会自动替换为实际切屏次数</div>\n\n    <div class="admin-status"'
new_hint = '提示中的 {count} 会自动替换为实际切屏次数</div>\n\n    <hr style="border:none;border-top:1px solid var(--border);margin:14px 0">\n\n    <label>单题容错次数</label>\n    <input type="number" id="adminMaxAttempts" min="1" max="5" value="2">\n    <div class="admin-hint">每题可答错的次数，第1次错可修改再答，默认2次</div>\n\n    <label>允许复核比例 (%)</label>\n    <input type="number" id="adminDisputeRatio" min="0" max="50" value="20">\n    <div class="admin-hint">每场练习允许申请AI复核的题目比例，默认20%</div>\n\n    <div class="admin-status"'
content = content.replace(old_hint, new_hint)

# 12. getSwitchConfig - add new defaults
content = content.replace(
    "warningText: '检测到切屏行为（共 {count} 次），请保持专注！'};",
    "warningText: '检测到切屏行为（共 {count} 次），请保持专注！', maxAttempts: 2, disputeRatio: 20};"
)

# 13. openAdminPanel - load new fields
content = content.replace(
    "document.getElementById('adminWarningText').value = cfg.warningText;",
    "document.getElementById('adminWarningText').value = cfg.warningText;\n  document.getElementById('adminMaxAttempts').value = cfg.maxAttempts || 2;\n  document.getElementById('adminDisputeRatio').value = cfg.disputeRatio || 20;"
)

# 14. saveAdminConfig - save new fields
content = content.replace(
    "warningText: document.getElementById('adminWarningText').value.trim() || '检测到切屏行为（共 {count} 次），请保持专注！'",
    "warningText: document.getElementById('adminWarningText').value.trim() || '检测到切屏行为（共 {count} 次），请保持专注！',\n    maxAttempts: parseInt(document.getElementById('adminMaxAttempts').value) || 2,\n    disputeRatio: parseInt(document.getElementById('adminDisputeRatio').value) || 20"
)

# 15. Conversion prompt update
content = content.replace(
    '+ \'规则：\\\\n1. 从输入中提取中英文对照信息\\\\n2. chinese填中文，answer填英文\\\\n3. type判断：单词用word，短语用phrase，句子用sentence\\\\n4. 只输出JSON，不要解释\'',
    '+ \'规则：\\\\n1. 从输入中提取中英文对照信息\\\\n2. chinese填中文，answer填英文\\\\n3. type判断：单词用word，短语用phrase，句子用sentence\\\\n4. 只输出JSON，不要解释\\\\n5. 重要：如果句子中包含多段对话（如A:...B:...），请拆分每条对话为独立的question\\\\n6. 重要：如果句子中包含"/"或"或"分隔的不同内容，请拆分为多个独立的question\\\\n7. 每条对话或每个选项作为独立的question，type均设为sentence\''
)

# 16. Integrity promise
content = content.replace(
    '练习过程中已开启<strong>切屏检测</strong>，切换页面将被记录。<br><br>\n      ✅ 诚实练习',
    '练习过程中已开启<strong>切屏检测</strong>，切换页面将被记录。<br><br>\n      <strong>📋 答题规则</strong><br>\n      • 每题有 <strong>2次答题机会</strong>（可在管理面板调整），第一次错误可修改后再次提交<br>\n      • 第二次无论对错均进入下一题<br>\n      • 每场练习允许对 <strong>20% 的题目</strong>申请 AI 复核（可在管理面板调整）<br>\n      • 如对判分有异议，可在下一题页面点击"申请复核"<br><br>\n      ✅ 诚实练习'
)

with open('/workspace/BE/English_v1.3.2.html', 'w') as f:
    f.write(content)

print('Done!')
print(f'Size: {len(content)} bytes')
print()
# Quick verify
for check in ['v1.3.2', 'page active', 'attemptCount', 'maxAttempts', 'dispute-banner', 'submitDispute', 'w-group-header', 'adminMaxAttempts', 'adminDisputeRatio', '多段对话', '2次答题机会']:
    print(f"  {"OK" if check in content else "XX"} {check}")

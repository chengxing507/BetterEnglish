# Build v3.html from v1.3.2.1 base
with open('/workspace/BE/v3.html', 'r') as f:
    c = f.read()

# 0. Update version
c = c.replace('v1.3.2.1', 'v3.0')

# =====================================================
# 1. CSS for hint button, sets manager, retry button
# =====================================================
old_css_end = '}\n\n</style>'
new_css_extra = '''}\n\n/* ===== Hint Button ===== */\n.btn-hint{display:inline-flex;align-items:center;gap:4px;padding:8px 16px;border-radius:10px;border:2px solid #ffc107;background:#fff8e1;color:#856404;font-size:13px;font-weight:600;cursor:pointer;transition:all .15s}\n.btn-hint:hover{background:#ffc107;color:#fff}\n.btn-hint.used{opacity:.5;cursor:not-allowed;border-color:#ccc;background:#f5f5f5;color:#999}\n\n/* ===== Question Sets ===== */\n.sets-section{margin-top:14px}\n.sets-section h3{font-size:14px;margin-bottom:8px;color:#495057}\n.sets-input-row{display:flex;gap:6px;margin-bottom:8px}\n.sets-input-row input{flex:1;padding:8px 12px;border:2px solid var(--border);border-radius:8px;font-size:13px;outline:none;background:var(--input-bg);color:var(--text)}\n.sets-input-row input:focus{border-color:#2d6a4f}\n.sets-input-row button{padding:8px 16px;border:none;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;background:#2d6a4f;color:#fff;white-space:nowrap}\n.set-item{display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:var(--sub-bg);border-radius:8px;margin-bottom:4px;font-size:13px}\n.set-item .set-name{flex:1;cursor:pointer;color:var(--text);font-weight:600}\n.set-item .set-meta{font-size:11px;color:var(--sub-text);margin:0 8px}\n.set-item .set-del{width:24px;height:24px;border:none;background:transparent;color:#ccc;font-size:14px;cursor:pointer;border-radius:50%;transition:all .15s}\n.set-item .set-del:hover{background:#fee;color:#dc3545}\n.sets-empty{text-align:center;color:var(--sub-text);font-size:12px;padding:10px 0}\n</style>'''
c = c.replace(old_css_end, new_css_extra)

# =====================================================
# 2. Add hint button to practice page (after q-actions, before keyboard)
# =====================================================
old_after_actions = '  </div>\n\n  <!-- ===== Virtual Keyboard ===== -->'
new_after_actions = '  </div>\n\n  <div style="text-align:center;margin-bottom:4px">\n    <button class="btn-hint" id="btnHint" onclick="showHint()">💡 提示</button>\n  </div>\n\n  <!-- ===== Virtual Keyboard ===== -->'
c = c.replace(old_after_actions, new_after_actions)

# =====================================================
# 3. Add wrong retry button to result page (after wrong section)
# =====================================================
old_after_wrong = '  <div id="disputeResultSection"></div>\n\n    <div class="ai-section">'
new_after_wrong = '''  <div id="disputeResultSection"></div>

  <div id="retryWrongSection" style="text-align:center;margin:8px 0;display:none">
    <button class="btn btn-outline" onclick="retryWrong()" style="border-color:#dc3545;color:#dc3545;font-size:13px;padding:8px 20px">🔄 重练错题</button>
  </div>

    <div class="ai-section">'''
c = c.replace(old_after_wrong, new_after_wrong)

# =====================================================
# 4. Add question sets to import page (after the import card)
# =====================================================
# Find where the import card ends and the ai-settings begins
old_import_card_end = '''    <button class="btn btn-primary btn-block" id="startBtn" disabled onclick="startPractice()" style="margin-top:14px">开始默写</button>
  </div>

    <div class="ai-settings">'''

new_import_card_end = '''    <button class="btn btn-primary btn-block" id="startBtn" disabled onclick="startPractice()" style="margin-top:14px">开始默写</button>
  </div>

  <!-- ===== 题库管理 ===== -->
  <div class="card sets-section" id="setsSection">
    <h3>📚 题库管理</h3>
    <div class="sets-input-row">
      <input type="text" id="setNameInput" placeholder="输入题库名称保存当前题库">
      <button onclick="saveQuestionSet()">💾 保存</button>
    </div>
    <div id="setList"></div>
  </div>

    <div class="ai-settings">'''
c = c.replace(old_import_card_end, new_import_card_end)

# =====================================================
# 5. Add JS: showHint, retryWrong, sets management
# =====================================================
old_last_console = "console.log('📝 英语默写 loaded');"
new_js_extra = '''// ===== 拼写提示 =====
function showHint() {
  if (state.locked) return;
  var q = state.questions[state.currentIdx];
  var ans = q.answer;
  var first = ans.charAt(0);
  var hint = first;
  for (var i = 1; i < ans.length; i++) {
    hint += ans.charAt(i) === ' ' ? ' ' : '_';
  }
  document.getElementById('feedback').textContent = '💡 提示: ' + hint;
  document.getElementById('feedback').className = 'q-feedback skip';
  var btn = document.getElementById('btnHint');
  btn.textContent = '💡 已提示';
  btn.className = 'btn-hint used';
  btn.disabled = true;
}

// ===== 错题重练 =====
function retryWrong() {
  if (!state.wrongRecords || !state.wrongRecords.length) return;
  // Get unique wrong questions by index
  var unique = [];
  var seen = {};
  state.wrongRecords.forEach(function(r) {
    if (!seen[r.index]) { seen[r.index] = true; unique.push(r); }
  });
  // Build new question list
  var newQuestions = unique.map(function(r) {
    var orig = state.questions[r.index];
    return {chinese: orig.chinese, answer: orig.answer, type: orig.type};
  });
  // Reset state and start
  state.questions = newQuestions;
  state.totalOriginal = newQuestions.length;
  state.currentIdx = 0;
  state.wrongRecords = [];
  state.everWrong = new Set();
  state.totalWrongCount = 0;
  state.startTime = Date.now();
  state.locked = false;
  state.shiftOn = false;
  state.isEarlyEnd = false;
  state.switchCount = 0;
  state.attemptCount = 0;
  state.lastWrong = null;
  state.disputeCount = 0;
  var scfg = getSwitchConfig();
  state.maxAttempts = scfg.maxAttempts || 2;
  state.maxDisputes = Math.max(1, Math.floor(newQuestions.length * (scfg.disputeRatio || 20) / 100));
  document.getElementById('headerSub').textContent = '重练错题 (' + newQuestions.length + '题)';
  showPage('pagePractice');
  renderQuestion();
}

// ===== 题库管理 =====
var questionSets = [];
function loadSets() {
  try { questionSets = JSON.parse(localStorage.getItem('beQuestionSets') || '[]'); } catch(e) { questionSets = []; }
  renderSets();
}
function saveQuestionSet() {
  var name = document.getElementById('setNameInput').value.trim();
  if (!name) return;
  var text = document.getElementById('jsonInput').value.trim();
  if (!text) return;
  var exists = false;
  for (var i = 0; i < questionSets.length; i++) {
    if (questionSets[i].name === name) { questionSets[i].data = text; questionSets[i].date = new Date().toLocaleString('zh-CN'); exists = true; break; }
  }
  if (!exists) questionSets.push({name: name, data: text, date: new Date().toLocaleString('zh-CN')});
  if (questionSets.length > 20) questionSets = questionSets.slice(-20);
  localStorage.setItem('beQuestionSets', JSON.stringify(questionSets));
  document.getElementById('setNameInput').value = '';
  renderSets();
}
function loadQuestionSet(idx) {
  var set = questionSets[idx];
  if (!set) return;
  document.getElementById('jsonInput').value = set.data;
  validateInput();
}
function deleteQuestionSet(idx) {
  questionSets.splice(idx, 1);
  localStorage.setItem('beQuestionSets', JSON.stringify(questionSets));
  renderSets();
}
function renderSets() {
  var list = document.getElementById('setList');
  if (!questionSets.length) { list.innerHTML = '<div class="sets-empty">暂无保存的题库</div>'; return; }
  var html = '';
  for (var i = 0; i < questionSets.length; i++) {
    var s = questionSets[i];
    html += '<div class="set-item"><span class="set-name" onclick="loadQuestionSet(' + i + ')">' + escHtml(s.name) + '</span><span class="set-meta">' + escHtml(s.date) + '</span><button class="set-del" onclick="deleteQuestionSet(' + i + ')">✕</button></div>';
  }
  list.innerHTML = html;
}

// ===== Update renderQuestion to reset hint =====
var origRenderQuestion = renderQuestion.toString();
// Find the end of renderQuestion and add hint reset before the closing }
c = c.replace(
    '  input.onfocus = function(){ this.blur(); };\n}',
    '  input.onfocus = function(){ this.blur(); };\n  // Reset hint button\n  var bh = document.getElementById(\'btnHint\');\n  bh.textContent = \'💡 提示\';\n  bh.className = \'btn-hint\';\n  bh.disabled = false;\n}'
);

// ===== Update finishPractice to show retryWrongSection =====
c = c.replace(
    '  } else { ws.style.display = \\'none\\'; }\n\n  // 复核区',
    '  } else { ws.style.display = \\'none\\'; }\n\n  // Show retry wrong button\n  var rws = document.getElementById(\'retryWrongSection\');\n  rws.style.display = state.wrongRecords.length > 0 ? \'block\' : \'none\';\n\n  // 复核区'
);

console.log('📝 英语默写 loaded');'''

c = c.replace(old_last_console, new_js_extra)

# ===== Load sets on page load =====
c = c.replace(
    'loadAiSettings();',
    'loadAiSettings(); loadSets();'
)

with open('/workspace/BE/v3.html', 'w') as f:
    f.write(c)
print('✅ v3.html built!')
print(f'Size: {len(c)} bytes')
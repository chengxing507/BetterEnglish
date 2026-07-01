with open('/workspace/BE/English_v1.3.2.html', 'r') as f:
    c = f.read()

# 1. Version
c = c.replace('v1.3.2', 'v1.3.2.1')

# 2. Fix submitAnswer - two attempts
old = '''function submitAnswer() {
  if (state.locked) return;
  var input = document.getElementById('answerInput');
  var userAns = input.value.trim();
  var q = state.questions[state.currentIdx];
  var fb = document.getElementById('feedback');

  if (!userAns) {
    fb.textContent = '\u23a0\u00ef\u00b8\u008f \u00e8\u00be\u0093\u00e5\u0085\u00a5\u00e7\u00ad\u0094\u00e6\u00a1\u0088';
    fb.className = 'q-feedback wrong';
    input.focus();
    return;
  }

  var isCorrect = userAns.toLowerCase() === q.answer.toLowerCase();

  if (isCorrect) {
    input.className = 'correct';
    fb.textContent = '\u2705 \u00e6\u00ad\u00a3\u00e7\u00a1\u00ae\u00ef\u00bc\u0081';
    fb.className = 'q-feedback correct';
    state.locked = true;
    document.getElementById('btnSubmit').disabled = true;
    document.getElementById('btnDontKnow').disabled = true;
    document.getElementById('kbShift').classList.add('disabled');
    document.querySelectorAll('#keyboard .kb-key[data-key]').forEach(function(k){k.classList.add('disabled')});
    input.disabled = true;
    setTimeout(function() { nextQuestion(); }, 600);
  } else {
    state.wrongRecords.push({
      chinese: q.chinese,
      answer: q.answer,
      userInput: userAns,
      index: state.currentIdx,
      isSkip: false
    });
    state.everWrong.add(state.currentIdx);
    state.totalWrongCount++;
    document.getElementById('wrongCountDisplay').textContent = '\u274c ' + state.totalWrongCount;

    input.className = 'wrong';
    fb.textContent = '\u274c \u00e4\u00b8\u008d\u00e6\u00ad\u00a3\u00e7\u00a1\u00ae\u00ef\u00bc\u008c\u00e5\u0086\u008d\u00e8\u00af\u0095\u00e8\u00af\u0095';
    fb.className = 'q-feedback wrong';
    input.focus();
  }
}

// ===== \u00e6\u0088\u0091\u00e4\u00b8\u008d\u00e4\u00bc\u009a =====
function showSkipModal() { document.getElementById('skipModal').classList.add('show'); }
function closeSkipModal() { document.getElementById('skipModal').classList.remove('show'); }'''

new = '''function submitAnswer() {
  if (state.locked) return;
  var input = document.getElementById('answerInput');
  var userAns = input.value.trim();
  var q = state.questions[state.currentIdx];
  var fb = document.getElementById('feedback');
  if (!userAns) { fb.textContent = '请输入答案'; fb.className = 'q-feedback wrong'; input.focus(); return; }
  state.attemptCount++;
  var isCorrect = userAns.toLowerCase() === q.answer.toLowerCase();
  if (isCorrect) {
    input.className = 'correct'; fb.textContent = '正确！'; fb.className = 'q-feedback correct';
    lockQuestion(); setTimeout(function() { nextQuestion(); }, 600);
  } else if (state.attemptCount < state.maxAttempts) {
    input.className = 'wrong'; fb.textContent = '不正确，还有第二次机会'; fb.className = 'q-feedback wrong'; input.focus();
  } else {
    state.wrongRecords.push({chinese:q.chinese, answer:q.answer, userInput:userAns, index:state.currentIdx, isSkip:false});
    state.everWrong.add(state.currentIdx); state.totalWrongCount++;
    updateWrongDisplay();
    state.lastWrong = {chinese:q.chinese, answer:q.answer, userInput:userAns, index:state.currentIdx};
    input.className = 'wrong'; fb.textContent = '错误，进入下一题'; fb.className = 'q-feedback wrong';
    lockQuestion(); setTimeout(function() { nextQuestion(); }, 800);
  }
}

function lockQuestion() {
  state.locked = true;
  document.getElementById('btnSubmit').disabled = true; document.getElementById('btnDontKnow').disabled = true;
  document.getElementById('kbShift').classList.add('disabled');
  document.querySelectorAll('#keyboard .kb-key[data-key]').forEach(function(k){k.classList.add('disabled')});
  document.getElementById('answerInput').disabled = true;
}

function updateWrongDisplay() {
  document.getElementById('wrongCountDisplay').textContent = 'X ' + state.everWrong.size;
}

// ===== 我不会 =====
function showSkipModal() { document.getElementById('skipModal').classList.add('show'); }
function closeSkipModal() { document.getElementById('skipModal').classList.remove('show'); }'''
c = c.replace(old, new)

# 3. Fix confirmSkip
old2 = '''function confirmSkip() {
  closeSkipModal();
  var q = state.questions[state.currentIdx];
  state.wrongRecords.push({
    chinese: q.chinese,
    answer: q.answer,
    userInput: '（跳过）',
    index: state.currentIdx,
    isSkip: true
  });
  state.everWrong.add(state.currentIdx);
  state.totalWrongCount++;
  state.attemptCount = state.maxAttempts;
  document.getElementById('wrongCountDisplay').textContent = 'X ' + state.totalWrongCount;
  state.lastWrong = {
    chinese: q.chinese,
    answer: q.answer,
    userInput: '（跳过）',
    index: state.currentIdx
  };
  lockQuestion();
  setTimeout(function() { nextQuestion(); }, 400);
}'''

new2 = '''function confirmSkip() {
  closeSkipModal();
  var q = state.questions[state.currentIdx];
  if (state.everWrong.has(state.currentIdx)) { lockQuestion(); setTimeout(function() { nextQuestion(); }, 400); return; }
  state.wrongRecords.push({chinese:q.chinese, answer:q.answer, userInput:'（跳过）', index:state.currentIdx, isSkip:true});
  state.everWrong.add(state.currentIdx); state.totalWrongCount++;
  state.attemptCount = state.maxAttempts; updateWrongDisplay();
  state.lastWrong = {chinese:q.chinese, answer:q.answer, userInput:'（跳过）', index:state.currentIdx};
  lockQuestion(); setTimeout(function() { nextQuestion(); }, 400);
}'''
c = c.replace(old2, new2)

# 4. Fix wrong count display in renderQuestion
c = c.replace("document.getElementById('wrongCountDisplay').textContent = 'X ' + state.totalWrongCount;", "updateWrongDisplay();")

# 5. Fix submitDispute - proper error reporting
old3 = '''function submitDispute() {
  var st = document.getElementById('disputeStatus');
  var ac = document.getElementById('disputeActions');
  st.style.display = 'block'; st.className = 'd-status loading'; st.textContent = 'AI复核中...';
  ac.style.display = 'none';
  var bu = localStorage.getItem('aiBaseUrl') || 'https://api.openai.com/v1';
  var ak = localStorage.getItem('aiApiKey') || '';
  var md = localStorage.getItem('aiModel') || 'gpt-4o-mini';
  if (state.disputeCount >= state.maxDisputes) { showDisputeError('复核次数已用尽'); return; }
  if (!ak) { showDisputeError('请先配置AI API Key'); return; }
  if (bu.endsWith('/')) bu = bu.slice(0, -1);
  if (!bu.endsWith('/v1')) bu += '/v1';
  var prompt = '你是一位英语复核老师。\\n题目：' + state._disputeTarget.chinese + '\\n标准答案：' + state._disputeTarget.answer + '\\n学生答案：' + state._disputeTarget.userInput + '\\n请以JSON回复(is_correct true/false, explanation简短)。忽略大小写和标点后一致或拼写小疏漏但可识别应判正确。';
  fetch(bu + '/chat/completions', {
    method: 'POST',
    headers: {'Content-Type':'application/json','Authorization':'Bearer ' + ak},
    body: JSON.stringify({model: md, messages: [{role:'system', content:'公正的英语复核老师'},{role:'user', content:prompt}], temperature: 0.1, max_tokens: 500})
  }).then(function(r){return r.json();}).then(function(d){
    var c = d.choices?.[0]?.message?.content || '';
    var m = c.match(/{[\\s\\S]*?}/);
    if (m) {
      var r2 = JSON.parse(m[0]);
      if (r2.is_correct !== undefined) {
        var idx = state._disputeTarget.index;
        state.disputeCount++; state._disputeTarget = null; closeDisputeModal();
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
}'''

new3 = '''function submitDispute() {
  var st = document.getElementById('disputeStatus');
  var ac = document.getElementById('disputeActions');
  st.style.display = 'block'; st.className = 'd-status loading'; st.textContent = 'AI复核中...';
  ac.style.display = 'none';
  var bu = localStorage.getItem('aiBaseUrl') || 'https://api.openai.com/v1';
  var ak = localStorage.getItem('aiApiKey') || '';
  var md = localStorage.getItem('aiModel') || 'gpt-4o-mini';
  if (state.disputeCount >= state.maxDisputes) { showDisputeError('复核次数已用尽'); return; }
  if (!ak) { showDisputeError('请先配置AI API Key'); return; }
  if (bu.endsWith('/')) bu = bu.slice(0, -1);
  if (!bu.endsWith('/v1')) bu += '/v1';
  var prompt = '你是一位英语复核老师。题目：' + state._disputeTarget.chinese + ' 标准答案：' + state._disputeTarget.answer + ' 学生答案：' + state._disputeTarget.userInput + ' 请只输出JSON：{"is_correct":true或false,"explanation":"简短说明"}。';
  fetch(bu + '/chat/completions', {
    method: 'POST',
    headers: {'Content-Type':'application/json','Authorization':'Bearer ' + ak},
    body: JSON.stringify({model: md, messages: [{role:'system', content:'你只输出JSON，不输出其他内容。'},{role:'user', content:prompt}], temperature: 0.1, max_tokens: 500})
  }).then(function(r){return r.json();}).then(function(d){
    if (d.error) { showDisputeError('API错误: ' + (d.error.message || JSON.stringify(d.error))); return; }
    var txt = d.choices?.[0]?.message?.content || '';
    var match = txt.match(/{[\\s\\S]*?}/);
    if (match) {
      try {
        var result = JSON.parse(match[0]);
        if (result.is_correct !== undefined) {
          var idx = state._disputeTarget.index;
          state.disputeCount++; state._disputeTarget = null; closeDisputeModal();
          alert('第' + (idx+1) + '题，经复核后确认' + (result.is_correct ? '正确' : '错误'));
          return;
        }
      } catch(e) {}
    }
    showDisputeError('AI回复格式异常: ' + txt.substring(0, 200));
  }).catch(function(e){showDisputeError('网络错误: ' + e.message);});
}

function showDisputeError(m) {
  var st = document.getElementById('disputeStatus');
  document.getElementById('disputeActions').style.display = 'flex';
  st.className = 'd-status error'; st.textContent = m;
}'''
c = c.replace(old3, new3)

# 6. Fix wrong count display in finishPractice
c = c.replace("document.getElementById('statWrong').textContent = wrongCount;", "document.getElementById('statWrong').textContent = state.everWrong.size;")

# 7. Add AI connectivity test to admin panel
c = c.replace(
    '<div class="admin-actions">\n      <button class="btn btn-secondary" onclick="closeAdminPanel()">关闭</button>\n      <button class="btn btn-primary" onclick="saveAdminConfig()">保存设置</button>\n    </div>',
    '<div class="admin-actions">\n      <button class="btn btn-secondary" onclick="closeAdminPanel()">关闭</button>\n      <button class="btn btn-primary" onclick="saveAdminConfig()">保存设置</button>\n    </div>\n    <div class="admin-check" style="margin-top:14px">\n      <button class="btn btn-outline" onclick="testAIConnection()" style="padding:8px 16px;font-size:12px;border-color:#6f42c1;color:#6f42c1">AI连通性检查</button>\n    </div>\n    <div id="aiTestResult" style="font-size:12px;margin-top:8px;min-height:20px;text-align:center"></div>'
)

# 8. Add testAIConnection function
c = c.replace(
    "console.log('📝 英语默写 loaded');",
    '''// ===== AI连通性检查 =====
function testAIConnection() {
  var r = document.getElementById('aiTestResult');
  r.innerHTML = '测试中...'; r.style.color = '#6f42c1';
  var bu = localStorage.getItem('aiBaseUrl') || 'https://api.openai.com/v1';
  var ak = localStorage.getItem('aiApiKey') || '';
  var md = localStorage.getItem('aiModel') || 'gpt-4o-mini';
  if (!ak) { r.innerHTML = '请先配置API Key'; r.style.color = '#dc3545'; return; }
  if (bu.endsWith('/')) bu = bu.slice(0, -1);
  if (!bu.endsWith('/v1')) bu += '/v1';
  var ok1 = false, ok2 = false;
  var t1 = fetch(bu + '/chat/completions', {
    method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+ak},
    body:JSON.stringify({model:md, messages:[{role:'user', content:'用5个字说：天气很好'}], temperature:0.1, max_tokens:50})
  }).then(function(r){return r.json();}).then(function(d){
    if(d.choices?.[0]?.message?.content) ok1 = true;
    else { r.innerHTML='总结测试失败'; r.style.color='#dc3545'; }
  }).catch(function(e){r.innerHTML='总结测试失败: '+e.message; r.style.color='#dc3545';});
  var t2 = fetch(bu + '/chat/completions', {
    method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+ak},
    body:JSON.stringify({model:md, messages:[{role:'user', content:'只输出JSON: {"is_correct":true}'}], temperature:0.1, max_tokens:100})
  }).then(function(r){return r.json();}).then(function(d){
    var txt = d.choices?.[0]?.message?.content || '';
    if(txt.indexOf('is_correct')>=0) ok2 = true;
    else { r.innerHTML='复核测试失败: AI未输出JSON'; r.style.color='#dc3545'; }
  }).catch(function(e){r.innerHTML='复核测试失败: '+e.message; r.style.color='#dc3545';});
  Promise.all([t1, t2]).then(function() {
    if(ok1 && ok2) r.innerHTML = '总结和复核均可正常使用'; r.style.color = '#28a745';
    if(ok1 && !ok2) r.innerHTML = '总结可用，复核异常。AI模型可能不支持JSON输出'; r.style.color = '#856404';
    if(!ok1 && ok2) r.innerHTML = '复核可用，总结异常。AI模型可能有问题'; r.style.color = '#856404';
  });
}

console.log('📝 英语默写 loaded');'''
)

with open('/workspace/BE/English_v1.3.2.1.html', 'w') as f:
    f.write(c)

print('Done! v1.3.2.1 generated')
print(f'Size: {len(c)} bytes')

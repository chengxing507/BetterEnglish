with open('/workspace/BE/English_v1.3.2.html', 'r') as f:
    c = f.read()

# 1. Remove dispute banner div from practice page
old_b = '  <!-- ===== Dispute Banner ===== -->\n  <div class="dispute-banner" id="disputeBanner" style="display:none">\n    <div class="db-text" id="disputeText"></div>\n    <div class="db-actions">\n      <button class="btn btn-outline" onclick="showDisputeModal()" id="btnDispute" style="padding:6px 16px;font-size:12px;border-color:#6f42c1;color:#6f42c1">有异议，申请复核</button>\n      <button class="btn btn-secondary" onclick="hideDisputeBanner()" style="padding:6px 16px;font-size:12px">忽略</button>\n    </div>\n  </div>\n\n  <!-- ===== Virtual Keyboard ===== -->'
new_b = '  <!-- ===== Virtual Keyboard ===== -->'
c = c.replace(old_b, new_b)

# 2. Remove showDisputeBanner call
c = c.replace('    if (state.lastWrong && state.lastWrong.index === state.currentIdx - 1) { showDisputeBanner(); }\n', '')

# 3. Update wrong list - add dispute button
old_wl = '''      gd.innerHTML = '<div class="w-group-header" onclick="this.classList.toggle(\\'expanded\\');this.nextElementSibling.classList.toggle(\\'show\\')">' +
        '<span class="w-g-title">' + escHtml(first.chinese) + ' ' + escHtml(first.answer) + '</span>' + badge +
        '<span class="w-g-arrow">▼</span></div>' +
        '<div class="w-group-body">' +
        attempts.map(function(a, i) { return '<div class="w-attempt"><span class="wa-label">' + (a.isSkip ? '跳过' : '第' + (i+1) + '次') + '</span> ' + escHtml(a.userInput) + '</div>'; }).join('') +
        '</div>';'''

new_wl = '''      gd.innerHTML = '<div class="w-group-header">' +
        '<span class="w-g-title">' + escHtml(first.chinese) + ' ' + escHtml(first.answer) + '</span>' + badge +
        '<span class="w-g-arrow" style="font-size:11px;cursor:pointer" onclick="this.parentElement.classList.toggle(\\'expanded\\');this.parentElement.nextElementSibling.classList.toggle(\\'show\\')">▼</span></div>' +
        '<div class="w-group-body">' +
        attempts.map(function(a, i) { return '<div class="w-attempt"><span class="wa-label">' + (a.isSkip ? '跳过' : '第' + (i+1) + '次') + '</span> ' + escHtml(a.userInput) + '</div>'; }).join('') +
        '</div>';'''
c = c.replace(old_wl, new_wl)

# 4. Add dispute button after wrong list section (before saveHistory)
# We need to add a dispute section after the wrong list
old_after_wrong = '  } else { ws.style.display = \'none\'; }\n\n  // 保存到历史'
new_after_wrong = '''  } else { ws.style.display = 'none'; }

  // 复核区
  var disputeSection = document.getElementById('disputeResultSection');
  if (disputeSection) {
    disputeSection.innerHTML = '';
    if (state.wrongRecords.length > 0 && state.disputeCount < state.maxDisputes) {
      var dTitle = document.createElement('h3');
      dTitle.textContent = '复核（剩余' + (state.maxDisputes - state.disputeCount) + '次）';
      dTitle.style.cssText = 'font-size:14px;margin-bottom:8px;color:#6f42c1';
      disputeSection.appendChild(dTitle);
      Object.keys(groups).forEach(function(idx) {
        var first = groups[idx][0];
        var btn = document.createElement('button');
        btn.className = 'btn btn-sm';
        btn.style.cssText = 'border:none;padding:6px 12px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;background:#f3e8ff;color:#6f42c1;margin:0 6px 6px 0';
        btn.textContent = first.chinese + ' 复核';
        btn.onclick = function() { prepareDispute(idx); };
        disputeSection.appendChild(btn);
      });
    }
  }

  // 保存到历史'''
c = c.replace(old_after_wrong, new_after_wrong)

# 5. Replace old functions
old_funcs = '''function showDisputeBanner() {
  if (!state.lastWrong || state.disputeCount >= state.maxDisputes) return;
  var b = document.getElementById('disputeBanner');
  document.getElementById('disputeText').textContent = '上一题[' + state.lastWrong.chinese + '] 你答[' + state.lastWrong.userInput + '] 正确[' + state.lastWrong.answer + '] 剩余复核' + (state.maxDisputes - state.disputeCount) + '次';
  b.style.display = 'flex';
}
function hideDisputeBanner() { document.getElementById('disputeBanner').style.display = 'none'; }'''

new_funcs = '''function prepareDispute(idx) {
  var first = null;
  for (var i = 0; i < state.wrongRecords.length; i++) {
    if (state.wrongRecords[i].index == idx) { first = state.wrongRecords[i]; break; }
  }
  if (!first) return;
  state._disputeTarget = {chinese: first.chinese, answer: first.answer, userInput: first.userInput, index: parseInt(idx)};
  showDisputeModal();
}'''
c = c.replace(old_funcs, new_funcs)

# 6. Update submitDispute to use _disputeTarget
c = c.replace("var prompt = '你是一位英语复核老师。\\n题目：' + state.lastWrong.chinese + '\\n标准答案：' + state.lastWrong.answer + '\\n学生答案：' + state.lastWrong.userInput + '\\n请以JSON回复(is_correct true/false, explanation简短)。忽略大小写和标点后一致或拼写小疏漏但可识别应判正确。';",
              "var prompt = '你是一位英语复核老师。\\n题目：' + state._disputeTarget.chinese + '\\n标准答案：' + state._disputeTarget.answer + '\\n学生答案：' + state._disputeTarget.userInput + '\\n请以JSON回复(is_correct true/false, explanation简短)。忽略大小写和标点后一致或拼写小疏漏但可识别应判正确。';")
c = c.replace('var idx = state.lastWrong.index;', 'var idx = state._disputeTarget.index;')
c = c.replace("state.disputeCount++; hideDisputeBanner(); state.lastWrong = null; closeDisputeModal();",
              "state.disputeCount++; state._disputeTarget = null; closeDisputeModal();")

# 7. Add dispute quota check
c = c.replace("if (!ak) { showDisputeError('请先配置AI API Key'); return; }",
              "if (state.disputeCount >= state.maxDisputes) { showDisputeError('复核次数已用尽'); return; }\n  if (!ak) { showDisputeError('请先配置AI API Key'); return; }")

# 8. Clean up unused CSS
c = c.replace('\n/* ===== Dispute Banner ===== */\n.dispute-banner{background:#f3e8ff;border:2px solid #6f42c1;border-radius:12px;padding:12px 16px;margin:10px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}\n.dispute-banner .db-text{font-size:13px;color:#4a1d96;line-height:1.5;flex:1;min-width:200px}\n.dispute-banner .db-actions{display:flex;gap:6px}\n\n', '\n')

# 9. Add dispute result section HTML after wrong section in result page
old_result_html = '  <div class="r-wrong" id="wrongSection" style="display:none">\n    <h3>📝 错题回顾</h3>\n    <div class="w-list" id="wrongList"></div>\n  </div>'
new_result_html = '  <div class="r-wrong" id="wrongSection" style="display:none">\n    <h3>📝 错题回顾</h3>\n    <div class="w-list" id="wrongList"></div>\n  </div>\n\n  <div id="disputeResultSection"></div>'
c = c.replace(old_result_html, new_result_html)

with open('/workspace/BE/English_v1.3.2.html', 'w') as f:
    f.write(c)
print('Done!')

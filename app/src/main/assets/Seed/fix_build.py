with open('/workspace/BE/build_v1321.py', 'r') as f:
    content = f.read()

# Fix 1: showDisputeError section
content = content.replace(
    'function showDisputeError(m) {\n  st documentdispute  document.getElementById(\'disputestyle.display \'flex\';\n stName = \'-status error\'; =}',
    'function showDisputeError(m) {\n  var st = document.getElementById(\'disputeStatus\');\n  document.getElementById(\'disputeActions\').style.display = \'flex\';\n  st.className = \'d-status error\'; st.textContent = \'复核失败: \' + m;\n}'
)

# Fix 2: admin_actions section
content = content.replace(
    '<div class="admin-check" style="margin-top:14px">\n      <button class="btn btn-outline" onclickAIConnection()":8px px;font-size:12px;width:border-color:#6f42c;color6f42c">AI性检查button>\n    </div>\n    <="Test" style="-size:12pxmargin-top:8px;min-height:20px;text-align:center"></div>',
    '<div class="admin-check" style="margin-top:14px">\n      <button class="btn btn-outline" onclick="testAIConnection()" style="padding:8px 16px;font-size:12px;border-color:#6f42c1;color:#6f42c1">AI连通性检查</button>\n    </div>\n    <div id="aiTestResult" style="font-size:12px;margin-top:8px;min-height:20px;text-align:center"></div>'
)

# Fix 3: testAI function variable definition
content = content.replace(
    'old_console = "console.log(\'\\U0001f4dduf1\\u89\\u5199\');_ =functionAIConnection() {',
    'test_ai = \'\'\'// ===== AI连通性检查 =====\nfunction testAIConnection() {'
)

# Fix 4: Fix the old_console replacement
content = content.replace(
    "old_console = 'console.log('''",
    "old_console = 'console.log('[0:0]  # dummy"
)

# Fix 5: Fix the ending of test_ai
old_end_test = '  }).catch(function(e){ r.innerHTML = \'复核测试失败: \'+e.message; r.style.color=\'#dc3545\'; });\n  Promise.all([summaryTest, disputeTest]).then(function() {\n    if (summaryOk && disputeOk) { r.innerHTML = \'总结和复核均可正常使用\'; r.style.color = \'#28a745\'; }\n    else if (summaryOk) { r.innerHTML = \'总结可用，复核异常。请检查AI模型是否支持JSON输出\'; r.style.color = \'#856404\'; }\n    else if (disputeOk) { r.innerHTML = \'复核可用，总结异常。请检查AI模型\'; r.style.color = \'#856404\'; }\n  });\n}\n\nconsole.log(\'📝 英语默写 loaded\');'

new_end_test = '''  }).catch(function(e){ r.innerHTML = '复核测试失败: '+e.message; r.style.color='#dc3545'; });
  Promise.all([summaryTest, disputeTest]).then(function() {
    if (summaryOk && disputeOk) { r.innerHTML = '总结和复核均可正常使用'; r.style.color = '#28a745'; }
    else if (summaryOk) { r.innerHTML = '总结可用，复核异常。请检查AI模型是否支持JSON输出'; r.style.color = '#856404'; }
    else if (disputeOk) { r.innerHTML = '复核可用，总结异常。请检查AI模型'; r.style.color = '#856404'; }
  });
}

console.log('英语默写 loaded');'''

content = content.replace(old_end_test, new_end_test)

with open('/workspace/BE/build_v1321.py', 'w') as f:
    f.write(content)
print('build_v1321.py fixed!')
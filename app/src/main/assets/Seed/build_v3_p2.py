with open('/workspace/BE/v3.html', 'r') as f:
    c = f.read()

# 1. Add correct count display next to wrong count in practice header
c = c.replace(
    '<span id="wrongCountDisplay">X 0</span>',
    '<span id="wrongCountDisplay">X 0</span>\n    <span id="correctCountDisplay" style="color:#28a745;margin-left:10px">V 0</span>'
)

# 2. Update renderQuestion to show correct count
c = c.replace(
    "updateWrongDisplay();\n  var badge",
    "updateWrongDisplay(); updateCorrectDisplay();\n  var badge"
)

# 3. Add updateCorrectDisplay function
c = c.replace(
    "function updateWrongDisplay() {",
    "function updateCorrectDisplay() {\n  var answered = state.currentIdx;\n  var correct = answered - state.everWrong.size;\n  document.getElementById('correctCountDisplay').textContent = 'V ' + (correct >= 0 ? correct : 0);\n}\n\nfunction updateWrongDisplay() {"
)

# 4. Also update in nextQuestion flow
c = c.replace(
    "updateWrongDisplay();\n  state.lastWrong",
    "updateWrongDisplay(); updateCorrectDisplay();\n  state.lastWrong"
)

# 5. Update validateInput to also show text parse info
c = c.replace(
    "var modeStr = '';",
    "var infoStr = '';\n  if (text.indexOf('\\n') >= 0 && !text.trim().startsWith('[') && !text.trim().startsWith('{')) infoStr = ' | 文本模式';\n  var modeStr = '';"
)

# 6. Update the preview text to show text mode
c = c.replace(
    "$importPreview.textContent = '✅ ' + result.questions.length + ' 题 | 单词 ' + types.word + ' 词组 ' + types.phrase + ' 句子 ' + types.sentence + modeStr;",
    "$importPreview.textContent = '✅ ' + result.questions.length + ' 题 | 单词 ' + types.word + ' 词组 ' + types.phrase + ' 句子 ' + types.sentence + infoStr + modeStr;"
)

# 7. Add text import instruction to placeholder
c = c.replace(
    "placeholder='粘贴 JSON 数据...&#10;&#10;示例:&#10;[{\"chinese\":\"苹果\",\"answer\":\"apple\"}]'",
    "placeholder='粘贴 JSON 或 文本 (每行 中文 英文)...&#10;&#10;示例:&#10;苹果 apple&#10;书 book&#10;老师 teacher'"
)

# 8. Improve parseJson to handle plain text format
old = """function parseJson(text) {
  text = text.trim();
  var data = JSON.parse(text);
  var list = [];
  var title = '';
  if (Array.isArray(data)) { list = data; }
  else if (data && typeof data === 'object') {
    if (data.title) title = data.title;
    list = data.questions || data.list || [];
    if (!Array.isArray(list) && data.chinese && data.answer) list = [data];
  }
  if (!list.length) throw new Error('未找到有效题目');"""

new = """function parseJson(text) {
  var txt = text.trim();
  // Try plain text format first
  var lines = txt.split('\\n');
  var found = [];
  var ttl = '';
  for (var i = 0; i < lines.length; i++) {
    var l = lines[i].trim();
    if (!l) continue;
    if (l.startsWith('#') || l.startsWith('【') || l.startsWith('标题')) { ttl = l.replace(/^[#\\[【标题\\]:]+/, '').trim(); continue; }
    // Try "中文 英文"  or "中文-英文"
    var parts = l.match(/^([\\u4e00-\\u9fff\\u3400-\\u4dbf\\u3000-\\u303f]+)[\\s\\t\\-]+(.+)$/);
    if (parts) { found.push({chinese:parts[1].trim(), answer:parts[2].trim(), type:'word'}); continue; }
    // Try "英文 中文"
    parts = l.match(/^([a-zA-Z][a-zA-Z\\s\\']*)[\\s\\t\\-]+([\\u4e00-\\u9fff].+)$/);
    if (parts) { found.push({chinese:parts[2].trim(), answer:parts[1].trim(), type:'word'}); continue; }
  }
  if (found.length > 0) return {questions: found, title: ttl};

  var data = JSON.parse(txt);
  var list = [];
  var title = '';
  if (Array.isArray(data)) { list = data; }
  else if (data && typeof data === 'object') {
    if (data.title) title = data.title;
    list = data.questions || data.list || [];
    if (!Array.isArray(list) && data.chinese && data.answer) list = [data];
  }
  if (!list.length) throw new Error('未找到有效题目');"""

c = c.replace(old, new)

with open('/workspace/BE/v3.html', 'w') as f:
    f.write(c)
print('Done! ' + str(len(c)) + ' bytes')

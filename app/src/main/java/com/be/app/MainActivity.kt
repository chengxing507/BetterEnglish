package com.be.app

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.net.wifi.WifiManager
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.InetAddress
import java.net.NetworkInterface
import java.net.ServerSocket
import java.net.Socket
import java.net.URLEncoder
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var uploadCallback: ValueCallback<Array<Uri>>? = null
    private var httpServer: SimpleHttpServer? = null

    // 线程安全的状态快照，供 HTTP 服务器读取
    @Volatile
    private var snapshot: String = "{}"

    /** 供 HTTP 服务器读取快照 */
    fun getSnapshot(): String = snapshot

    // Activity Result API：文件选择器
    private val fileChooserLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        val uris = if (result.resultCode == RESULT_OK && result.data != null) {
            val data = result.data
            data?.data?.let { arrayOf(it) }
                ?: data?.clipData?.let { clip ->
                    (0 until clip.itemCount).map { clip.getItemAt(it).uri }.toTypedArray()
                }
        } else null
        uploadCallback?.onReceiveValue(uris)
        uploadCallback = null
    }

    // ============ JavaScript 桥接 ============
    inner class BEJsBridge {
        @JavascriptInterface
        fun updateSnapshot(json: String) {
            snapshot = json
        }

        @JavascriptInterface
        fun startServer(port: Int): String {
            try {
                httpServer?.stop()
                val server = SimpleHttpServer(port, this@MainActivity)
                server.start()
                httpServer = server
                return "OK:$port"
            } catch (e: Exception) {
                return "ERR:${e.message}"
            }
        }

        @JavascriptInterface
        fun stopServer() {
            httpServer?.stop()
            httpServer = null
        }

        @JavascriptInterface
        fun getLocalIp(): String {
            return getLocalIpAddress()
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            setSupportZoom(true)
            builtInZoomControls = true
            displayZoomControls = false
            loadWithOverviewMode = true
            useWideViewPort = true
            allowFileAccessFromFileURLs = true
            allowUniversalAccessFromFileURLs = true
            cacheMode = android.webkit.WebSettings.LOAD_DEFAULT
            // 允许混合内容（HTTP 服务器是纯文本，但这里不影响）
            mixedContentMode = android.webkit.WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }

        // 注册 JS 桥接
        webView.addJavascriptInterface(BEJsBridge(), "BEAndroid")

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                return false
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                this@MainActivity.uploadCallback?.onReceiveValue(null)
                this@MainActivity.uploadCallback = filePathCallback
                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                }
                try {
                    fileChooserLauncher.launch(Intent.createChooser(intent, "选择JSON文件"))
                } catch (e: Exception) {
                    this@MainActivity.uploadCallback?.onReceiveValue(null)
                    this@MainActivity.uploadCallback = null
                    return false
                }
                return true
            }
        }

        webView.loadUrl("file:///android_asset/English_v1.4.4.html")
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        httpServer?.stop()
        super.onDestroy()
    }

    /** 获取本机局域网 IP */
    private fun getLocalIpAddress(): String {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val networkInterface = interfaces.nextElement()
                if (networkInterface.isLoopback || !networkInterface.isUp) continue
                val name = networkInterface.name ?: ""
                // 优先 Wi-Fi 接口
                if (!name.contains("wlan", ignoreCase = true) &&
                    !name.contains("eth", ignoreCase = true)) continue
                val addresses = networkInterface.inetAddresses
                while (addresses.hasMoreElements()) {
                    val addr = addresses.nextElement()
                    if (addr is InetAddress && !addr.isLoopbackAddress &&
                        addr.hostAddress?.contains('.') == true) {
                        return addr.hostAddress ?: "未知"
                    }
                }
            }
            // 兜底：取第一个非回环 IPv4
            val allIfs = NetworkInterface.getNetworkInterfaces()
            while (allIfs.hasMoreElements()) {
                val ni = allIfs.nextElement()
                val addrs = ni.inetAddresses
                while (addrs.hasMoreElements()) {
                    val addr = addrs.nextElement()
                    if (addr is InetAddress && !addr.isLoopbackAddress &&
                        addr.hostAddress?.contains('.') == true) {
                        return addr.hostAddress ?: "未知"
                    }
                }
            }
        } catch (e: Exception) {
            return "获取失败"
        }
        return "未知"
    }
}

// ============ 简易 HTTP 服务器 ============
class SimpleHttpServer(
    private val port: Int,
    private val activity: MainActivity
) {
    private var serverSocket: ServerSocket? = null
    @Volatile
    private var running = false

    fun start() {
        running = true
        thread(name = "LanMonitorServer") {
            try {
                serverSocket = ServerSocket(port)
                while (running) {
                    try {
                        val client = serverSocket?.accept() ?: break
                        thread(name = "LanMonitorHandler") {
                            try {
                                handleClient(client)
                            } catch (_: Exception) {
                            } finally {
                                try { client.close() } catch (_: Exception) {}
                            }
                        }
                    } catch (_: Exception) {
                        if (!running) break
                    }
                }
            } catch (e: Exception) {
                android.util.Log.e("LanMonitor", "Server error: ${e.message}")
            }
        }
    }

    fun stop() {
        running = false
        try { serverSocket?.close() } catch (_: Exception) {}
        serverSocket = null
    }

    private fun handleClient(client: Socket) {
        val reader = BufferedReader(InputStreamReader(client.inputStream))
        val requestLine = reader.readLine() ?: return
        // 只支持 GET
        if (!requestLine.startsWith("GET")) return

        // 读取请求头
        var line = reader.readLine()
        while (line != null && line.isNotEmpty()) {
            line = reader.readLine()
        }

        // 读取当前快照
        val json = activity.getSnapshot()
        val body = buildStatusPage(json)
        val response = """
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: ${body.toByteArray().size}
Connection: close
Access-Control-Allow-Origin: *

$body
""".trimIndent()

        client.outputStream.write(response.toByteArray(Charsets.UTF_8))
        client.outputStream.flush()
    }

    private fun buildStatusPage(json: String): String {
        // 对 JSON 做 JS 安全转义（仅转义 </script> 即可），不做 HTML 转义因为是在 <script> 里
        val safeJson = json.replace("</script>", "<\\/script>")

        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>英语默写 · 实时监看</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}
.container{max-width:600px;width:100%;padding:24px;text-align:center}
h1{font-size:22px;margin-bottom:4px;color:#f1f5f9}
.sub{font-size:13px;color:#94a3b8;margin-bottom:24px}
.status-card{background:#1e293b;border-radius:16px;padding:28px 24px;margin-bottom:16px;border:1px solid #334155}
.status-icon{font-size:48px;margin-bottom:8px}
.status-title{font-size:18px;font-weight:700;margin-bottom:4px}
.status-detail{font-size:14px;color:#94a3b8;margin-bottom:16px}
.progress-bar{height:8px;background:#334155;border-radius:4px;overflow:hidden;margin-bottom:20px}
.progress-fill{height:100%;background:linear-gradient(90deg,#3b82f6,#8b5cf6);border-radius:4px;transition:width .8s ease;width:0%}
.stats-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:16px}
.stat-item{background:#0f172a;border-radius:10px;padding:14px 8px}
.stat-val{font-size:24px;font-weight:700}
.stat-val.green{color:#22c55e}
.stat-val.red{color:#ef4444}
.stat-val.blue{color:#3b82f6}
.stat-lbl{font-size:11px;color:#64748b;margin-top:2px}
.current-q{background:#0f172a;border-radius:10px;padding:16px;margin-bottom:16px}
.q-label{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.q-chinese{font-size:20px;font-weight:700;color:#f1f5f9;word-break:break-word}
.q-empty{font-size:14px;color:#64748b;padding:8px 0}
.wrong-list{text-align:left;max-height:160px;overflow-y:auto;margin-top:12px}
.wrong-item{display:flex;justify-content:space-between;padding:6px 10px;background:#0f172a;border-radius:6px;margin-bottom:4px;font-size:12px;border-left:3px solid #ef4444}
.wrong-item .wi-ch{color:#f1f5f9}
.wrong-item .wi-ok{color:#22c55e}
.footer{font-size:11px;color:#475569;margin-top:16px}
.auto-refresh{font-size:11px;color:#3b82f6;margin-top:8px}
</style>
</head>
<body>
<div class="container">
  <h1>📝 英语默写</h1>
  <div class="sub">实时监看面板</div>
  <div id="app"></div>
  <div class="footer" id="footer"></div>
  <div class="auto-refresh" id="refreshStatus"></div>
</div>
<script>
var DATA = $safeJson;
// 解析数据
function render() {
  var d = DATA;
  var app = document.getElementById('app');
  var isActive = d.active === true;
  if (!isActive) {
    app.innerHTML = '<div class="status-card"><div class="status-icon">⏸️</div><div class="status-title">等待开始练习</div><div class="status-detail">打开手机上的英语默写 App 并开始练习，此处将自动显示进度</div></div>';
    document.getElementById('footer').textContent = '监看地址 ' + window.location.host;
    return;
  }
  var total = d.total || 0;
  var current = (d.currentIdx || 0) + 1;
  var done = d.done || 0;
  var wrong = d.wrong || 0;
  var correct = done - wrong;
  var pct = total > 0 ? (done / total * 100) : 0;
  var accuracy = done > 0 ? Math.round(correct / done * 100) : 0;
  var q = d.currentQuestion || '';
  var qType = d.currentType || '';
  var typeMap = {word:'📖 单词', phrase:'📝 词组', sentence:'💬 句子'};
  var typeLabel = typeMap[qType] || '';

  var wrongHtml = '';
  if (d.wrongRecords && d.wrongRecords.length > 0) {
    var seen = {};
    wrongHtml = '<div class="wrong-list">';
    d.wrongRecords.forEach(function(r) {
      if (seen[r.index]) return;
      seen[r.index] = true;
      wrongHtml += '<div class="wrong-item"><span class="wi-ch">' + esc(r.chinese) + '</span><span class="wi-ok">' + esc(r.answer) + '</span></div>';
    });
    wrongHtml += '</div>';
  }

  app.innerHTML = 
    '<div class="status-card">' +
      '<div class="status-icon">' + (d.isExamMode ? '📝' : '✏️') + '</div>' +
      '<div class="status-title">' + (d.isExamMode ? '测验模式' : '练习模式') + '</div>' +
      '<div class="status-detail">' + (d.sessionTitle || '进行中') + '</div>' +
      '<div class="progress-bar"><div class="progress-fill" style="width:' + pct + '%"></div></div>' +
      '<div class="stats-grid">' +
        '<div class="stat-item"><div class="stat-val blue">' + current + '/' + total + '</div><div class="stat-lbl">当前题</div></div>' +
        '<div class="stat-item"><div class="stat-val green">' + accuracy + '%</div><div class="stat-lbl">正确率</div></div>' +
        '<div class="stat-item"><div class="stat-val red">' + wrong + '</div><div class="stat-lbl">错误</div></div>' +
      '</div>' +
      '<div class="current-q">' +
        '<div class="q-label">' + typeLabel + '</div>' +
        '<div class="q-chinese">' + esc(q) + '</div>' +
      '</div>' +
      wrongHtml +
    '</div>';
  document.getElementById('footer').textContent = '监看地址 ' + window.location.host + ' | 自动刷新中';
}
function esc(s) {
  var d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}
render();
// 每 2 秒刷新页面
setTimeout(function() { window.location.reload(); }, 2000);
</script>
</body>
</html>
""".trimIndent()
    }
}



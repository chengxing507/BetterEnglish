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
import java.net.URLDecoder
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

    /** 供 HTTP 服务器获取 WebView */
    fun getWebView(): WebView = webView

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
        try {
            val reader = BufferedReader(InputStreamReader(client.inputStream))
            val requestLine = reader.readLine() ?: return
        
            // 读取请求头
            var line = reader.readLine()
            var contentLength = 0
            while (line != null && line.isNotEmpty()) {
                if (line.startsWith("Content-Length:", ignoreCase = true)) {
                    contentLength = line.substringAfter(":").trim().toIntOrNull() ?: 0
                }
                line = reader.readLine()
            }

            // 解析请求路径
            val parts = requestLine.split(" ")
            val method = parts.getOrNull(0) ?: return
            val path = parts.getOrNull(1) ?: "/"

            // 处理弹窗 API
            if (path.startsWith("/api/popup") && method == "POST") {
                val msg = path.substringAfter("msg=").substringBefore("&")
                    .replace("+", " ")
                    .let { java.net.URLDecoder.decode(it, "UTF-8") }
                // 通过 evaluateJavascript 调用前端的弹窗函数
                            activity.runOnUiThread {
                                activity.getWebView().evaluateJavascript(
                                    "onMonitorPopup('${msg.replace("'", "\\'").replace("\n", "\\n")}');",
                                    null
                                )
                            }
                val resp = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 2\r\nConnection: close\r\nAccess-Control-Allow-Origin: *\r\n\r\nOK"
                client.outputStream.write(resp.toByteArray(Charsets.UTF_8))
                client.outputStream.flush()
                return
            }

            // 读取当前快照
            val json = activity.getSnapshot()
            val body = buildStatusPage(json)
            val response = buildString {
                            append("HTTP/1.1 200 OK\r\n")
                            append("Content-Type: text/html; charset=utf-8\r\n")
                            append("Content-Length: ${body.toByteArray().size}\r\n")
                            append("Connection: close\r\n")
                            append("Access-Control-Allow-Origin: *\r\n")
                            append("\r\n")
                            append(body)
                        }

            client.outputStream.write(response.toByteArray(Charsets.UTF_8))
            client.outputStream.flush()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun buildStatusPage(json: String): String {
        val safeJson = json.replace("</script>", "<\\/script>")
        val template = activity.assets.open("monitor.html")
            .bufferedReader().use { it.readText() }
        return template.replace("__JSON__", safeJson)
    }

}



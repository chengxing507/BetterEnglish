package com.be.app

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        // WebView 配置
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true          // 本地存储
            allowFileAccess = true            // 允许访问 assets 文件
            allowContentAccess = true
            setSupportZoom(true)
            builtInZoomControls = true
            displayZoomControls = false
            loadWithOverviewMode = true
            useWideViewPort = true
            // 允许通过 file:// 加载
            allowFileAccessFromFileURLs = true
            allowUniversalAccessFromFileURLs = true
            // 缓存策略
            cacheMode = android.webkit.WebSettings.LOAD_DEFAULT
        }

        // WebViewClient：确保所有链接在当前 WebView 中打开
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                return false // 让 WebView 自己加载
            }
        }

        // 支持文件上传
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                // 创建文件选择 Intent
                val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                }
                // 使用 ActivityResultLauncher 方式（更现代）
                // 但由于 WebView 的特殊性，使用传统的 startActivityForResult 方式
                uploadCallback = filePathCallback
                startActivityForResult(intent, FILE_CHOOSER_REQUEST_CODE)
                return true
            }
        }

    private var uploadCallback: ValueCallback<Array<Uri>>? = null

    companion object {
        private const val FILE_CHOOSER_REQUEST_CODE = 1001
    }

    // 处理文件选择结果
    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
            if (resultCode == RESULT_OK && data != null) {
                val result = if (data.clipData != null) {
                    // 多文件选择
                    val uris = Array(data.clipData!!.itemCount) { i -> data.clipData!!.getItemAt(i).uri }
                    uris
                } else {
                    data.data?.let { arrayOf(it) }
                }
                uploadCallback?.onReceiveValue(result)
            } else {
                uploadCallback?.onReceiveValue(null)
            }
            uploadCallback = null
            return
        }
        super.onActivityResult(requestCode, resultCode, data)
    }

        // 从 assets 加载主页面
        webView.loadUrl("file:///android_asset/English_v1.4.2.html")
    }

    // 处理返回键：如果有历史记录则回退
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
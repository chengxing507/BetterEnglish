package com.be.app

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var uploadCallback: ValueCallback<Array<Uri>>? = null

    // Activity Result API：文件选择器（兼容 Android 12+，不会闪退）
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

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        // WebView 配置
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
        }

        // WebViewClient
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                return false
            }
        }

        // 支持文件上传（使用 Activity Result API，兼容 Android 12+）
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                this@MainActivity.uploadCallback?.onReceiveValue(null)
                this@MainActivity.uploadCallback = filePathCallback

                val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                }
                try {
                    fileChooserLauncher.launch(Intent.createChooser(intent, "选择文件"))
                } catch (e: Exception) {
                    this@MainActivity.uploadCallback?.onReceiveValue(null)
                    this@MainActivity.uploadCallback = null
                    return false
                }
                return true
            }
        }

        // 从 assets 加载主页面
        webView.loadUrl("file:///android_asset/English_v1.4.2.html")
    }

    // 处理返回键
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
}
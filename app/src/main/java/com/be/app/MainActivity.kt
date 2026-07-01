package com.be.app

import android.annotation.SuppressLint
import android.os.Bundle
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
        webView.webChromeClient = WebChromeClient()

        // 从 assets 加载主页面
        webView.loadUrl("file:///android_asset/English_v1.4.html")
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
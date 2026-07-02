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
    private var uploadCallback: ValueCallback<Array<Uri>>? = null

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

        // 支持文件上传
        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                }
                uploadCallback = filePathCallback
                startActivityForResult(intent, FILE_CHOOSER_REQUEST_CODE)
                return true
            }
        }

        // 从 assets 加载主页面
        webView.loadUrl("file:///android_asset/English_v1.4.2.html")
    }

    // 处理文件选择结果
    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
            if (resultCode == RESULT_OK && data != null) {
                val result = if (data.clipData != null) {
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

    // 处理返回键
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    companion object {
        private const val FILE_CHOOSER_REQUEST_CODE = 1001
    }
}
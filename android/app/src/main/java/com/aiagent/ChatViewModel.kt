package com.aiagent

import android.content.Context
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

private const val PREFS_NAME = "ai_agent_prefs"
private const val PREF_SERVER_URL = "server_url"
const val DEFAULT_SERVER_URL = "http://10.0.2.2:8000"

data class ChatMessage(val role: String, val content: String)

class ChatViewModel : ViewModel() {

    val messages = mutableStateListOf<ChatMessage>()
    val isLoading = mutableStateOf(false)
    val serverUrl = mutableStateOf(DEFAULT_SERVER_URL)
    val lastModel = mutableStateOf("")
    val errorMessage = mutableStateOf<String?>(null)

    private var sessionId: String? = null

    private val http = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    fun loadPrefs(context: Context) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        serverUrl.value = prefs.getString(PREF_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL
    }

    fun saveServerUrl(context: Context, url: String) {
        serverUrl.value = url
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit().putString(PREF_SERVER_URL, url).apply()
    }

    fun newConversation() {
        sessionId = null
        messages.clear()
        lastModel.value = ""
        errorMessage.value = null
    }

    fun sendMessage(userText: String) {
        if (userText.isBlank() || isLoading.value) return
        messages.add(ChatMessage("user", userText))
        isLoading.value = true
        errorMessage.value = null

        viewModelScope.launch {
            try {
                val result = withContext(Dispatchers.IO) { callApi(userText) }
                messages.add(ChatMessage("assistant", result.first))
                lastModel.value = result.second
                sessionId = result.third
            } catch (e: Exception) {
                errorMessage.value = e.message ?: "Unknown error"
            } finally {
                isLoading.value = false
            }
        }
    }

    /** Returns Triple(content, model_id, session_id). */
    private fun callApi(userText: String): Triple<String, String, String> {
        val body = JSONObject().apply {
            put("messages", JSONArray().put(JSONObject().apply {
                put("role", "user")
                put("content", userText)
            }))
            put("intent", "chat")
            sessionId?.let { put("session_id", it) }
        }

        val reqBody = body.toString()
            .toRequestBody("application/json".toMediaType())

        val baseUrl = serverUrl.value.trimEnd('/')
        val request = Request.Builder()
            .url("$baseUrl/v1/chat/completions")
            .post(reqBody)
            .build()

        val response = http.newCall(request).execute()
        val responseBody = response.body?.string() ?: ""

        if (!response.isSuccessful) {
            throw Exception("HTTP ${response.code}: $responseBody")
        }

        val json = JSONObject(responseBody)
        val content = json.getString("content")
        val model = json.optString("model", "unknown")
        val sid = json.optString("session_id", sessionId ?: "")
        return Triple(content, model, sid)
    }
}

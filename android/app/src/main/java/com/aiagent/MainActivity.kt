package com.aiagent

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    external fun stringFromJNI(): String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val nativeMessage = if (nativeLoaded) {
            runCatching { stringFromJNI() }.getOrElse { "Native call unavailable" }
        } else {
            "Native library failed to load"
        }

        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    AppScaffold(nativeMessage)
                }
            }
        }
    }

    companion object {
        private val nativeLoaded: Boolean = runCatching {
            System.loadLibrary("aiagent-native")
        }.isSuccess
    }
}

@Composable
private fun AppScaffold(nativeMessage: String) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "AI-AGENT (Android Kotlin + C++ + Compose)", style = MaterialTheme.typography.headlineSmall)
        Text(text = "Native layer says: $nativeMessage")
        Text(text = "• Jetpack Compose UI enabled")
        Text(text = "• JNI bridge with CMake enabled")
        Text(text = "• Ready for feature module expansion")
    }
}

package com.aiagent

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    ChatScreen()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ChatScreen(vm: ChatViewModel = viewModel()) {
    val context = LocalContext.current
    LaunchedEffect(Unit) { vm.loadPrefs(context) }

    var showSettings by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("AI-AGENT", fontWeight = FontWeight.Bold) },
                actions = {
                    if (vm.lastModel.value.isNotEmpty()) {
                        Text(
                            text = vm.lastModel.value,
                            fontSize = 11.sp,
                            color = MaterialTheme.colorScheme.onPrimary.copy(alpha = .8f),
                            modifier = Modifier.padding(end = 8.dp)
                        )
                    }
                    TextButton(onClick = { vm.newConversation() }) {
                        Text("New", color = MaterialTheme.colorScheme.onPrimary)
                    }
                    TextButton(onClick = { showSettings = true }) {
                        Text("⚙", color = MaterialTheme.colorScheme.onPrimary)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { innerPadding ->
        Column(modifier = Modifier.fillMaxSize().padding(innerPadding)) {
            MessageList(messages = vm.messages, isLoading = vm.isLoading.value, modifier = Modifier.weight(1f))

            vm.errorMessage.value?.let { err ->
                Text(
                    text = "⚠ $err",
                    color = MaterialTheme.colorScheme.error,
                    fontSize = 12.sp,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                )
            }

            InputRow(onSend = { text -> vm.sendMessage(text) }, enabled = !vm.isLoading.value)
        }
    }

    if (showSettings) {
        SettingsDialog(
            currentUrl = vm.serverUrl.value,
            onDismiss = { showSettings = false },
            onSave = { url ->
                vm.saveServerUrl(context, url)
                showSettings = false
            }
        )
    }
}

@Composable
fun MessageList(messages: List<ChatMessage>, isLoading: Boolean, modifier: Modifier = Modifier) {
    val listState = rememberLazyListState()
    LaunchedEffect(messages.size, isLoading) {
        if (messages.isNotEmpty()) listState.animateScrollToItem(messages.size - 1)
    }

    LazyColumn(
        state = listState,
        modifier = modifier.padding(horizontal = 12.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        contentPadding = PaddingValues(vertical = 12.dp)
    ) {
        if (messages.isEmpty()) {
            item {
                Text(
                    "👋 Say hello to start a conversation!\n\nMake sure your backend is running and the URL is set in ⚙ Settings.",
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = .5f),
                    fontSize = 14.sp,
                    modifier = Modifier.padding(16.dp)
                )
            }
        }
        items(messages) { msg -> MessageBubble(msg) }
        if (isLoading) {
            item {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    CircularProgressIndicator(modifier = Modifier.size(18.dp), strokeWidth = 2.dp)
                    Spacer(Modifier.width(8.dp))
                    Text("Thinking…", color = MaterialTheme.colorScheme.onSurface.copy(alpha = .5f), fontSize = 13.sp)
                }
            }
        }
    }
}

@Composable
fun MessageBubble(msg: ChatMessage) {
    val isUser = msg.role == "user"
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
    ) {
        Box(
            modifier = Modifier
                .widthIn(max = 300.dp)
                .clip(
                    RoundedCornerShape(
                        topStart = 16.dp, topEnd = 16.dp,
                        bottomStart = if (isUser) 16.dp else 4.dp,
                        bottomEnd = if (isUser) 4.dp else 16.dp
                    )
                )
                .background(if (isUser) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant)
                .padding(horizontal = 14.dp, vertical = 10.dp)
        ) {
            Text(
                text = msg.content,
                color = if (isUser) MaterialTheme.colorScheme.onPrimary else MaterialTheme.colorScheme.onSurface,
                fontSize = 15.sp
            )
        }
    }
}

@Composable
fun InputRow(onSend: (String) -> Unit, enabled: Boolean) {
    var text by remember { mutableStateOf("") }

    fun doSend() {
        val t = text.trim()
        if (t.isNotEmpty() && enabled) {
            onSend(t)
            text = ""
        }
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface)
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        TextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.weight(1f),
            placeholder = { Text("Ask anything…") },
            enabled = enabled,
            singleLine = false,
            maxLines = 4,
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
            keyboardActions = KeyboardActions(onSend = { doSend() }),
            colors = TextFieldDefaults.colors(
                focusedContainerColor = MaterialTheme.colorScheme.surfaceVariant,
                unfocusedContainerColor = MaterialTheme.colorScheme.surfaceVariant
            ),
            shape = RoundedCornerShape(12.dp)
        )
        Spacer(Modifier.width(8.dp))
        Button(
            onClick = { doSend() },
            enabled = enabled && text.isNotBlank(),
            shape = RoundedCornerShape(12.dp)
        ) {
            Text("Send")
        }
    }
}

@Composable
fun SettingsDialog(currentUrl: String, onDismiss: () -> Unit, onSave: (String) -> Unit) {
    var url by remember { mutableStateOf(currentUrl) }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Settings") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Backend server URL", style = MaterialTheme.typography.labelMedium)
                OutlinedTextField(
                    value = url,
                    onValueChange = { url = it },
                    singleLine = true,
                    placeholder = { Text(DEFAULT_SERVER_URL) },
                    modifier = Modifier.fillMaxWidth()
                )
                Text(
                    "Use http://10.0.2.2:8000 for a local backend on Android Emulator.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = .6f)
                )
            }
        },
        confirmButton = { Button(onClick = { onSave(url.trim()) }) { Text("Save") } },
        dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } }
    )
}


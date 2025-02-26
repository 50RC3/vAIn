package com.mlchatbot.ui;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import com.google.android.material.textfield.TextInputEditText;
import com.google.android.material.button.MaterialButton;
import com.mlchatbot.R;
import com.mlchatbot.ml.LocalModel;
import com.mlchatbot.p2p.P2PManager;
import java.util.ArrayList;
import java.util.List;

public class ChatActivity extends AppCompatActivity {
    private RecyclerView chatRecyclerView;
    private ChatAdapter chatAdapter;
    private TextInputEditText messageInput;
    private MaterialButton sendButton;
    private LocalModel localModel;
    private P2PManager p2pManager;
    private List<MessageItem> messages;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_chat);
        
        // Initialize UI components
        initializeViews();
        
        // Initialize ML model and P2P manager
        localModel = new LocalModel(this);
        p2pManager = new P2PManager(this);
        
        // Initialize message list and adapter
        messages = new ArrayList<>();
        chatAdapter = new ChatAdapter(messages);
        chatRecyclerView.setAdapter(chatAdapter);
        chatRecyclerView.setLayoutManager(new LinearLayoutManager(this));
        
        // Set up click listeners
        setupClickListeners();
    }

    private void initializeViews() {
        chatRecyclerView = findViewById(R.id.chat_recycler_view);
        messageInput = findViewById(R.id.message_input);
        sendButton = findViewById(R.id.send_button);
    }

    private void setupClickListeners() {
        sendButton.setOnClickListener(v -> {
            String message = messageInput.getText().toString().trim();
            if (!message.isEmpty()) {
                sendMessage(message);
                messageInput.setText("");
            }
        });
    }

    private void sendMessage(String message) {
        // Add user message to chat
        MessageItem userMessage = new MessageItem(message, true);
        messages.add(userMessage);
        chatAdapter.notifyItemInserted(messages.size() - 1);
        chatRecyclerView.scrollToPosition(messages.size() - 1);

        // Get model response
        localModel.generateResponse(message, response -> {
            MessageItem botMessage = new MessageItem(response, false);
            messages.add(botMessage);
            chatAdapter.notifyItemInserted(messages.size() - 1);
            chatRecyclerView.scrollToPosition(messages.size() - 1);

            // Update P2P network with new interaction
            p2pManager.shareModelUpdate();
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        localModel.close();
        p2pManager.disconnect();
    }
}

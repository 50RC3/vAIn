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

    // ...existing code...
}

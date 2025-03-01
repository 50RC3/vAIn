package com.vain.android.ui;

public class ChatMessage {
    private String text;
    private String timestamp;
    private boolean isUser;

    public ChatMessage(String text, String timestamp, boolean isUser) {
        this.text = text;
        this.timestamp = timestamp;
        this.isUser = isUser;
    }

    public String getText() {
        return text;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public boolean isUser() {
        return isUser;
    }
}

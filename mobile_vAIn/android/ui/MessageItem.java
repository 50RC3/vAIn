package com.mlchatbot.ui;

public class MessageItem {
    private final String message;
    private final boolean isUser;
    private final long timestamp;

    public MessageItem(String message, boolean isUser) {
        this.message = message;
        this.isUser = isUser;
        this.timestamp = System.currentTimeMillis();
    }

    public String getMessage() {
        return message;
    }

    public boolean isUser() {
        return isUser;
    }

    public long getTimestamp() {
        return timestamp;
    }
}

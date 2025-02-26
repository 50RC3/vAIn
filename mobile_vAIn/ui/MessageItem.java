package com.mlchatbot.ui;

import java.util.Date;

public class MessageItem {
    private final String message;
    private final boolean isUser;
    private final Date timestamp;

    public MessageItem(String message, boolean isUser) {
        this.message = message;
        this.isUser = isUser;
        this.timestamp = new Date();
    }

    public String getMessage() {
        return message;
    }

    public boolean isUser() {
        return isUser;
    }

    public Date getTimestamp() {
        return timestamp;
    }

    @Override
    public String toString() {
        return "MessageItem{" +
                "message='" + message + '\'' +
                ", isUser=" + isUser +
                ", timestamp=" + timestamp +
                '}';
    }
}

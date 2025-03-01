package com.vain.android.ui;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class Main {
    public static void main(String[] args) {
        // Create a timestamp
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
        
        // Create some example messages
        ChatMessage userMessage = new ChatMessage("Hello, AI!", timestamp, true);
        ChatMessage aiMessage = new ChatMessage("Hello, User!", timestamp, false);
        
        // Print the messages
        System.out.println("User message: " + userMessage.getText() + " [" + userMessage.getTimestamp() + "]");
        System.out.println("AI message: " + aiMessage.getText() + " [" + aiMessage.getTimestamp() + "]");
    }
}

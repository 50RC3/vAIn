package com.mlchatbot.p2p;

import android.util.Log;
import com.mlchatbot.ml.LocalModel;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class PeerConnection {
    private static final String TAG = "PeerConnection";
    private static final int BUFFER_SIZE = 1024 * 1024; // 1MB buffer
    private static final byte MESSAGE_TYPE_MODEL_UPDATE = 1;
    private static final byte MESSAGE_TYPE_SYNC_REQUEST = 2;

    private final Socket socket;
    private final DataInputStream inputStream;
    private final DataOutputStream outputStream;
    private final ExecutorService executor;
    private boolean isRunning;

    public PeerConnection(Socket socket) throws IOException {
        this.socket = socket;
        this.inputStream = new DataInputStream(socket.getInputStream());
        this.outputStream = new DataOutputStream(socket.getOutputStream());
        this.executor = Executors.newSingleThreadExecutor();
        this.isRunning = true;
    }

    public void startModelSync(LocalModel localModel) {
        executor.execute(() -> {
            try {
                while (isRunning) {
                    // Read message type
                    byte messageType = inputStream.readByte();
                    
                    switch (messageType) {
                        case MESSAGE_TYPE_MODEL_UPDATE:
                            handleModelUpdate(localModel);
                            break;
                        case MESSAGE_TYPE_SYNC_REQUEST:
                            handleSyncRequest(localModel);
                            break;
                        default:
                            Log.w(TAG, "Unknown message type received: " + messageType);
                    }
                }
            } catch (IOException e) {
                Log.e(TAG, "Error during model sync", e);
                close();
            }
        });
    }

    private void handleModelUpdate(LocalModel localModel) throws IOException {
        // Read update size
        int updateSize = inputStream.readInt();
        if (updateSize <= 0 || updateSize > BUFFER_SIZE) {
            throw new IOException("Invalid update size: " + updateSize);
        }

        // Read update data
        byte[] updateData = new byte[updateSize];
        int bytesRead = 0;
        while (bytesRead < updateSize) {
            int count = inputStream.read(updateData, bytesRead, updateSize - bytesRead);
            if (count < 0) {
                throw new IOException("End of stream reached before complete update received");
            }
            bytesRead += count;
        }

        // Verify checksum
        long receivedChecksum = inputStream.readLong();
        long calculatedChecksum = calculateChecksum(updateData);
        if (receivedChecksum != calculatedChecksum) {
            throw new IOException("Checksum mismatch");
        }

        // Apply update to local model
        try {
            localModel.updateModelWithFederatedLearning(updateData);
            sendAcknowledgement(true);
        } catch (Exception e) {
            Log.e(TAG, "Error applying model update", e);
            sendAcknowledgement(false);
        }
    }

    private void handleSyncRequest(LocalModel localModel) {
        // TODO: Implement model state synchronization
        // This would involve:
        // 1. Getting current model state
        // 2. Serializing the state
        // 3. Sending it to the peer
    }

    public void sendModelUpdate(byte[] updateData) throws IOException {
        synchronized (outputStream) {
            // Write message type
            outputStream.writeByte(MESSAGE_TYPE_MODEL_UPDATE);
            
            // Write update size
            outputStream.writeInt(updateData.length);
            
            // Write update data
            outputStream.write(updateData);
            
            // Write checksum
            outputStream.writeLong(calculateChecksum(updateData));
            
            outputStream.flush();
        }
    }

    private void sendAcknowledgement(boolean success) throws IOException {
        synchronized (outputStream) {
            outputStream.writeBoolean(success);
            outputStream.flush();
        }
    }

    private long calculateChecksum(byte[] data) {
        // Simple checksum calculation
        long checksum = 0;
        ByteBuffer buffer = ByteBuffer.wrap(data);
        while (buffer.hasRemaining()) {
            if (buffer.remaining() >= 8) {
                checksum ^= buffer.getLong();
            } else {
                checksum ^= buffer.get();
            }
        }
        return checksum;
    }

    public void requestSync() throws IOException {
        synchronized (outputStream) {
            outputStream.writeByte(MESSAGE_TYPE_SYNC_REQUEST);
            outputStream.flush();
        }
    }

    public void close() {
        isRunning = false;
        executor.shutdown();
        try {
            socket.close();
        } catch (IOException e) {
            Log.e(TAG, "Error closing socket", e);
        }
    }
}

package com.mlchatbot.p2p;

import android.content.Context;
import android.net.wifi.p2p.WifiP2pManager;
import android.net.wifi.p2p.WifiP2pConfig;
import android.net.wifi.p2p.WifiP2pInfo;
import android.util.Log;
import com.mlchatbot.ml.LocalModel;
import org.json.JSONObject;
import java.io.IOException;
import java.net.Socket;
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;

public class P2PManager implements WifiP2pManager.ConnectionInfoListener {
    private static final String TAG = "P2PManager";
    private final Context context;
    private final WifiP2pManager manager;
    private final WifiP2pManager.Channel channel;
    private LocalModel localModel;
    private final Map<String, PeerConnection> peerConnections;
    private boolean isGroupOwner = false;
    private String groupOwnerAddress;

    public P2PManager(Context context) {
        this.context = context;
        this.manager = (WifiP2pManager) context.getSystemService(Context.WIFI_P2P_SERVICE);
        this.channel = manager.initialize(context, context.getMainLooper(), null);
        this.peerConnections = new ConcurrentHashMap<>();
    }

    public void setLocalModel(LocalModel model) {
        this.localModel = model;
    }

    public void startDiscovery() {
        manager.discoverPeers(channel, new WifiP2pManager.ActionListener() {
            @Override
            public void onSuccess() {
                Log.d(TAG, "Discovery started successfully");
            }

            @Override
            public void onFailure(int reason) {
                Log.e(TAG, "Discovery start failed with reason: " + reason);
            }
        });
    }

    public void shareModelUpdate() throws IOException {
        if (localModel == null) return;

        JSONObject modelUpdate = localModel.getModelUpdate();
        for (PeerConnection conn : peerConnections.values()) {
            try {
                conn.sendModelUpdate(modelUpdate);
            } catch (IOException e) {
                Log.e(TAG, "Failed to share model update with peer: " + conn.getPeerId(), e);
            }
        }
    }

    @Override
    public void onConnectionInfoAvailable(WifiP2pInfo info) {
        this.isGroupOwner = info.isGroupOwner;
        this.groupOwnerAddress = info.groupOwnerAddress.getHostAddress();

        if (isGroupOwner) {
            startGroupOwnerServer();
        } else {
            connectToGroupOwner();
        }
    }

    private void startGroupOwnerServer() {
        // Implementation for group owner server
        // This would handle incoming connections from peers
    }

    private void connectToGroupOwner() {
        // Implementation for connecting to group owner
        // This would establish connection to the group owner
    }

    public void disconnect() {
        manager.removeGroup(channel, new WifiP2pManager.ActionListener() {
            @Override
            public void onSuccess() {
                Log.d(TAG, "Disconnected successfully");
            }

            @Override
            public void onFailure(int reason) {
                Log.e(TAG, "Disconnect failed with reason: " + reason);
            }
        });

        for (PeerConnection conn : peerConnections.values()) {
            conn.close();
        }
        peerConnections.clear();
    }

    private static class PeerConnection implements AutoCloseable {
        private final Socket socket;
        private final String peerId;

        public PeerConnection(Socket socket, String peerId) {
            this.socket = socket;
            this.peerId = peerId;
        }

        public void sendModelUpdate(JSONObject update) throws IOException {
            // Implementation for sending model update to peer
        }

        public String getPeerId() {
            return peerId;
        }

        @Override
        public void close() {
            try {
                socket.close();
            } catch (IOException e) {
                Log.e(TAG, "Error closing peer connection", e);
            }
        }
    }
}

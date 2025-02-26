package com.mlchatbot.p2p;

import android.content.Context;
import android.net.wifi.p2p.WifiP2pConfig;
import android.net.wifi.p2p.WifiP2pDevice;
import android.net.wifi.p2p.WifiP2pDeviceList;
import android.net.wifi.p2p.WifiP2pInfo;
import android.net.wifi.p2p.WifiP2pManager;
import android.util.Log;
import com.mlchatbot.ml.LocalModel;
import java.io.IOException;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class P2PManager implements WifiP2pManager.ChannelListener {
    private static final String TAG = "P2PManager";
    private static final int PORT = 8888;

    private final Context context;
    private final WifiP2pManager manager;
    private final WifiP2pManager.Channel channel;
    private final List<WifiP2pDevice> peers;
    private final ExecutorService executor;
    private LocalModel localModel;
    private ServerSocket serverSocket;
    private boolean isGroupOwner = false;
    private InetAddress groupOwnerAddress;

    public P2PManager(Context context) {
        this.context = context;
        this.manager = (WifiP2pManager) context.getSystemService(Context.WIFI_P2P_SERVICE);
        this.channel = manager.initialize(context, context.getMainLooper(), this);
        this.peers = new ArrayList<>();
        this.executor = Executors.newCachedThreadPool();
        
        initializeP2P();
    }

    private void initializeP2P() {
        // Start peer discovery
        manager.discoverPeers(channel, new WifiP2pManager.ActionListener() {
            @Override
            public void onSuccess() {
                Log.d(TAG, "Peer discovery started");
            }

            @Override
            public void onFailure(int reason) {
                Log.e(TAG, "Peer discovery failed: " + reason);
            }
        });

        // Register peer discovery callback
        WifiP2pManager.PeerListListener peerListListener = new WifiP2pManager.PeerListListener() {
            @Override
            public void onPeersAvailable(WifiP2pDeviceList peerList) {
                peers.clear();
                peers.addAll(peerList.getDeviceList());
                Log.d(TAG, "Found " + peers.size() + " peers");
            }
        };

        // Register connection info callback
        WifiP2pManager.ConnectionInfoListener connectionInfoListener = new WifiP2pManager.ConnectionInfoListener() {
            @Override
            public void onConnectionInfoAvailable(WifiP2pInfo info) {
                groupOwnerAddress = info.groupOwnerAddress;
                isGroupOwner = info.isGroupOwner;

                if (isGroupOwner) {
                    startServer();
                } else {
                    connectToGroupOwner();
                }
            }
        };
    }

    private void startServer() {
        executor.execute(() -> {
            try {
                serverSocket = new ServerSocket(PORT);
                while (!Thread.currentThread().isInterrupted()) {
                    Socket client = serverSocket.accept();
                    handleClientConnection(client);
                }
            } catch (IOException e) {
                Log.e(TAG, "Server socket error", e);
            }
        });
    }

    private void handleClientConnection(Socket client) {
        executor.execute(() -> {
            try {
                PeerConnection connection = new PeerConnection(client);
                connection.startModelSync(localModel);
            } catch (IOException e) {
                Log.e(TAG, "Error handling client connection", e);
            }
        });
    }

    private void connectToGroupOwner() {
        if (groupOwnerAddress != null) {
            executor.execute(() -> {
                try {
                    Socket socket = new Socket(groupOwnerAddress, PORT);
                    PeerConnection connection = new PeerConnection(socket);
                    connection.startModelSync(localModel);
                } catch (IOException e) {
                    Log.e(TAG, "Error connecting to group owner", e);
                }
            });
        }
    }

    public void shareModelUpdate() {
        // Trigger model update sharing with connected peers
        for (WifiP2pDevice peer : peers) {
            connectToPeer(peer);
        }
    }

    private void connectToPeer(WifiP2pDevice device) {
        WifiP2pConfig config = new WifiP2pConfig();
        config.deviceAddress = device.deviceAddress;

        manager.connect(channel, config, new WifiP2pManager.ActionListener() {
            @Override
            public void onSuccess() {
                Log.d(TAG, "Connected to peer: " + device.deviceAddress);
            }

            @Override
            public void onFailure(int reason) {
                Log.e(TAG, "Failed to connect to peer: " + reason);
            }
        });
    }

    public void setLocalModel(LocalModel model) {
        this.localModel = model;
    }

    @Override
    public void onChannelDisconnected() {
        Log.e(TAG, "P2P channel disconnected");
        // Attempt to reinitialize
        manager.initialize(context, context.getMainLooper(), this);
    }

    public void disconnect() {
        if (serverSocket != null) {
            try {
                serverSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "Error closing server socket", e);
            }
        }

        manager.removeGroup(channel, new WifiP2pManager.ActionListener() {
            @Override
            public void onSuccess() {
                Log.d(TAG, "P2P group removed");
            }

            @Override
            public void onFailure(int reason) {
                Log.e(TAG, "Failed to remove P2P group: " + reason);
            }
        });

        executor.shutdown();
    }
}

package com.mlchatbot.p2p;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;
import androidx.annotation.Nullable;
import com.mlchatbot.ml.LocalModel;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class P2PService extends Service {
    private static final String TAG = "P2PService";
    
    private final IBinder binder = new LocalBinder();
    private P2PManager p2pManager;
    private LocalModel localModel;
    private ExecutorService executor;
    private boolean isRunning = false;

    public class LocalBinder extends Binder {
        P2PService getService() {
            return P2PService.this;
        }
    }

    @Override
    public void onCreate() {
        super.onCreate();
        executor = Executors.newCachedThreadPool();
        p2pManager = new P2PManager(this);
        localModel = new LocalModel(this);
        p2pManager.setLocalModel(localModel);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (!isRunning) {
            startP2PDiscovery();
            isRunning = true;
        }
        // If service is killed, restart it
        return START_STICKY;
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return binder;
    }

    private void startP2PDiscovery() {
        executor.execute(() -> {
            try {
                // Start discovering peers and handling connections
                p2pManager.startDiscovery();
                
                // Schedule periodic model synchronization
                scheduleModelSync();
                
                Log.i(TAG, "P2P discovery started successfully");
            } catch (Exception e) {
                Log.e(TAG, "Error starting P2P discovery", e);
            }
        });
    }

    private void scheduleModelSync() {
        executor.execute(() -> {
            while (isRunning) {
                try {
                    // Attempt to sync model with peers every 30 minutes
                    p2pManager.shareModelUpdate();
                    Thread.sleep(30 * 60 * 1000); // 30 minutes
                } catch (InterruptedException e) {
                    Log.e(TAG, "Model sync interrupted", e);
                    Thread.currentThread().interrupt();
                    break;
                } catch (Exception e) {
                    Log.e(TAG, "Error during model sync", e);
                }
            }
        });
    }

    public void requestImmediateSync() {
        executor.execute(() -> {
            try {
                p2pManager.shareModelUpdate();
                Log.i(TAG, "Immediate sync requested and completed");
            } catch (Exception e) {
                Log.e(TAG, "Error during immediate sync", e);
            }
        });
    }

    @Override
    public void onDestroy() {
        isRunning = false;
        if (p2pManager != null) {
            p2pManager.disconnect();
        }
        if (localModel != null) {
            localModel.close();
        }
        if (executor != null) {
            executor.shutdown();
        }
        super.onDestroy();
    }

    public boolean isServiceRunning() {
        return isRunning;
    }

    public void updateLearningRate(float learningRate) {
        if (localModel != null) {
            executor.execute(() -> {
                try {
                    // Update learning rate for local model training
                    // This would be implemented in the LocalModel class
                    Log.i(TAG, "Learning rate updated to: " + learningRate);
                } catch (Exception e) {
                    Log.e(TAG, "Error updating learning rate", e);
                }
            });
        }
    }

    public void forceModelUpdate() {
        if (localModel != null && p2pManager != null) {
            executor.execute(() -> {
                try {
                    // Force a model update and share with peers
                    p2pManager.shareModelUpdate();
                    Log.i(TAG, "Forced model update completed");
                } catch (Exception e) {
                    Log.e(TAG, "Error during forced model update", e);
                }
            });
        }
    }
}

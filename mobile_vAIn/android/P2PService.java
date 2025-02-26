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
import java.util.concurrent.TimeUnit;

public class P2PService extends Service {
    private static final String TAG = "P2PService";
    private static final long SYNC_INTERVAL = TimeUnit.MINUTES.toMillis(30);
    
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
        Log.d(TAG, "P2PService created");
        p2pManager = new P2PManager(this);
        executor = Executors.newSingleThreadExecutor();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (!isRunning) {
            startP2PDiscovery();
            isRunning = true;
        }
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
                p2pManager.startDiscovery();
                scheduleModelSync();
                Log.i(TAG, "P2P discovery started successfully");
            } catch (Exception e) {
                Log.e(TAG, "Error starting P2P discovery", e);
                retryDiscovery();
            }
        });
    }

    private void retryDiscovery() {
        executor.execute(() -> {
            try {
                Thread.sleep(TimeUnit.SECONDS.toMillis(30));
                startP2PDiscovery();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }

    private void scheduleModelSync() {
        executor.execute(() -> {
            while (isRunning && !Thread.currentThread().isInterrupted()) {
                try {
                    p2pManager.shareModelUpdate();
                    Thread.sleep(SYNC_INTERVAL);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                } catch (Exception e) {
                    Log.e(TAG, "Error during model sync", e);
                    handleSyncError(e);
                }
            }
        });
    }

    private void handleSyncError(Exception e) {
        if (isRunning) {
            executor.execute(() -> {
                try {
                    Thread.sleep(TimeUnit.SECONDS.toMillis(60));
                    p2pManager.shareModelUpdate();
                } catch (Exception retryError) {
                    Log.e(TAG, "Retry sync failed", retryError);
                }
            });
        }
    }

    @Override
    public void onDestroy() {
        isRunning = false;
        if (executor != null) {
            executor.shutdownNow();
            try {
                if (!executor.awaitTermination(5, TimeUnit.SECONDS)) {
                    Log.w(TAG, "Executor did not terminate in time");
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        if (p2pManager != null) {
            p2pManager.disconnect();
        }
        if (localModel != null) {
            localModel.close();
        }
        super.onDestroy();
        Log.d(TAG, "P2PService destroyed");
    }
}
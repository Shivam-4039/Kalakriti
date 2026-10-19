import { create } from 'zustand';
import * as SQLite from 'expo-sqlite';
import { api } from '../services/api';

const db = SQLite.openDatabaseSync('kalakriti_offline.db');

export interface OfflineRequest {
  id: number;
  endpoint: string;
  method: 'POST' | 'PUT' | 'DELETE';
  payload: string; // JSON string
  created_at: string;
}

interface OfflineState {
  isOffline: boolean;
  pendingCount: number;
  isSyncing: boolean;

  setOfflineStatus: (isOffline: boolean) => void;
  initDb: () => void;
  queueRequest: (endpoint: string, method: 'POST' | 'PUT' | 'DELETE', payload: object) => Promise<void>;
  syncPendingRequests: () => Promise<void>;
}

export const useOfflineStore = create<OfflineState>((set, get) => ({
  isOffline: false,
  pendingCount: 0,
  isSyncing: false,

  setOfflineStatus: (isOffline: boolean) => {
    set({ isOffline });
    if (!isOffline) {
      get().syncPendingRequests();
    }
  },

  // Initialize offline requests table
  initDb: () => {
    try {
      db.execSync(`
        CREATE TABLE IF NOT EXISTS pending_requests (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          endpoint TEXT NOT NULL,
          method TEXT NOT NULL,
          payload TEXT NOT NULL,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
      `);
      
      const countResult = db.getFirstSync<{ count: number }>('SELECT COUNT(*) as count FROM pending_requests');
      set({ pendingCount: countResult?.count || 0 });
    } catch (error) {
      console.error('[OfflineStore] Failed to initialize SQLite DB:', error);
    }
  },

  // Push failed network mutation request to local SQLite queue
  queueRequest: async (endpoint: string, method: 'POST' | 'PUT' | 'DELETE', payload: object) => {
    try {
      db.runSync(
        'INSERT INTO pending_requests (endpoint, method, payload) VALUES (?, ?, ?)',
        [endpoint, method, JSON.stringify(payload)]
      );
      
      const countResult = db.getFirstSync<{ count: number }>('SELECT COUNT(*) as count FROM pending_requests');
      set({ pendingCount: countResult?.count || 0 });
      console.log(`[OfflineStore] Request queued for ${endpoint}`);
    } catch (error) {
      console.error('[OfflineStore] Failed to queue offline request:', error);
    }
  },

  // Attempt to flush and execute queued requests when network restores
  syncPendingRequests: async () => {
    if (get().isSyncing || get().isOffline) return;

    try {
      set({ isSyncing: true });
      const pendingRequests = db.getAllSync<OfflineRequest>('SELECT * FROM pending_requests ORDER BY id ASC');

      if (pendingRequests.length === 0) {
        set({ isSyncing: false, pendingCount: 0 });
        return;
      }

      console.log(`[OfflineStore] Syncing ${pendingRequests.length} pending offline requests...`);

      for (const req of pendingRequests) {
        try {
          const payloadObj = JSON.parse(req.payload);
          if (req.method === 'POST') await api.post(req.endpoint, payloadObj);
          if (req.method === 'PUT') await api.put(req.endpoint, payloadObj);
          if (req.method === 'DELETE') await api.delete(req.endpoint);

          // Delete executed request from SQLite database
          db.runSync('DELETE FROM pending_requests WHERE id = ?', [req.id]);
        } catch (err) {
          console.error(`[OfflineStore] Sync failed for request #${req.id}:`, err);
          break; // Stop execution loop if connection drops mid-sync
        }
      }

      const countResult = db.getFirstSync<{ count: number }>('SELECT COUNT(*) as count FROM pending_requests');
      set({ pendingCount: countResult?.count || 0 });
    } catch (error) {
      console.error('[OfflineStore] Error during offline sync process:', error);
    } finally {
      set({ isSyncing: false });
    }
  },
}));
import { useEffect, useState } from 'react';
import * as Network from 'expo-network';
import { useOfflineStore } from '../stores/offlineStore';

export const useNetwork = () => {
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const setOfflineStatus = useOfflineStore((state) => state.setOfflineStatus);

  useEffect(() => {
    let isMounted = true;

    const checkNetwork = async () => {
      try {
        const state = await Network.getNetworkStateAsync();
        const connected = Boolean(state.isConnected && state.isInternetReachable !== false);

        if (isMounted) {
          setIsConnected(connected);
          setOfflineStatus(!connected);
        }
      } catch (error) {
        console.error('[useNetwork] Error checking network status:', error);
      }
    };

    // Initial check
    checkNetwork();

    // Check connection periodically every 5 seconds
    const intervalId = setInterval(checkNetwork, 5000);

    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, [setOfflineStatus]);

  return { isConnected };
};
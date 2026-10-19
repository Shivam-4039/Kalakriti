import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { WifiOff, Wifi } from 'lucide-react-native';
import { colors, layout, typography } from '../theme';
import { useOfflineStore } from '../stores/offlineStore';

export const NetworkBanner: React.FC = () => {
    const isOffline = useOfflineStore((state) => state.isOffline);
    const pendingCount = useOfflineStore((state) => state.pendingCount);
    const [showReconnected, setShowReconnected] = useState<boolean>(false);
    const [wasOffline, setWasOffline] = useState<boolean>(false);

    useEffect(() => {
        if (isOffline) {
            setWasOffline(true);
        } else if (wasOffline) {
            setShowReconnected(true);
            const timer = setTimeout(() => {
                setShowReconnected(false);
                setWasOffline(false);
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [isOffline, wasOffline]);

    if (!isOffline && !showReconnected) return null;

    return (
        <View
            style={[
                styles.banner,
                { backgroundColor: isOffline ? colors.error : colors.success },
            ]}
        >
            {isOffline ? (
                <>
                    <WifiOff size={18} color="#FFFFFF" style={styles.icon} />
                    <Text style={styles.text}>
                        इंटरनेट बंद है (Offline)
                        {pendingCount > 0 ? ` • ${pendingCount} सेव्ड` : ''}
                    </Text>
                </>
            ) : (
                <>
                    <Wifi size={18} color="#FFFFFF" style={styles.icon} />
                    <Text style={styles.text}>इंटरनेट चालू हो गया (Connected)</Text>
                </>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    banner: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: layout.spacing.xs + 2,
        paddingHorizontal: layout.spacing.md,
    },
    icon: {
        marginRight: layout.spacing.xs,
    },
    text: {
        color: '#FFFFFF',
        fontSize: typography.sizes.caption,
        fontWeight: '700',
    },
});
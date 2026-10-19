import React, { useCallback, useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, RefreshControl } from 'react-native';
import { useRouter, useFocusEffect } from 'expo-router';
import { PlusCircle, Package, Globe, Mic } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';
import { BigButton } from '../../components/BigButton';
import { SpeakOnMount } from '../../components/SpeakOnMount';
import { FloatingMicHelp } from '../../components/FloatingMicHelp';
import { NetworkBanner } from '../../components/NetworkBanner';
import { useAuthStore } from '../../stores/authStore';
import { api } from '../../services/api';

export default function HomeScreen() {
    const router = useRouter();
    const artisan = useAuthStore((state) => state.artisan);

    const [productCount, setProductCount] = useState<number>(0);
    const [ondcCount, setOndcCount] = useState<number>(0);
    const [refreshing, setRefreshing] = useState<boolean>(false);

    const fetchDashboardStats = useCallback(async () => {
        try {
            setRefreshing(true);
            const response = await api.get<{ items: { ondc_status?: string }[] }>('/products?limit=100');
            const items = response.data.items || [];
            setProductCount(items.length);

            const liveItems = items.filter((p) => p.ondc_status === 'published');
            setOndcCount(liveItems.length);
        } catch (error) {
            console.log('[HomeScreen] Failed to fetch product stats:', error);
        } finally {
            setRefreshing(false);
        }
    }, []);

    useFocusEffect(
        useCallback(() => {
            fetchDashboardStats();
        }, [fetchDashboardStats])
    );

    return (
        <SafeAreaView style={styles.safeArea}>
            <NetworkBanner />
            <SpeakOnMount text="सामान बेचने के लिए नीचे का माइक बटन दबाएं और बोलकर बतायें (Press mic button below to list products by speaking)" />

            <ScrollView
                contentContainerStyle={styles.container}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={fetchDashboardStats} />
                }
            >
                {/* Welcome Header */}
                <View style={styles.header}>
                    <Text style={styles.greeting}>नमस्ते (Hello),</Text>
                    <Text style={styles.artisanName}>{artisan?.name || 'कारीगर साथी'}</Text>
                </View>

                {/* Core Stats Overview */}
                <View style={styles.statsRow}>
                    <View style={styles.statCard}>
                        <Package size={28} color={colors.accent} />
                        <Text style={styles.statNumber}>{productCount}</Text>
                        <Text style={styles.statLabel}>कुल सामान (Total)</Text>
                    </View>

                    <View style={styles.statCard}>
                        <Globe size={28} color={colors.success} />
                        <Text style={styles.statNumber}>{ondcCount}</Text>
                        <Text style={styles.statLabel}>ONDC पर लाइव (Live)</Text>
                    </View>
                </View>

                {/* Primary Hero CTA Block */}
                <View style={styles.heroCard}>
                    <View style={styles.heroHeader}>
                        <Mic size={32} color={colors.primary} />
                        <Text style={styles.heroTitle}>नया सामान जोड़ें (Add Item)</Text>
                    </View>
                    <Text style={styles.heroDescription}>
                        लिखने की ज़रूरत नहीं है। बस बोलकर और फोटो खींचकर सामान ONDC पर बेचें।
                    </Text>

                    <BigButton
                        title="बोलकर सामान जोड़ें (Start Listing)"
                        icon={PlusCircle}
                        size="large"
                        variant="primary"
                        onPress={() => router.push('/listing/voice')}
                    />
                </View>

                {/* Quick Nav Button to Catalog */}
                <BigButton
                    title="मेरा सामान देखें (View Catalog)"
                    icon={Package}
                    variant="outline"
                    onPress={() => router.push('/(tabs)/catalog')}
                />
            </ScrollView>

            <FloatingMicHelp helpText="सामान जोड़ने के लिए काले बटन को दबाएं और आवाज़ में विवरण दें।" />
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    safeArea: {
        flex: 1,
        backgroundColor: colors.background,
    },
    container: {
        padding: layout.spacing.lg,
        paddingBottom: 100,
    },
    header: {
        marginBottom: layout.spacing.lg,
    },
    greeting: {
        fontSize: typography.sizes.bodyLarge,
        color: colors.textSecondary,
    },
    artisanName: {
        fontSize: typography.sizes.heroTitle,
        fontWeight: '800',
        color: colors.textPrimary,
    },
    statsRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: layout.spacing.lg,
    },
    statCard: {
        flex: 0.48,
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderWidth: 1,
        borderRadius: layout.borderRadius.md,
        padding: layout.spacing.md,
        alignItems: 'center',
    },
    statNumber: {
        fontSize: typography.sizes.heroTitle,
        fontWeight: '800',
        color: colors.textPrimary,
        marginVertical: layout.spacing.xs,
    },
    statLabel: {
        fontSize: typography.sizes.caption,
        color: colors.textSecondary,
        fontWeight: '600',
    },
    heroCard: {
        backgroundColor: colors.primarySoft,
        borderRadius: layout.borderRadius.lg,
        padding: layout.spacing.lg,
        marginBottom: layout.spacing.lg,
        borderWidth: 1,
        borderColor: colors.border,
    },
    heroHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: layout.spacing.xs,
    },
    heroTitle: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '800',
        color: colors.textPrimary,
        marginLeft: layout.spacing.xs,
    },
    heroDescription: {
        fontSize: typography.sizes.body,
        color: colors.textSecondary,
        marginBottom: layout.spacing.lg,
        lineHeight: 22,
    },
});
import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import QRCode from 'react-native-qrcode-svg';
import { CheckCircle2, Package, Home } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';
import { SpeakOnMount } from '../../components/SpeakOnMount';
import { BigButton } from '../../components/BigButton';
import { NetworkBanner } from '../../components/NetworkBanner';
import { useListingStore } from '../../stores/listingStore';
import { api } from '../../services/api';

export default function ListingSuccessScreen() {
    const router = useRouter();
    const { createdProductId, resetListing } = useListingStore();
    const [qrUrl, setQrUrl] = useState<string>('');

    useEffect(() => {
        const fetchQrPayload = async () => {
            if (!createdProductId) return;
            try {
                const response = await api.get<{ link_url?: string }>(
                    `/qr/product/${createdProductId}/link`
                );
                setQrUrl(response.data.link_url || `https://kalakriti.app/qr/${createdProductId}`);
            } catch {
                setQrUrl(`https://kalakriti.app/qr/${createdProductId}`);
            }
        };

        fetchQrPayload();
    }, [createdProductId]);

    const handleFinish = (targetRoute: '/(tabs)/catalog' | '/(tabs)') => {
        resetListing();
        router.replace(targetRoute);
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <NetworkBanner />
            <SpeakOnMount text="बधाई हो! आपका सामान जुड़ गया है और QR कोड तैयार है।" />

            <ScrollView contentContainerStyle={styles.container}>
                <View style={styles.successBadge}>
                    <CheckCircle2 size={64} color={colors.success} />
                </View>

                <Text style={styles.title}>बधाई हो! (Success)</Text>
                <Text style={styles.subtitle}>
                    आपका सामान ONDC नेटवर्क से जुड़ गया है।
                </Text>

                {/* Generated QR Code Card */}
                <View style={styles.qrCard}>
                    <Text style={styles.qrHeader}>सामान का QR कोड</Text>
                    <Text style={styles.qrSub}>
                        खरीदार इसे स्कैन करके सीधा सामान खरीद सकते हैं
                    </Text>

                    <View style={styles.qrWrapper}>
                        {qrUrl ? (
                            <QRCode value={qrUrl} size={180} />
                        ) : (
                            <Text>QR लोड हो रहा है...</Text>
                        )}
                    </View>
                </View>

                <BigButton
                    title="कैटलॉग देखें (View Catalog)"
                    icon={Package}
                    size="large"
                    onPress={() => handleFinish('/(tabs)/catalog')}
                />

                <BigButton
                    title="मुख्य पृष्ठ (Home)"
                    icon={Home}
                    variant="outline"
                    onPress={() => handleFinish('/(tabs)')}
                />
            </ScrollView>
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
        alignItems: 'center',
        justifyContent: 'center',
    },
    successBadge: {
        marginVertical: layout.spacing.md,
    },
    title: {
        fontSize: typography.sizes.heroTitle,
        fontWeight: '800',
        color: colors.textPrimary,
    },
    subtitle: {
        fontSize: typography.sizes.bodyLarge,
        color: colors.textSecondary,
        textAlign: 'center',
        marginVertical: layout.spacing.xs,
        marginBottom: layout.spacing.lg,
    },
    qrCard: {
        backgroundColor: colors.surface,
        borderRadius: layout.borderRadius.lg,
        borderWidth: 1,
        borderColor: colors.border,
        padding: layout.spacing.lg,
        alignItems: 'center',
        width: '100%',
        marginBottom: layout.spacing.xl,
    },
    qrHeader: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '800',
        color: colors.textPrimary,
    },
    qrSub: {
        fontSize: typography.sizes.caption,
        color: colors.textSecondary,
        textAlign: 'center',
        marginBottom: layout.spacing.md,
    },
    qrWrapper: {
        padding: layout.spacing.md,
        backgroundColor: '#FFFFFF',
        borderRadius: layout.borderRadius.md,
        borderWidth: 1,
        borderColor: colors.border,
    },
});
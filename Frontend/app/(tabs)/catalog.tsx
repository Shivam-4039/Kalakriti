import React, { useCallback, useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    FlatList,
    RefreshControl,
    Modal,
    TouchableOpacity,
    Alert,
} from 'react-native';
import { useFocusEffect } from 'expo-router';
import QRCode from 'react-native-qrcode-svg';
import { Package, X, Plus } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';
import { ProductCard, Product } from '../../components/ProductCard';
import { SpeakOnMount } from '../../components/SpeakOnMount';
import { FloatingMicHelp } from '../../components/FloatingMicHelp';
import { BigButton } from '../../components/BigButton';
import { NetworkBanner } from '../../components/NetworkBanner';
import { api } from '../../services/api';
import { useRouter } from 'expo-router';

export default function CatalogScreen() {
    const router = useRouter();
    const [products, setProducts] = useState<Product[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [activeQrPayload, setActiveQrPayload] = useState<{ id: string; title: string; url: string } | null>(null);

    const fetchProducts = useCallback(async () => {
        try {
            setIsLoading(true);
            const response = await api.get<{ items: Product[] }>('/products?limit=50');
            setProducts(response.data.items || []);
        } catch (error) {
            console.error('[CatalogScreen] Failed to fetch products:', error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useFocusEffect(
        useCallback(() => {
            fetchProducts();
        }, [fetchProducts])
    );

    const handlePublishOndc = async (productId: string) => {
        try {
            await api.post(`/ondc/publish/${productId}`);
            Alert.alert('सफलता (Success)', 'आपका सामान ONDC पर लाइव हो गया है!');
            fetchProducts();
        } catch {
            Alert.alert('त्रुटि (Error)', 'ONDC पर पब्लिश नहीं हो सका। फिर कोशिश करें।');
        }
    };

    const handleShowQR = async (product: Product) => {
        try {
            const response = await api.get<{ qr_payload?: string; link_url?: string }>(`/qr/product/${product.id}/link`);
            const linkUrl = response.data.link_url || `https://kalakriti.app/qr/${product.id}`;
            setActiveQrPayload({ id: product.id, title: product.title, url: linkUrl });
        } catch {
            // Fallback QR link formatting
            setActiveQrPayload({
                id: product.id,
                title: product.title,
                url: `https://kalakriti.app/qr/${product.id}`,
            });
        }
    };

    const handleDeleteProduct = (productId: string) => {
        Alert.alert(
            'हटाएं (Delete)',
            'क्या आप इस सामान को हटाना चाहते हैं?',
            [
                { text: 'नहीं (Cancel)', style: 'cancel' },
                {
                    text: 'हाँ (Delete)',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            await api.delete(`/products/${productId}`);
                            fetchProducts();
                        } catch {
                            Alert.alert('त्रुटि (Error)', 'सामान नहीं हटाया जा सका।');
                        }
                    },
                },
            ]
        );
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <NetworkBanner />
            <SpeakOnMount text="यह आपका कैटलॉग है। यहाँ आपके सभी जोड़े गए सामान दिखेंगे।" />

            <View style={styles.header}>
                <Text style={styles.title}>मेरा सामान (Catalog)</Text>
            </View>

            <FlatList
                data={products}
                keyExtractor={(item) => item.id}
                contentContainerStyle={styles.listContainer}
                refreshControl={
                    <RefreshControl refreshing={isLoading} onRefresh={fetchProducts} />
                }
                renderItem={({ item }) => (
                    <ProductCard
                        product={item}
                        onPress={() => { }}
                        onPublish={() => handlePublishOndc(item.id)}
                        onShowQR={() => handleShowQR(item)}
                        onDelete={() => handleDeleteProduct(item.id)}
                    />
                )}
                ListEmptyComponent={
                    !isLoading ? (
                        <View style={styles.emptyContainer}>
                            <Package size={64} color={colors.textSecondary} />
                            <Text style={styles.emptyTitle}>कोई सामान नहीं मिला</Text>
                            <Text style={styles.emptySubtitle}>
                                अपना पहला सामान जोड़ने के लिए नीचे दिए बटन पर क्लिक करें।
                            </Text>
                            <BigButton
                                title="सामान जोड़ें (Add Product)"
                                icon={Plus}
                                onPress={() => router.push('/listing/voice')}
                            />
                        </View>
                    ) : null
                }
            />

            {/* QR Phygital Bridge Modal */}
            <Modal
                visible={Boolean(activeQrPayload)}
                transparent
                animationType="fade"
                onRequestClose={() => setActiveQrPayload(null)}
            >
                <View style={styles.modalOverlay}>
                    <View style={styles.modalContent}>
                        <TouchableOpacity
                            style={styles.closeBtn}
                            onPress={() => setActiveQrPayload(null)}
                        >
                            <X size={28} color={colors.textPrimary} />
                        </TouchableOpacity>

                        <Text style={styles.qrTitle}>{activeQrPayload?.title}</Text>
                        <Text style={styles.qrSubtitle}>खरीदार इसे स्कैन करके सीधा सामान खरीद सकते हैं</Text>

                        <View style={styles.qrWrapper}>
                            {activeQrPayload?.url && (
                                <QRCode value={activeQrPayload.url} size={200} />
                            )}
                        </View>

                        <BigButton
                            title="बंद करें (Close)"
                            variant="outline"
                            onPress={() => setActiveQrPayload(null)}
                        />
                    </View>
                </View>
            </Modal>

            <FloatingMicHelp helpText="यहाँ आपके जोड़े गए सभी सामान की सूची है।" />
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    safeArea: {
        flex: 1,
        backgroundColor: colors.background,
    },
    header: {
        padding: layout.spacing.lg,
        backgroundColor: colors.surface,
        borderBottomWidth: 1,
        borderBottomColor: colors.border,
    },
    title: {
        fontSize: typography.sizes.screenTitle,
        fontWeight: '800',
        color: colors.textPrimary,
    },
    listContainer: {
        padding: layout.spacing.lg,
        paddingBottom: 100,
    },
    emptyContainer: {
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: layout.spacing.xl,
    },
    emptyTitle: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '700',
        color: colors.textPrimary,
        marginTop: layout.spacing.md,
    },
    emptySubtitle: {
        fontSize: typography.sizes.body,
        color: colors.textSecondary,
        textAlign: 'center',
        marginVertical: layout.spacing.sm,
        marginBottom: layout.spacing.lg,
    },
    modalOverlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.6)',
        justifyContent: 'center',
        alignItems: 'center',
        padding: layout.spacing.lg,
    },
    modalContent: {
        backgroundColor: colors.surface,
        borderRadius: layout.borderRadius.lg,
        padding: layout.spacing.lg,
        width: '100%',
        alignItems: 'center',
    },
    closeBtn: {
        alignSelf: 'flex-end',
        padding: layout.spacing.xs,
    },
    qrTitle: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '800',
        color: colors.textPrimary,
        textAlign: 'center',
    },
    qrSubtitle: {
        fontSize: typography.sizes.caption,
        color: colors.textSecondary,
        textAlign: 'center',
        marginBottom: layout.spacing.lg,
    },
    qrWrapper: {
        padding: layout.spacing.lg,
        backgroundColor: '#FFFFFF',
        borderRadius: layout.borderRadius.md,
        borderWidth: 1,
        borderColor: colors.border,
        marginBottom: layout.spacing.lg,
    },
});
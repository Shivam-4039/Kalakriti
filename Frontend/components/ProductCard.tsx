import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { QrCode, Globe, Trash2 } from 'lucide-react-native';
import { colors, layout, typography } from '../theme';
import { StatusPill, type StatusType } from './StatusPill';

export interface Product {
    id: string;
    title: string;
    price: number;
    image_url?: string;
    ondc_status?: StatusType;
    craft_type?: string;
}

interface ProductCardProps {
    product: Product;
    onPress: () => void;
    onPublish?: () => void;
    onShowQR?: () => void;
    onDelete?: () => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({
    product,
    onPress,
    onPublish,
    onShowQR,
    onDelete,
}) => {
    return (
        <TouchableOpacity
            activeOpacity={0.8}
            onPress={onPress}
            style={styles.card}
        >
            <Image
                source={
                    product.image_url
                        ? { uri: product.image_url }
                        : require('../assets/images/icon.png')
                }
                style={styles.image}
                resizeMode="cover"
            />

            <View style={styles.content}>
                <View style={styles.headerRow}>
                    <Text style={styles.title} numberOfLines={1}>
                        {product.title}
                    </Text>
                    <StatusPill status={product.ondc_status || 'draft'} />
                </View>

                <Text style={styles.price}>
                    ₹{product.price ? product.price.toLocaleString('en-IN') : '0'}
                </Text>

                {product.craft_type ? (
                    <Text style={styles.craft}>{product.craft_type}</Text>
                ) : null}

                {/* Action Buttons Row */}
                <View style={styles.actionRow}>
                    {onShowQR && (
                        <TouchableOpacity
                            onPress={onShowQR}
                            style={styles.actionButton}
                        >
                            <QrCode size={20} color={colors.accent} />
                            <Text style={styles.actionTextAccent}>QR कोड</Text>
                        </TouchableOpacity>
                    )}

                    {onPublish && product.ondc_status !== 'published' && (
                        <TouchableOpacity
                            onPress={onPublish}
                            style={[styles.actionButton, styles.publishBtn]}
                        >
                            <Globe size={18} color="#FFFFFF" />
                            <Text style={styles.publishText}>ONDC पर बेचें</Text>
                        </TouchableOpacity>
                    )}

                    {onDelete && (
                        <TouchableOpacity
                            onPress={onDelete}
                            style={styles.iconOnlyButton}
                        >
                            <Trash2 size={20} color={colors.error} />
                        </TouchableOpacity>
                    )}
                </View>
            </View>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: colors.surface,
        borderRadius: layout.borderRadius.md,
        borderWidth: 1,
        borderColor: colors.border,
        marginBottom: layout.spacing.md,
        overflow: 'hidden',
        flexDirection: 'row',
    },
    image: {
        width: 110,
        height: 120,
        backgroundColor: colors.primarySoft,
    },
    content: {
        flex: 1,
        padding: layout.spacing.md,
        justifyContent: 'space-between',
    },
    headerRow: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    title: {
        fontSize: typography.sizes.body,
        fontWeight: '700',
        color: colors.textPrimary,
        flex: 1,
        marginRight: layout.spacing.xs,
    },
    price: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '800',
        color: colors.primary,
        marginVertical: layout.spacing.xs,
    },
    craft: {
        fontSize: typography.sizes.caption,
        color: colors.textSecondary,
    },
    actionRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginTop: layout.spacing.sm,
        gap: layout.spacing.xs,
    },
    actionButton: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 6,
        paddingHorizontal: 10,
        borderRadius: layout.borderRadius.sm,
        backgroundColor: colors.primarySoft,
    },
    actionTextAccent: {
        fontSize: typography.sizes.caption,
        fontWeight: '700',
        color: colors.accent,
        marginLeft: 4,
    },
    publishBtn: {
        backgroundColor: colors.success,
    },
    publishText: {
        fontSize: typography.sizes.caption,
        fontWeight: '700',
        color: '#FFFFFF',
        marginLeft: 4,
    },
    iconOnlyButton: {
        padding: 6,
        marginLeft: 'auto',
    },
});

export default ProductCard;
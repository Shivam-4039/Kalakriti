import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { AlertTriangle, RefreshCw } from 'lucide-react-native';
import { colors, layout, typography } from '../theme';
import { useTTS } from '../hooks/useTTS';

interface ErrorSpeakerProps {
    message: string;
    speakMessage?: string;
    onRetry?: () => void;
}

export const ErrorSpeaker: React.FC<ErrorSpeakerProps> = ({
    message,
    speakMessage,
    onRetry,
}) => {
    const { speak } = useTTS();

    useEffect(() => {
        const speechText = speakMessage || message || 'कुछ गड़बड़ हुई है, फिर से कोशिश करें (Error occurred)';
        speak(speechText);
    }, [message, speakMessage, speak]);

    return (
        <View style={styles.card}>
            <View style={styles.contentRow}>
                <AlertTriangle size={36} color={colors.error} style={styles.icon} />
                <View style={styles.textContainer}>
                    <Text style={styles.title}>ध्यान दें (Attention)</Text>
                    <Text style={styles.message}>{message}</Text>
                </View>
            </View>

            {onRetry && (
                <TouchableOpacity activeOpacity={0.8} onPress={onRetry} style={styles.retryBtn}>
                    <RefreshCw size={20} color="#FFFFFF" />
                    <Text style={styles.retryText}>फिर से कोशिश करें (Retry)</Text>
                </TouchableOpacity>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: colors.errorSoft,
        borderColor: colors.error,
        borderWidth: 1,
        borderRadius: layout.borderRadius.md,
        padding: layout.spacing.md,
        marginVertical: layout.spacing.md,
    },
    contentRow: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    icon: {
        marginRight: layout.spacing.md,
    },
    textContainer: {
        flex: 1,
    },
    title: {
        fontSize: typography.sizes.body,
        fontWeight: '700',
        color: colors.error,
    },
    message: {
        fontSize: typography.sizes.body,
        color: colors.textPrimary,
        marginTop: 2,
    },
    retryBtn: {
        backgroundColor: colors.error,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        paddingVertical: layout.spacing.sm,
        borderRadius: layout.borderRadius.sm,
        marginTop: layout.spacing.md,
        minHeight: layout.touchTarget.standard - 8,
    },
    retryText: {
        color: '#FFFFFF',
        fontWeight: '700',
        fontSize: typography.sizes.body,
        marginLeft: layout.spacing.xs,
    },
});
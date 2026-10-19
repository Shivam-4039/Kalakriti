import React from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { HelpCircle, Home } from 'lucide-react-native';
import { colors, layout, typography } from '../theme';
import { BigButton } from '../components/BigButton';
import { SpeakOnMount } from '../components/SpeakOnMount';

export default function NotFoundScreen() {
    const router = useRouter();

    return (
        <SafeAreaView style={styles.safeArea}>
            <SpeakOnMount text="यह पेज नहीं मिला। मुख्य स्क्रीन पर वापस जाने के लिए नीचे का बटन दबाएं।" />

            <View style={styles.container}>
                <HelpCircle size={80} color={colors.accent} style={styles.icon} />

                <Text style={styles.title}>पेज नहीं मिला (Page Not Found)</Text>
                <Text style={styles.subtitle}>
                    आप जिस पेज को ढूंढ रहे हैं वह मौजूद नहीं है या हटा दिया गया है।
                </Text>

                <BigButton
                    title="मुख्य स्क्रीन पर जाएं (Go Home)"
                    icon={Home}
                    size="large"
                    onPress={() => router.replace('/(tabs)')}
                />
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    safeArea: {
        flex: 1,
        backgroundColor: colors.background,
    },
    container: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        padding: layout.spacing.lg,
    },
    icon: {
        marginBottom: layout.spacing.lg,
    },
    title: {
        fontSize: typography.sizes.screenTitle,
        fontWeight: '800',
        color: colors.textPrimary,
        textAlign: 'center',
    },
    subtitle: {
        fontSize: typography.sizes.body,
        color: colors.textSecondary,
        textAlign: 'center',
        marginTop: layout.spacing.xs,
        marginBottom: layout.spacing.xl,
    },
});
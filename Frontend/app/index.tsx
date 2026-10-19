import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView } from 'react-native';
import { useRouter } from 'expo-router';
import { Globe, ArrowRight } from 'lucide-react-native';
import { colors, layout, typography } from '../theme';
import { SUPPORTED_LANGUAGES, Language } from '../constants/languages';
import { LanguageChip } from '../components/LanguageChip';
import { BigButton } from '../components/BigButton';
import { SpeakOnMount } from '../components/SpeakOnMount';
import { NetworkBanner } from '../components/NetworkBanner';
import { useAuthStore } from '../stores/authStore';

export default function IndexScreen() {
    const router = useRouter();
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
    const artisan = useAuthStore((state) => state.artisan);
    const updateProfile = useAuthStore((state) => state.updateProfile);

    const [selectedLang, setSelectedLang] = useState<Language>(
        SUPPORTED_LANGUAGES[0]
    );

    useEffect(() => {
        // Redirect existing active sessions directly to dashboard tabs
        if (isAuthenticated) {
            router.replace('/(tabs)');
        }
    }, [isAuthenticated, router]);

    const handleSelectLanguage = (lang: Language) => {
        setSelectedLang(lang);
    };

    const handleContinue = async () => {
        if (artisan) {
            await updateProfile({ language_code: selectedLang.code });
        }
        router.push('/(auth)/login');
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <NetworkBanner />
            <SpeakOnMount text="कलाकृति में आपका स्वागत है। अपनी भाषा चुनें। (Welcome to Kalakriti. Choose your language.)" />

            <ScrollView contentContainerStyle={styles.container}>
                <View style={styles.header}>
                    <View style={styles.logoBadge}>
                        <Globe size={40} color={colors.accent} />
                    </View>
                    <Text style={styles.title}>कलाकृति</Text>
                    <Text style={styles.subtitle}>KALAKRITI</Text>
                    <Text style={styles.instruction}>
                        अपनी भाषा चुनें / Select Language
                    </Text>
                </View>

                {/* Language Grid */}
                <View style={styles.grid}>
                    {SUPPORTED_LANGUAGES.map((lang) => (
                        <LanguageChip
                            key={lang.code}
                            language={lang}
                            isSelected={selectedLang.code === lang.code}
                            onSelect={handleSelectLanguage}
                        />
                    ))}
                </View>
            </ScrollView>

            {/* Primary Action Sticky Footer */}
            <View style={styles.footer}>
                <BigButton
                    title="आगे बढ़ें (Continue)"
                    icon={ArrowRight}
                    size="large"
                    onPress={handleContinue}
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
        padding: layout.spacing.lg,
        paddingBottom: 100,
    },
    header: {
        alignItems: 'center',
        marginVertical: layout.spacing.lg,
    },
    logoBadge: {
        width: 80,
        height: 80,
        borderRadius: layout.borderRadius.full,
        backgroundColor: colors.accentSoft,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: layout.spacing.md,
    },
    title: {
        fontSize: typography.sizes.heroTitle,
        fontWeight: '800',
        color: colors.textPrimary,
    },
    subtitle: {
        fontSize: typography.sizes.caption,
        fontWeight: '700',
        color: colors.textSecondary,
        letterSpacing: 2,
        marginBottom: layout.spacing.md,
    },
    instruction: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '700',
        color: colors.primary,
        marginTop: layout.spacing.sm,
    },
    grid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        marginTop: layout.spacing.md,
    },
    footer: {
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        backgroundColor: colors.surface,
        padding: layout.spacing.md,
        borderTopWidth: 1,
        borderTopColor: colors.border,
    },
});
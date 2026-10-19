import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    ScrollView,
    TextInput,
    Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { User, LogOut, Check, ShieldCheck } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';
import { BigButton } from '../../components/BigButton';
import { SpeakOnMount } from '../../components/SpeakOnMount';
import { FloatingMicHelp } from '../../components/FloatingMicHelp';
import { SUPPORTED_LANGUAGES, Language } from '../../constants/languages';
import { LanguageChip } from '../../components/LanguageChip';
import { NetworkBanner } from '../../components/NetworkBanner';
import { useAuthStore } from '../../stores/authStore';

export default function ProfileScreen() {
    const router = useRouter();
    const { artisan, updateProfile, logout, isLoading } = useAuthStore();

    const [name, setName] = useState<string>(artisan?.name || '');
    const [craftType, setCraftType] = useState<string>(artisan?.craft_type || '');
    const [selectedLang, setSelectedLang] = useState<string>(
        artisan?.language_code || 'hi'
    );

    const handleSave = async () => {
        const success = await updateProfile({
            name,
            craft_type: craftType,
            language_code: selectedLang,
        });

        if (success) {
            Alert.alert('सफलता (Success)', 'प्रोफ़ाइल अपडेट हो गई है!');
        } else {
            Alert.alert('त्रुटि (Error)', 'प्रोफ़ाइल अपडेट नहीं हो सकी।');
        }
    };

    const handleLogout = () => {
        Alert.alert(
            'लॉगआउट (Logout)',
            'क्या आप बाहर निकलना चाहते हैं?',
            [
                { text: 'नहीं (Cancel)', style: 'cancel' },
                {
                    text: 'हाँ (Logout)',
                    style: 'destructive',
                    onPress: async () => {
                        await logout();
                        router.replace('/');
                    },
                },
            ]
        );
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <NetworkBanner />
            <SpeakOnMount text="यह आपकी प्रोफाइल है। यहाँ आप नाम और भाषा बदल सकते हैं।" />

            <ScrollView contentContainerStyle={styles.container}>
                <View style={styles.header}>
                    <View style={styles.avatar}>
                        <User size={48} color={colors.primary} />
                    </View>
                    <Text style={styles.phoneText}>{artisan?.phone_number}</Text>
                </View>

                {/* Free Assurance Banner */}
                <View style={styles.freeBanner}>
                    <ShieldCheck size={24} color={colors.success} />
                    <Text style={styles.freeBannerText}>
                        कलाकृति कारीगरों के लिए 100% मुफ्त है।
                    </Text>
                </View>

                {/* Profile Form */}
                <View style={styles.formGroup}>
                    <Text style={styles.label}>आपका नाम (Name)</Text>
                    <TextInput
                        style={styles.input}
                        value={name}
                        onChangeText={setName}
                        placeholder="नाम लिखें..."
                    />
                </View>

                <View style={styles.formGroup}>
                    <Text style={styles.label}>हस्तकला प्रकार (Craft Type)</Text>
                    <TextInput
                        style={styles.input}
                        value={craftType}
                        onChangeText={setCraftType}
                        placeholder="जैसे: टेराकोटा, लकड़ी की नक्काशी"
                    />
                </View>

                {/* Language Selection */}
                <Text style={styles.sectionTitle}>भाषा बदलें (Select Language)</Text>
                <View style={styles.langGrid}>
                    {SUPPORTED_LANGUAGES.map((lang: Language) => (
                        <LanguageChip
                            key={lang.code}
                            language={lang}
                            isSelected={selectedLang === lang.code}
                            onSelect={(selected) => setSelectedLang(selected.code)}
                        />
                    ))}
                </View>

                <BigButton
                    title="प्रोफाइल सेव करें (Save Profile)"
                    icon={Check}
                    size="large"
                    loading={isLoading}
                    onPress={handleSave}
                />

                <View style={styles.logoutWrapper}>
                    <BigButton
                        title="लॉगआउट करें (Logout)"
                        icon={LogOut}
                        variant="danger"
                        onPress={handleLogout}
                    />
                </View>
            </ScrollView>

            <FloatingMicHelp helpText="अपनी प्रोफाइल जानकारी बदलने के बाद सेव बटन दबाएं।" />
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
        paddingBottom: 120,
    },
    header: {
        alignItems: 'center',
        marginVertical: layout.spacing.md,
    },
    avatar: {
        width: 80,
        height: 80,
        borderRadius: layout.borderRadius.full,
        backgroundColor: colors.primarySoft,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: layout.spacing.sm,
    },
    phoneText: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '800',
        color: colors.textPrimary,
    },
    freeBanner: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: colors.successSoft,
        padding: layout.spacing.md,
        borderRadius: layout.borderRadius.md,
        marginBottom: layout.spacing.lg,
    },
    freeBannerText: {
        fontSize: typography.sizes.body,
        fontWeight: '700',
        color: colors.success,
        marginLeft: layout.spacing.sm,
        flex: 1,
    },
    formGroup: {
        marginBottom: layout.spacing.md,
    },
    label: {
        fontSize: typography.sizes.body,
        fontWeight: '700',
        color: colors.textPrimary,
        marginBottom: layout.spacing.xs,
    },
    input: {
        backgroundColor: colors.surface,
        borderWidth: 1,
        borderColor: colors.border,
        borderRadius: layout.borderRadius.md,
        paddingHorizontal: layout.spacing.md,
        height: layout.touchTarget.standard,
        fontSize: typography.sizes.body,
        color: colors.textPrimary,
    },
    sectionTitle: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '800',
        color: colors.textPrimary,
        marginTop: layout.spacing.md,
        marginBottom: layout.spacing.sm,
    },
    langGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        marginBottom: layout.spacing.lg,
    },
    logoutWrapper: {
        marginTop: layout.spacing.xl,
    },
});
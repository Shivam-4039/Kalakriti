import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    TextInput,
    TouchableOpacity,
    KeyboardAvoidingView,
    Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Phone, ArrowRight, PlayCircle } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';
import { BigButton } from '../../components/BigButton';
import { SpeakOnMount } from '../../components/SpeakOnMount';
import { ErrorSpeaker } from '../../components/ErrorSpeaker';
import { useAuthStore } from '../../stores/authStore';

export default function LoginScreen() {
    const router = useRouter();
    const { sendOtp, enableDemoMode, isLoading } = useAuthStore();
    const [phoneNumber, setPhoneNumber] = useState<string>('');
    const [errorMessage, setErrorMessage] = useState<string>('');

    const handleSendOtp = async () => {
        setErrorMessage('');
        const cleanNumber = phoneNumber.replace(/\D/g, '');

        if (cleanNumber.length !== 10) {
            setErrorMessage('कृपया 10 अंकों का मोबाइल नंबर दर्ज करें (Enter 10-digit number)');
            return;
        }

        const fullPhone = `+91${cleanNumber}`;
        const success = await sendOtp(fullPhone);

        if (success) {
            router.push({ pathname: '/(auth)/otp', params: { phone: fullPhone } });
        } else {
            setErrorMessage('OTP भेजने में समस्या हुई। फिर कोशिश करें। (Failed to send OTP)');
        }
    };

    const handleDemoBypass = async () => {
        setErrorMessage('');
        await enableDemoMode();
        router.replace('/(tabs)');
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <SpeakOnMount text="अपना 10 अंकों का मोबाइल नंबर दर्ज करें (Enter your 10 digit mobile number)" />

            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                style={styles.container}
            >
                <View style={styles.header}>
                    <Text style={styles.title}>लॉगिन करें (Login)</Text>
                    <Text style={styles.subtitle}>
                        ओटीपी (OTP) पाने के लिए अपना फोन नंबर डालें
                    </Text>
                </View>

                {errorMessage ? <ErrorSpeaker message={errorMessage} /> : null}

                <View style={styles.inputContainer}>
                    <Text style={styles.countryCode}>+91</Text>
                    <TextInput
                        style={styles.input}
                        placeholder="9876543210"
                        placeholderTextColor={colors.textSecondary}
                        keyboardType="phone-pad"
                        maxLength={10}
                        value={phoneNumber}
                        onChangeText={setPhoneNumber}
                        autoFocus
                    />
                    <Phone size={24} color={colors.textSecondary} />
                </View>

                <BigButton
                    title="ओटीपी (OTP) भेजें"
                    icon={ArrowRight}
                    size="large"
                    loading={isLoading}
                    onPress={handleSendOtp}
                />

                {/* Demo Bypass Option for SIH Jury Evaluation */}
                <View style={styles.demoSection}>
                    <Text style={styles.demoDivider}>— या / OR —</Text>
                    <TouchableOpacity
                        activeOpacity={0.8}
                        onPress={handleDemoBypass}
                        style={styles.demoButton}
                    >
                        <PlayCircle size={24} color={colors.accent} />
                        <Text style={styles.demoButtonText}>
                            डेमो लॉगिन (Quick Demo Login)
                        </Text>
                    </TouchableOpacity>
                </View>
            </KeyboardAvoidingView>
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
        padding: layout.spacing.lg,
        justifyContent: 'center',
    },
    header: {
        marginBottom: layout.spacing.xl,
    },
    title: {
        fontSize: typography.sizes.heroTitle,
        fontWeight: '800',
        color: colors.textPrimary,
    },
    subtitle: {
        fontSize: typography.sizes.bodyLarge,
        color: colors.textSecondary,
        marginTop: layout.spacing.xs,
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: colors.surface,
        borderWidth: 2,
        borderColor: colors.border,
        borderRadius: layout.borderRadius.md,
        paddingHorizontal: layout.spacing.md,
        height: layout.touchTarget.primary,
        marginBottom: layout.spacing.lg,
    },
    countryCode: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '700',
        color: colors.textPrimary,
        marginRight: layout.spacing.sm,
    },
    input: {
        flex: 1,
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '700',
        color: colors.textPrimary,
    },
    demoSection: {
        marginTop: layout.spacing.xl,
        alignItems: 'center',
    },
    demoDivider: {
        fontSize: typography.sizes.caption,
        color: colors.textSecondary,
        marginBottom: layout.spacing.md,
    },
    demoButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: colors.accentSoft,
        paddingVertical: layout.spacing.md,
        paddingHorizontal: layout.spacing.lg,
        borderRadius: layout.borderRadius.md,
        minHeight: layout.touchTarget.standard,
    },
    demoButtonText: {
        fontSize: typography.sizes.body,
        fontWeight: '700',
        color: colors.accent,
        marginLeft: layout.spacing.sm,
    },
});
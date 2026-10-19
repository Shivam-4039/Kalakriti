import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    TextInput,
    TouchableOpacity,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { CheckCircle2, ArrowLeft } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';
import { BigButton } from '../../components/BigButton';
import { SpeakOnMount } from '../../components/SpeakOnMount';
import { ErrorSpeaker } from '../../components/ErrorSpeaker';
import { useAuthStore } from '../../stores/authStore';

export default function OtpScreen() {
    const router = useRouter();
    const params = useLocalSearchParams<{ phone?: string }>();
    const phone = params.phone || '';

    const { verifyOtp, isLoading } = useAuthStore();
    const [otp, setOtp] = useState<string>('');
    const [errorMessage, setErrorMessage] = useState<string>('');

    const handleVerify = async () => {
        setErrorMessage('');
        if (otp.length !== 6) {
            setErrorMessage('कृपया 6 अंकों का OTP दर्ज करें (Enter 6-digit OTP)');
            return;
        }

        const success = await verifyOtp(phone, otp);

        if (success) {
            router.replace('/(tabs)');
        } else {
            setErrorMessage('गलत OTP है। फिर से प्रयास करें (Incorrect OTP)');
        }
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <SpeakOnMount text="फोन पर आया 6 अंकों का ओटीपी दर्ज करें (Enter 6 digit OTP received on phone)" />

            <View style={styles.container}>
                <TouchableOpacity
                    onPress={() => router.back()}
                    style={styles.backButton}
                >
                    <ArrowLeft size={28} color={colors.textPrimary} />
                </TouchableOpacity>

                <View style={styles.header}>
                    <Text style={styles.title}>ओटीपी दर्ज करें (OTP)</Text>
                    <Text style={styles.subtitle}>
                        {phone} पर भेजा गया 6 अंकों का कोड डालें
                    </Text>
                </View>

                {errorMessage ? <ErrorSpeaker message={errorMessage} /> : null}

                <View style={styles.otpContainer}>
                    <TextInput
                        style={styles.otpInput}
                        placeholder="123456"
                        placeholderTextColor={colors.textSecondary}
                        keyboardType="number-pad"
                        maxLength={6}
                        value={otp}
                        onChangeText={setOtp}
                        autoFocus
                    />
                </View>

                <BigButton
                    title="सत्यापित करें (Verify)"
                    icon={CheckCircle2}
                    size="large"
                    loading={isLoading}
                    onPress={handleVerify}
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
        padding: layout.spacing.lg,
        justifyContent: 'center',
    },
    backButton: {
        position: 'absolute',
        top: layout.spacing.lg,
        left: layout.spacing.lg,
        padding: layout.spacing.xs,
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
    otpContainer: {
        backgroundColor: colors.surface,
        borderWidth: 2,
        borderColor: colors.border,
        borderRadius: layout.borderRadius.md,
        height: layout.touchTarget.primary,
        justifyContent: 'center',
        paddingHorizontal: layout.spacing.md,
        marginBottom: layout.spacing.xl,
    },
    otpInput: {
        fontSize: typography.sizes.heroTitle,
        fontWeight: '800',
        letterSpacing: 12,
        textAlign: 'center',
        color: colors.primary,
    },
});
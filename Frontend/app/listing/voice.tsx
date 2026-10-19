import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { ArrowLeft, ArrowRight } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';
import { VoiceButton } from '../../components/VoiceButton';
import { StepIndicator } from '../../components/StepIndicator';
import { SpeakOnMount } from '../../components/SpeakOnMount';
import { FloatingMicHelp } from '../../components/FloatingMicHelp';
import { ErrorSpeaker } from '../../components/ErrorSpeaker';
import { BigButton } from '../../components/BigButton';
import { NetworkBanner } from '../../components/NetworkBanner';
import { startRecording, stopRecording } from '../../services/audio';
import { useListingStore } from '../../stores/listingStore';
import { useAuthStore } from '../../stores/authStore';
import { DEFAULT_LANGUAGE_CODE } from '../../constants/languages';

export default function VoiceListingScreen() {
    const router = useRouter();
    const artisan = useAuthStore((state) => state.artisan);
    const langCode = artisan?.language_code || DEFAULT_LANGUAGE_CODE;

    const { processVoiceInput, isProcessingVoice } = useListingStore();
    const [isRecording, setIsRecording] = useState<boolean>(false);
    const [errorMessage, setErrorMessage] = useState<string>('');

    const handleMicToggle = async () => {
        setErrorMessage('');
        if (isRecording) {
            const uri = await stopRecording();
            setIsRecording(false);

            if (uri) {
                const success = await processVoiceInput(uri, langCode);
                if (success) {
                    router.push('/listing/photo');
                } else {
                    setErrorMessage('आवाज़ समझने में समस्या हुई। फिर से बोलें।');
                }
            } else {
                setErrorMessage('माइक रिकॉर्डिंग विफल हुई। फिर प्रयास करें।');
            }
        } else {
            const started = await startRecording();
            if (started) {
                setIsRecording(true);
            } else {
                setErrorMessage('माइक अनुमति दें (Enable microphone permission)');
            }
        }
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <NetworkBanner />
            <StepIndicator currentStep={1} />
            <SpeakOnMount text="माइक बटन दबाएं और अपने सामान के बारे में बोलकर बतायें।" />

            <View style={styles.container}>
                <TouchableOpacity
                    onPress={() => router.back()}
                    style={styles.backButton}
                >
                    <ArrowLeft size={28} color={colors.textPrimary} />
                </TouchableOpacity>

                <View style={styles.content}>
                    <Text style={styles.title}>सामान का विवरण दें</Text>
                    <Text style={styles.subtitle}>
                        उदाहरण: "यह 2 किलो का मिट्टी का मटका है, कीमत ₹500 है"
                    </Text>

                    {errorMessage ? <ErrorSpeaker message={errorMessage} /> : null}

                    <VoiceButton
                        isListening={isRecording}
                        isProcessing={isProcessingVoice}
                        onPress={handleMicToggle}
                    />
                </View>

                {/* Manual Skip Fallback */}
                <View style={styles.footer}>
                    <BigButton
                        title="फोटो खींचें (Next: Photo)"
                        icon={ArrowRight}
                        variant="outline"
                        onPress={() => router.push('/listing/photo')}
                    />
                </View>
            </View>

            <FloatingMicHelp helpText="काले माइक बटन को दबाकर सामान का नाम और कीमत बोलें।" />
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
        justifyContent: 'space-between',
    },
    backButton: {
        padding: layout.spacing.xs,
    },
    content: {
        alignItems: 'center',
        justifyContent: 'center',
        flex: 1,
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
        marginVertical: layout.spacing.md,
    },
    footer: {
        marginBottom: layout.spacing.sm,
    },
});
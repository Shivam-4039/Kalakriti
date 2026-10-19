import React, { useState } from 'react';
import {
    View,
    Text,
    StyleSheet,
    SafeAreaView,
    ScrollView,
    Image,
    TextInput,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Check } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';
import { StepIndicator } from '../../components/StepIndicator';
import { SpeakOnMount } from '../../components/SpeakOnMount';
import { AudioPlayer } from '../../components/AudioPlayer';
import { FloatingMicHelp } from '../../components/FloatingMicHelp';
import { ErrorSpeaker } from '../../components/ErrorSpeaker';
import { BigButton } from '../../components/BigButton';
import { NetworkBanner } from '../../components/NetworkBanner';
import { useListingStore } from '../../stores/listingStore';

export default function ListingPreviewScreen() {
    const router = useRouter();
    const {
        extractedFields,
        updateExtractedFields,
        enhancedImageUrl,
        imageUri,
        readbackAudioBase64,
        approveAndPublishProduct,
        isSubmitting,
    } = useListingStore();

    const [errorMessage, setErrorMessage] = useState<string>('');
    const displayImage = enhancedImageUrl || imageUri;

    const handlePublish = async () => {
        setErrorMessage('');
        const success = await approveAndPublishProduct();
        if (success) {
            router.push('/listing/success');
        } else {
            setErrorMessage('सामान जोडने में समस्या हुई। फिर प्रयास करें।');
        }
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <NetworkBanner />
            <StepIndicator currentStep={3} />
            <SpeakOnMount text="जानकारी की जांच करें। अगर सब सही है तो हरा बटन दबाएं।" />

            <ScrollView contentContainerStyle={styles.container}>
                <Text style={styles.title}>जानकारी की जांच करें</Text>

                {errorMessage ? <ErrorSpeaker message={errorMessage} /> : null}

                {/* Readback Audio Player */}
                {readbackAudioBase64 ? (
                    <AudioPlayer
                        base64Audio={readbackAudioBase64}
                        title="निकाली गई जानकारी सुनें"
                    />
                ) : null}

                {/* Photo Display */}
                {displayImage ? (
                    <Image source={{ uri: displayImage }} style={styles.previewImage} />
                ) : null}

                {/* Editable Fields Form */}
                <View style={styles.card}>
                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>सामान का नाम (Title)</Text>
                        <TextInput
                            style={styles.input}
                            value={extractedFields.title || ''}
                            onChangeText={(title) => updateExtractedFields({ title })}
                        />
                    </View>

                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>कीमत ₹ (Price)</Text>
                        <TextInput
                            style={styles.input}
                            keyboardType="number-pad"
                            value={String(extractedFields.price || 0)}
                            onChangeText={(p) => updateExtractedFields({ price: Number(p) || 0 })}
                        />
                    </View>

                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>कला का प्रकार (Craft Type)</Text>
                        <TextInput
                            style={styles.input}
                            value={extractedFields.craft_type || ''}
                            onChangeText={(craft_type) => updateExtractedFields({ craft_type })}
                        />
                    </View>

                    <View style={styles.fieldGroup}>
                        <Text style={styles.label}>विवरण (Description)</Text>
                        <TextInput
                            style={[styles.input, styles.multilineInput]}
                            multiline
                            numberOfLines={3}
                            value={extractedFields.description || ''}
                            onChangeText={(description) => updateExtractedFields({ description })}
                        />
                    </View>
                </View>

                <BigButton
                    title="सब सही है - जोड़ें (Publish)"
                    icon={Check}
                    size="large"
                    variant="accent"
                    loading={isSubmitting}
                    onPress={handlePublish}
                />
            </ScrollView>

            <FloatingMicHelp helpText="सभी जानकारी सही होने पर 'सब सही है' बटन दबाएं।" />
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
    title: {
        fontSize: typography.sizes.screenTitle,
        fontWeight: '800',
        color: colors.textPrimary,
        marginBottom: layout.spacing.md,
    },
    previewImage: {
        width: '100%',
        height: 220,
        borderRadius: layout.borderRadius.md,
        marginVertical: layout.spacing.md,
    },
    card: {
        backgroundColor: colors.surface,
        borderRadius: layout.borderRadius.md,
        borderWidth: 1,
        borderColor: colors.border,
        padding: layout.spacing.md,
        marginBottom: layout.spacing.lg,
    },
    fieldGroup: {
        marginBottom: layout.spacing.md,
    },
    label: {
        fontSize: typography.sizes.caption,
        fontWeight: '700',
        color: colors.textSecondary,
        marginBottom: layout.spacing.xs,
    },
    input: {
        borderWidth: 1,
        borderColor: colors.border,
        borderRadius: layout.borderRadius.sm,
        paddingHorizontal: layout.spacing.md,
        height: layout.touchTarget.standard - 8,
        fontSize: typography.sizes.body,
        fontWeight: '600',
        color: colors.textPrimary,
        backgroundColor: colors.background,
    },
    multilineInput: {
        height: 80,
        textAlignVertical: 'top',
        paddingTop: layout.spacing.xs,
    },
});
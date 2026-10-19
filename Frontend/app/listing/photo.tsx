import React, { useState, useRef } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity, Image } from 'react-native';
import { useRouter } from 'expo-router';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Camera, RefreshCw, ArrowRight, ArrowLeft } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';
import { StepIndicator } from '../../components/StepIndicator';
import { SpeakOnMount } from '../../components/SpeakOnMount';
import { FloatingMicHelp } from '../../components/FloatingMicHelp';
import { ErrorSpeaker } from '../../components/ErrorSpeaker';
import { BigButton } from '../../components/BigButton';
import { NetworkBanner } from '../../components/NetworkBanner';
import { useListingStore } from '../../stores/listingStore';

export default function PhotoCaptureScreen() {
    const router = useRouter();
    const cameraRef = useRef<CameraView | null>(null);
    const [permission, requestPermission] = useCameraPermissions();

    const { processCapturedImage, isProcessingImage } = useListingStore();
    const [previewUri, setPreviewUri] = useState<string | null>(null);
    const [errorMessage, setErrorMessage] = useState<string>('');

    if (!permission) {
        return <View style={styles.container} />;
    }

    if (!permission.granted) {
        return (
            <SafeAreaView style={styles.safeArea}>
                <View style={styles.permissionContainer}>
                    <Camera size={64} color={colors.accent} />
                    <Text style={styles.permissionTitle}>कैमरा अनुमति दें (Allow Camera)</Text>
                    <Text style={styles.permissionSubtitle}>
                        सामान की फोटो खींचने के लिए कैमरा एक्सेस ज़रूरी है।
                    </Text>
                    <BigButton title="अनुमति दें (Grant Permission)" onPress={requestPermission} />
                </View>
            </SafeAreaView>
        );
    }

    const handleTakePicture = async () => {
        try {
            if (cameraRef.current) {
                const photo = await cameraRef.current.takePictureAsync({ quality: 0.8 });
                if (photo?.uri) {
                    setPreviewUri(photo.uri);
                }
            }
        } catch {
            setErrorMessage('फोटो लेने में समस्या हुई। फिर कोशिश करें।');
        }
    };

    const handleConfirmPhoto = async () => {
        if (!previewUri) return;
        const success = await processCapturedImage(previewUri);
        if (success) {
            router.push('/listing/preview');
        } else {
            setErrorMessage('फोटो अपलोड नहीं हो सकी। फिर कोशिश करें।');
        }
    };

    return (
        <SafeAreaView style={styles.safeArea}>
            <NetworkBanner />
            <StepIndicator currentStep={2} />
            <SpeakOnMount text="सामान की साफ फोटो खींचें।" />

            <View style={styles.container}>
                <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
                    <ArrowLeft size={28} color={colors.textPrimary} />
                </TouchableOpacity>

                {errorMessage ? <ErrorSpeaker message={errorMessage} /> : null}

                {previewUri ? (
                    <View style={styles.previewWrapper}>
                        <Image source={{ uri: previewUri }} style={styles.previewImage} />
                        <View style={styles.buttonRow}>
                            <View style={{ flex: 1, marginRight: layout.spacing.xs }}>
                                <BigButton
                                    title="फिर से खींचें"
                                    icon={RefreshCw}
                                    variant="outline"
                                    onPress={() => setPreviewUri(null)}
                                />
                            </View>
                            <View style={{ flex: 1, marginLeft: layout.spacing.xs }}>
                                <BigButton
                                    title="सही है (Confirm)"
                                    icon={ArrowRight}
                                    loading={isProcessingImage}
                                    onPress={handleConfirmPhoto}
                                />
                            </View>
                        </View>
                    </View>
                ) : (
                    <View style={styles.cameraWrapper}>
                        <CameraView ref={cameraRef} style={styles.camera}>
                            <View style={styles.cameraOverlay}>
                                <TouchableOpacity
                                    activeOpacity={0.8}
                                    onPress={handleTakePicture}
                                    style={styles.captureBtn}
                                >
                                    <View style={styles.innerCaptureBtn} />
                                </TouchableOpacity>
                            </View>
                        </CameraView>
                    </View>
                )}
            </View>

            <FloatingMicHelp helpText="सफेद गोल बटन को दबाकर सामान की फोटो खींचें।" />
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
    },
    backButton: {
        padding: layout.spacing.xs,
        marginBottom: layout.spacing.sm,
    },
    cameraWrapper: {
        flex: 1,
        borderRadius: layout.borderRadius.lg,
        overflow: 'hidden',
        borderWidth: 2,
        borderColor: colors.border,
    },
    camera: {
        flex: 1,
    },
    cameraOverlay: {
        flex: 1,
        justifyContent: 'flex-end',
        alignItems: 'center',
        paddingBottom: layout.spacing.xl,
    },
    captureBtn: {
        width: layout.touchTarget.mic,
        height: layout.touchTarget.mic,
        borderRadius: layout.borderRadius.full,
        backgroundColor: 'rgba(255,255,255,0.4)',
        alignItems: 'center',
        justifyContent: 'center',
    },
    innerCaptureBtn: {
        width: 68,
        height: 68,
        borderRadius: layout.borderRadius.full,
        backgroundColor: '#FFFFFF',
    },
    previewWrapper: {
        flex: 1,
        justifyContent: 'space-between',
    },
    previewImage: {
        flex: 1,
        borderRadius: layout.borderRadius.lg,
        marginBottom: layout.spacing.md,
    },
    buttonRow: {
        flexDirection: 'row',
    },
    permissionContainer: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',
        padding: layout.spacing.lg,
    },
    permissionTitle: {
        fontSize: typography.sizes.screenTitle,
        fontWeight: '800',
        marginTop: layout.spacing.md,
    },
    permissionSubtitle: {
        fontSize: typography.sizes.body,
        color: colors.textSecondary,
        textAlign: 'center',
        marginVertical: layout.spacing.md,
    },
});
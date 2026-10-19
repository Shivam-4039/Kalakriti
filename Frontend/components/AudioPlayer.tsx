import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Volume2, Play, Square } from 'lucide-react-native';
import { colors, layout, typography } from '../theme';
import { playBase64Audio, stopAudioPlayback } from '../services/audio';

interface AudioPlayerProps {
    base64Audio: string;
    title?: string;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
    base64Audio,
    title = 'आवाज़ सुनें (Listen Audio)',
}) => {
    const [isPlaying, setIsPlaying] = useState<boolean>(false);

    const handleTogglePlay = async () => {
        if (isPlaying) {
            await stopAudioPlayback();
            setIsPlaying(false);
        } else {
            setIsPlaying(true);
            const success = await playBase64Audio(base64Audio, () => {
                setIsPlaying(false);
            });
            if (!success) setIsPlaying(false);
        }
    };

    return (
        <View style={styles.card}>
            <View style={styles.header}>
                <Volume2 size={24} color={colors.accent} style={styles.headerIcon} />
                <Text style={styles.title}>{title}</Text>
            </View>

            <TouchableOpacity
                activeOpacity={0.8}
                onPress={handleTogglePlay}
                style={[
                    styles.playButton,
                    { backgroundColor: isPlaying ? colors.error : colors.accent },
                ]}
            >
                {isPlaying ? (
                    <>
                        <Square size={20} color="#FFFFFF" fill="#FFFFFF" />
                        <Text style={styles.buttonText}>रोकें (Stop)</Text>
                    </>
                ) : (
                    <>
                        <Play size={20} color="#FFFFFF" fill="#FFFFFF" />
                        <Text style={styles.buttonText}>सुनें (Play)</Text>
                    </>
                )}
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
    card: {
        backgroundColor: colors.surface,
        borderRadius: layout.borderRadius.md,
        borderWidth: 1,
        borderColor: colors.border,
        padding: layout.spacing.md,
        marginVertical: layout.spacing.sm,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    header: {
        flexDirection: 'row',
        alignItems: 'center',
        flex: 1,
    },
    headerIcon: {
        marginRight: layout.spacing.sm,
    },
    title: {
        fontSize: typography.sizes.body,
        fontWeight: '600',
        color: colors.textPrimary,
    },
    playButton: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: layout.spacing.xs + 2,
        paddingHorizontal: layout.spacing.md,
        borderRadius: layout.borderRadius.sm,
        minHeight: layout.touchTarget.standard - 12,
    },
    buttonText: {
        color: '#FFFFFF',
        fontWeight: '700',
        fontSize: typography.sizes.body,
        marginLeft: layout.spacing.xs,
    },
});
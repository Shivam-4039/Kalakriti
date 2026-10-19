import React from 'react';
import { TouchableOpacity, StyleSheet, View } from 'react-native';
import { HelpCircle, Mic } from 'lucide-react-native';
import { colors, layout } from '../theme';
import { useTTS } from '../hooks/useTTS';

interface FloatingMicHelpProps {
    helpText: string;
}

export const FloatingMicHelp: React.FC<FloatingMicHelpProps> = ({ helpText }) => {
    const { speak, isSpeaking } = useTTS();

    const handleHelpPress = () => {
        if (helpText) {
            speak(helpText);
        }
    };

    return (
        <TouchableOpacity
            activeOpacity={0.8}
            onPress={handleHelpPress}
            style={[
                styles.floatingButton,
                { backgroundColor: isSpeaking ? colors.accent : colors.primary },
            ]}
            accessibilityLabel="मदद के लिए दबाएं (Press for help)"
        >
            <View style={styles.iconContainer}>
                <Mic size={24} color="#FFFFFF" />
                <HelpCircle
                    size={14}
                    color="#FFFFFF"
                    style={styles.helpBadge}
                />
            </View>
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    floatingButton: {
        position: 'absolute',
        bottom: layout.spacing.xl,
        right: layout.spacing.lg,
        width: 60,
        height: 60,
        borderRadius: layout.borderRadius.full,
        alignItems: 'center',
        justifyContent: 'center',
        elevation: 6,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 3 },
        shadowOpacity: 0.25,
        shadowRadius: 5,
        zIndex: 999,
    },
    iconContainer: {
        position: 'relative',
        alignItems: 'center',
        justifyContent: 'center',
    },
    helpBadge: {
        position: 'absolute',
        top: -4,
        right: -6,
        backgroundColor: colors.accent,
        borderRadius: layout.borderRadius.full,
    },
});
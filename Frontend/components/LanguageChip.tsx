import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';
import { Check } from 'lucide-react-native';
import { colors, layout, typography } from '../theme';
import { Language } from '../constants/languages';

interface LanguageChipProps {
    language: Language;
    isSelected: boolean;
    onSelect: (lang: Language) => void;
}

export const LanguageChip: React.FC<LanguageChipProps> = ({
    language,
    isSelected,
    onSelect,
}) => {
    return (
        <TouchableOpacity
            activeOpacity={0.8}
            onPress={() => onSelect(language)}
            style={[
                styles.chip,
                isSelected && styles.selectedChip,
            ]}
        >
            <Text
                style={[
                    styles.nativeText,
                    isSelected && styles.selectedText,
                ]}
            >
                {language.nativeName}
            </Text>

            {isSelected && (
                <Check size={20} color="#FFFFFF" style={styles.checkIcon} />
            )}
        </TouchableOpacity>
    );
};

const styles = StyleSheet.create({
    chip: {
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderWidth: 2,
        borderRadius: layout.borderRadius.lg,
        paddingVertical: layout.spacing.md,
        paddingHorizontal: layout.spacing.lg,
        margin: layout.spacing.xs,
        minHeight: layout.touchTarget.standard,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        minWidth: '45%',
    },
    selectedChip: {
        backgroundColor: colors.primary,
        borderColor: colors.primary,
    },
    nativeText: {
        fontSize: typography.sizes.sectionTitle,
        fontWeight: '700',
        color: colors.textPrimary,
    },
    selectedText: {
        color: '#FFFFFF',
    },
    checkIcon: {
        marginLeft: layout.spacing.xs,
    },
});
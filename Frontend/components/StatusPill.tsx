import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, layout, typography } from '../theme';

export type StatusType = 'published' | 'draft' | 'pending' | 'failed' | string;

interface StatusPillProps {
    status: StatusType;
}

export const StatusPill: React.FC<StatusPillProps> = ({ status }) => {
    let backgroundColor: string = colors.primarySoft;
    let textColor: string = colors.textSecondary;
    let label = 'ड्राफ्ट (Draft)';

    const normalizedStatus = status ? status.toLowerCase() : 'draft';

    if (normalizedStatus === 'published' || normalizedStatus === 'active') {
        backgroundColor = colors.successSoft;
        textColor = colors.success;
        label = 'ONDC लाइव (Live)';
    } else if (normalizedStatus === 'pending') {
        backgroundColor = colors.warningSoft;
        textColor = colors.warning;
        label = 'प्रक्रिया में (Pending)';
    } else if (normalizedStatus === 'failed' || normalizedStatus === 'error') {
        backgroundColor = colors.errorSoft;
        textColor = colors.error;
        label = 'त्रुटि (Error)';
    }

    return (
        <View style={[styles.pill, { backgroundColor }]}>
            <Text style={[styles.text, { color: textColor }]}>{label}</Text>
        </View>
    );
};

const styles = StyleSheet.create({
    pill: {
        paddingVertical: 2,
        paddingHorizontal: layout.spacing.sm,
        borderRadius: layout.borderRadius.full,
        alignSelf: 'flex-start',
    },
    text: {
        fontSize: typography.sizes.caption - 1,
        fontWeight: '700',
    },
});

export default StatusPill;
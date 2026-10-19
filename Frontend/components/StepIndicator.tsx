import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, layout, typography } from '../theme';

interface StepIndicatorProps {
    currentStep: 1 | 2 | 3;
}

const steps = [
    { step: 1, label: 'आवाज़ (Voice)' },
    { step: 2, label: 'फोटो (Photo)' },
    { step: 3, label: 'जांच (Review)' },
];

export const StepIndicator: React.FC<StepIndicatorProps> = ({ currentStep }) => {
    return (
        <View style={styles.container}>
            {steps.map((item, index) => {
                const isActive = item.step === currentStep;
                const isCompleted = item.step < currentStep;

                return (
                    <React.Fragment key={item.step}>
                        <View style={styles.stepItem}>
                            <View
                                style={[
                                    styles.circle,
                                    isActive && styles.activeCircle,
                                    isCompleted && styles.completedCircle,
                                ]}
                            >
                                <Text
                                    style={[
                                        styles.circleText,
                                        (isActive || isCompleted) && styles.activeCircleText,
                                    ]}
                                >
                                    {item.step}
                                </Text>
                            </View>
                            <Text style={[styles.stepLabel, isActive && styles.activeStepLabel]}>
                                {item.label}
                            </Text>
                        </View>

                        {index < steps.length - 1 && (
                            <View
                                style={[
                                    styles.connectorLine,
                                    isCompleted && styles.completedConnectorLine,
                                ]}
                            />
                        )}
                    </React.Fragment>
                );
            })}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingHorizontal: layout.spacing.lg,
        paddingVertical: layout.spacing.md,
        backgroundColor: colors.surface,
        borderBottomWidth: 1,
        borderBottomColor: colors.border,
    },
    stepItem: {
        alignItems: 'center',
    },
    circle: {
        width: 36,
        height: 36,
        borderRadius: layout.borderRadius.full,
        backgroundColor: colors.primarySoft,
        borderWidth: 2,
        borderColor: colors.border,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: layout.spacing.xs,
    },
    activeCircle: {
        backgroundColor: colors.primary,
        borderColor: colors.primary,
    },
    completedCircle: {
        backgroundColor: colors.success,
        borderColor: colors.success,
    },
    circleText: {
        fontSize: typography.sizes.body,
        fontWeight: '700',
        color: colors.textSecondary,
    },
    activeCircleText: {
        color: '#FFFFFF',
    },
    stepLabel: {
        fontSize: typography.sizes.caption - 1,
        color: colors.textSecondary,
        fontWeight: '500',
    },
    activeStepLabel: {
        color: colors.textPrimary,
        fontWeight: '700',
    },
    connectorLine: {
        flex: 1,
        height: 2,
        backgroundColor: colors.border,
        marginHorizontal: layout.spacing.xs,
        marginBottom: layout.spacing.md,
    },
    completedConnectorLine: {
        backgroundColor: colors.success,
    },
});
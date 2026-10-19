import { MD3LightTheme } from 'react-native-paper';

// Core design system tokens locked to project specifications
export const colors = {
    background: '#FAFAFA',
    surface: '#FFFFFF',
    primary: '#1A1A1A',
    primarySoft: '#F0F0F0',
    accent: '#2563EB',
    success: '#16A34A',
    warning: '#D97706',
    error: '#DC2626',
    textPrimary: '#111827',
    textSecondary: '#6B7280',
    border: '#E5E7EB',

    // Status background tints for tags/pills
    successSoft: '#DCFCE7',
    warningSoft: '#FEF3C7',
    errorSoft: '#FEE2E2',
    accentSoft: '#DBEAFE',
} as const;

export const typography = {
    // Spacing and sizes designed for low-literacy clarity (min body 16sp)
    sizes: {
        caption: 14,
        body: 16,
        bodyLarge: 18,
        sectionTitle: 20,
        screenTitle: 26,
        heroTitle: 32,
    },
    fontFamily: {
        regular: 'System', // Standard Roboto (Android) or San Francisco (iOS)
        devanagari: 'NotoSansDevanagari', // Regional fallback
    },
} as const;

export const layout = {
    // Touch targets enforce minimum 56dp (standard) and 72dp+ (primary CTAs)
    touchTarget: {
        standard: 56,
        primary: 72,
        mic: 88,
    },
    borderRadius: {
        sm: 8,
        md: 12,
        lg: 16,
        full: 9999,
    },
    spacing: {
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32,
    },
} as const;

// Custom React Native Paper theme matching system design
export const paperTheme = {
    ...MD3LightTheme,
    colors: {
        ...MD3LightTheme.colors,
        primary: colors.primary,
        onPrimary: '#FFFFFF',
        primaryContainer: colors.primarySoft,
        onPrimaryContainer: colors.primary,
        secondary: colors.accent,
        background: colors.background,
        surface: colors.surface,
        error: colors.error,
        outline: colors.border,
    },
    roundness: layout.borderRadius.md,
};
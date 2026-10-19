import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  View,
} from 'react-native';
import { LucideIcon } from 'lucide-react-native';
import { colors, layout, typography } from '../theme';

interface BigButtonProps {
  title: string;
  onPress: () => void;
  icon?: LucideIcon;
  variant?: 'primary' | 'secondary' | 'accent' | 'outline' | 'danger';
  size?: 'standard' | 'large'; // standard: 56dp, large: 72dp
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
}

export const BigButton: React.FC<BigButtonProps> = ({
  title,
  onPress,
  icon: Icon,
  variant = 'primary',
  size = 'standard',
  disabled = false,
  loading = false,
  fullWidth = true,
}) => {
  const minHeight = size === 'large' ? layout.touchTarget.primary : layout.touchTarget.standard;

  // Determine styles based on variant
  let backgroundColor: string = colors.primary;
  let textColor: string = '#FFFFFF';
  let borderColor: string = 'transparent';

  if (variant === 'secondary') {
    backgroundColor = colors.primarySoft;
    textColor = colors.textPrimary;
  } else if (variant === 'accent') {
    backgroundColor = colors.accent;
    textColor = '#FFFFFF';
  } else if (variant === 'outline') {
    backgroundColor = colors.surface;
    textColor = colors.textPrimary;
    borderColor = colors.border;
  } else if (variant === 'danger') {
    backgroundColor = colors.error;
    textColor = '#FFFFFF';
  }

  if (disabled) {
    backgroundColor = colors.border;
    textColor = colors.textSecondary;
    borderColor = 'transparent';
  }

  return (
    <TouchableOpacity
      activeOpacity={0.8}
      onPress={onPress}
      disabled={disabled || loading}
      style={[
        styles.button,
        {
          minHeight,
          backgroundColor,
          borderColor,
          borderWidth: variant === 'outline' ? 1 : 0,
          alignSelf: fullWidth ? 'stretch' : 'auto',
        },
      ]}
    >
      {loading ? (
        <ActivityIndicator size="small" color={textColor} />
      ) : (
        <View style={styles.content}>
          {Icon && (
            <Icon
              size={size === 'large' ? 28 : 24}
              color={textColor}
              style={styles.icon}
            />
          )}
          <Text
            style={[
              styles.text,
              {
                color: textColor,
                fontSize: size === 'large' ? typography.sizes.bodyLarge : typography.sizes.body,
              },
            ]}
          >
            {title}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: layout.borderRadius.md,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: layout.spacing.lg,
    marginVertical: layout.spacing.xs,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  icon: {
    marginRight: layout.spacing.sm,
  },
  text: {
    fontWeight: '700',
    textAlign: 'center',
  },
});
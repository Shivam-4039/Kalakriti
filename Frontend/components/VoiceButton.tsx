import React, { useEffect, useRef } from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  View,
  Animated,
  ActivityIndicator,
} from 'react-native';
import { Mic, MicOff } from 'lucide-react-native';
import { colors, layout, typography } from '../theme';

interface VoiceButtonProps {
  isListening: boolean;
  isProcessing: boolean;
  onPress: () => void;
  labelIdle?: string;
  labelListening?: string;
}

export const VoiceButton: React.FC<VoiceButtonProps> = ({
  isListening,
  isProcessing,
  onPress,
  labelIdle = 'बोलकर बतायें (Speak)',
  labelListening = 'सुन रहा हूँ... (Listening...)',
}) => {
  const pulseAnim = useRef(new Animated.Value(1)).current;

  // Gentle pulsing animation when mic is actively listening
  useEffect(() => {
    let animation: Animated.CompositeAnimation;

    if (isListening) {
      animation = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1.0,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      );
      animation.start();
    } else {
      pulseAnim.setValue(1);
    }

    return () => {
      if (animation) animation.stop();
    };
  }, [isListening, pulseAnim]);

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.pulseRing,
          {
            transform: [{ scale: pulseAnim }],
            backgroundColor: isListening ? colors.errorSoft : 'transparent',
          },
        ]}
      >
        <TouchableOpacity
          activeOpacity={0.8}
          onPress={onPress}
          disabled={isProcessing}
          style={[
            styles.micButton,
            {
              backgroundColor: isListening
                ? colors.error
                : isProcessing
                ? colors.textSecondary
                : colors.primary,
            },
          ]}
        >
          {isProcessing ? (
            <ActivityIndicator size="large" color="#FFFFFF" />
          ) : isListening ? (
            <MicOff size={40} color="#FFFFFF" />
          ) : (
            <Mic size={40} color="#FFFFFF" />
          )}
        </TouchableOpacity>
      </Animated.View>

      <Text style={styles.statusText}>
        {isProcessing
          ? 'समझ रहा हूँ... (Processing...)'
          : isListening
          ? labelListening
          : labelIdle}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: layout.spacing.lg,
  },
  pulseRing: {
    width: layout.touchTarget.mic + 24,
    height: layout.touchTarget.mic + 24,
    borderRadius: layout.borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
  },
  micButton: {
    width: layout.touchTarget.mic,
    height: layout.touchTarget.mic,
    borderRadius: layout.borderRadius.full,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 4,
  },
  statusText: {
    marginTop: layout.spacing.md,
    fontSize: typography.sizes.bodyLarge,
    fontWeight: '700',
    color: colors.textPrimary,
    textAlign: 'center',
  },
});
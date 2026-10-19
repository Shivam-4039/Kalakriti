import React, { useCallback } from 'react';
import { useFocusEffect } from 'expo-router';
import { useTTS } from '../hooks/useTTS';

interface SpeakOnMountProps {
    text: string;
    delayMs?: number;
}

export const SpeakOnMount: React.FC<SpeakOnMountProps> = ({
    text,
    delayMs = 300, // Small delay allows smooth screen transition before narration begins
}) => {
    const { speak, stop } = useTTS();

    useFocusEffect(
        useCallback(() => {
            let isSubscribed = true;

            const timer = setTimeout(() => {
                if (isSubscribed && text) {
                    speak(text);
                }
            }, delayMs);

            return () => {
                isSubscribed = false;
                clearTimeout(timer);
                stop();
            };
        }, [text, delayMs, speak, stop])
    );

    return null; // Purely logical audio component, renders nothing to DOM
};
import { useState, useCallback } from 'react';
import { speakText, stopSpeech } from '../services/speech';
import { useAuthStore } from '../stores/authStore';
import { DEFAULT_LANGUAGE_CODE } from '../constants/languages';

export const useTTS = () => {
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const artisan = useAuthStore((state) => state.artisan);
  const userLanguage = artisan?.language_code || DEFAULT_LANGUAGE_CODE;

  const speak = useCallback(
    async (text: string, customLanguageCode?: string) => {
      try {
        setIsSpeaking(true);
        const targetLang = customLanguageCode || userLanguage;
        const success = await speakText(text, targetLang, () => {
          setIsSpeaking(false);
        });

        if (!success) {
          setIsSpeaking(false);
        }
        return success;
      } catch (error) {
        console.error('[useTTS] Error invoking speech synthesis:', error);
        setIsSpeaking(false);
        return false;
      }
    },
    [userLanguage]
  );

  const stop = useCallback(async () => {
    await stopSpeech();
    setIsSpeaking(false);
  }, []);

  return { speak, stop, isSpeaking };
};
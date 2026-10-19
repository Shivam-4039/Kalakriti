import { api } from './api';
import { playBase64Audio, stopAudioPlayback } from './audio';
import { DEFAULT_LANGUAGE_CODE } from '../constants/languages';

interface SynthesizeResponse {
    audio_base64?: string;
    audio?: string;
}

/**
 * Synthesizes text to speech using backend TTS and plays audio immediately
 */
export const speakText = async (
    text: string,
    languageCode: string = DEFAULT_LANGUAGE_CODE,
    onFinish?: () => void
): Promise<boolean> => {
    try {
        if (!text || text.trim().length === 0) {
            return false;
        }

        // Stop any current audio before starting new TTS playback
        await stopAudioPlayback();

        const response = await api.post<SynthesizeResponse | string>('/voice/synthesize', {
            text,
            language_code: languageCode,
        });

        let base64Audio = '';

        if (typeof response.data === 'string') {
            base64Audio = response.data;
        } else if (response.data && typeof response.data === 'object') {
            base64Audio = response.data.audio_base64 || response.data.audio || '';
        }

        if (!base64Audio) {
            console.error('[SpeechService] Backend returned empty audio payload.');
            return false;
        }

        return await playBase64Audio(base64Audio, onFinish);
    } catch (error) {
        console.error('[SpeechService] Failed to synthesize or play text:', error);
        return false;
    }
};

/**
 * Stop any active TTS audio playback
 */
export const stopSpeech = async (): Promise<void> => {
    await stopAudioPlayback();
};
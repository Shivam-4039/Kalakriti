import { Audio } from 'expo-av';

let currentRecording: Audio.Recording | null = null;
let currentSound: Audio.Sound | null = null;

// Request microphone permissions
export const requestAudioPermissions = async (): Promise<boolean> => {
  try {
    const { status } = await Audio.requestPermissionsAsync();
    return status === 'granted';
  } catch (error) {
    console.error('[AudioService] Failed to request permissions:', error);
    return false;
  }
};

// Start recording audio in 16kHz mono WAV format
export const startRecording = async (): Promise<boolean> => {
  try {
    const hasPermission = await requestAudioPermissions();
    if (!hasPermission) {
      throw new Error('Microphone permission not granted.');
    }

    // Configure audio mode for voice recording
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: true,
      playsInSilentModeIOS: true,
      shouldDuckAndroid: true,
      playThroughEarpieceAndroid: false,
    });

    if (currentRecording) {
      await stopRecording();
    }

    const recording = new Audio.Recording();
    
    // Custom recording options for 16kHz mono WAV backend compatibility
    const recordingOptions: Audio.RecordingOptions = {
      android: {
        extension: '.wav',
        outputFormat: Audio.AndroidOutputFormat.THREE_GPP,
        audioEncoder: Audio.AndroidAudioEncoder.AMR_NB,
        sampleRate: 16000,
        numberOfChannels: 1,
        bitRate: 128000,
      },
      ios: {
        extension: '.wav',
        audioQuality: Audio.IOSAudioQuality.HIGH,
        sampleRate: 16000,
        numberOfChannels: 1,
        bitRate: 128000,
        linearPCMBitDepth: 16,
        linearPCMIsBigEndian: false,
        linearPCMIsFloat: false,
      },
      web: {},
    };

    await recording.prepareToRecordAsync(recordingOptions);
    await recording.startAsync();
    currentRecording = recording;
    return true;
  } catch (error) {
    console.error('[AudioService] Failed to start recording:', error);
    currentRecording = null;
    return false;
  }
};

// Stop recording and return local URI of recorded WAV file
export const stopRecording = async (): Promise<string | null> => {
  try {
    if (!currentRecording) return null;

    await currentRecording.stopAndUnloadAsync();
    const uri = currentRecording.getURI();
    currentRecording = null;

    // Reset audio mode after recording completes
    await Audio.setAudioModeAsync({
      allowsRecordingIOS: false,
      playsInSilentModeIOS: true,
    });

    return uri;
  } catch (error) {
    console.error('[AudioService] Failed to stop recording:', error);
    currentRecording = null;
    return null;
  }
};

// Play base64 encoded audio string returned from API TTS
export const playBase64Audio = async (base64String: string, onPlaybackFinished?: () => void): Promise<boolean> => {
  try {
    await stopAudioPlayback();

    // Standardize data URI format
    const audioUri = base64String.startsWith('data:audio')
      ? base64String
      : `data:audio/wav;base64,${base64String}`;

    const { sound } = await Audio.Sound.createAsync(
      { uri: audioUri },
      { shouldPlay: true }
    );

    currentSound = sound;

    sound.setOnPlaybackStatusUpdate((status) => {
      if (status.isLoaded && status.didJustFinish) {
        sound.unloadAsync().catch(() => {});
        currentSound = null;
        if (onPlaybackFinished) onPlaybackFinished();
      }
    });

    return true;
  } catch (error) {
    console.error('[AudioService] Failed to play base64 audio:', error);
    return false;
  }
};

// Stop any currently playing audio
export const stopAudioPlayback = async (): Promise<void> => {
  try {
    if (currentSound) {
      await currentSound.stopAsync();
      await currentSound.unloadAsync();
      currentSound = null;
    }
  } catch (error) {
    console.error('[AudioService] Failed to stop audio playback:', error);
  }
};
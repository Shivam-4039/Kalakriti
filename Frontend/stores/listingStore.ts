import { create } from 'zustand';
import { api } from '../services/api';
import { uploadImage } from '../services/camera';

export interface ExtractedProductFields {
  title?: string;
  description?: string;
  category?: string;
  price?: number;
  craft_type?: string;
  material?: string;
  colors?: string[];
  estimated_production_days?: number;
}

interface ListingState {
  // Wizard state tracking
  currentStep: 1 | 2 | 3 | 4; // 1: Voice, 2: Photo, 3: Review, 4: Success
  conversationId: string | null;
  audioUri: string | null;
  imageUri: string | null;
  enhancedImageUrl: string | null;
  
  // Extracted fields and status flags
  extractedFields: ExtractedProductFields;
  readbackAudioBase64: string | null;
  isProcessingVoice: boolean;
  isProcessingImage: boolean;
  isSubmitting: boolean;
  createdProductId: string | null;

  // Actions
  setAudioUri: (uri: string) => void;
  setImageUri: (uri: string) => void;
  updateExtractedFields: (fields: Partial<ExtractedProductFields>) => void;
  
  processVoiceInput: (audioUri: string, languageCode: string) => Promise<boolean>;
  processCapturedImage: (imageUri: string) => Promise<boolean>;
  approveAndPublishProduct: () => Promise<boolean>;
  resetListing: () => void;
}

const initialFields: ExtractedProductFields = {
  title: '',
  description: '',
  category: '',
  price: 0,
  craft_type: '',
  material: '',
  colors: [],
};

export const useListingStore = create<ListingState>((set, get) => ({
  currentStep: 1,
  conversationId: null,
  audioUri: null,
  imageUri: null,
  enhancedImageUrl: null,
  extractedFields: initialFields,
  readbackAudioBase64: null,
  isProcessingVoice: false,
  isProcessingImage: false,
  isSubmitting: false,
  createdProductId: null,

  setAudioUri: (uri: string) => set({ audioUri: uri }),
  setImageUri: (uri: string) => set({ imageUri: uri }),

  updateExtractedFields: (fields: Partial<ExtractedProductFields>) =>
    set((state) => ({
      extractedFields: { ...state.extractedFields, ...fields },
    })),

  // Send voice recording WAV to backend POST /voice/process
  processVoiceInput: async (audioUri: string, languageCode: string) => {
    try {
      set({ isProcessingVoice: true, audioUri });

      const filename = audioUri.split('/').pop() || 'recording.wav';
      const formData = new FormData();
      formData.append('audio_file', {
        uri: audioUri,
        name: filename,
        type: 'audio/wav',
      } as unknown as Blob);
      formData.append('language_code', languageCode);

      if (get().conversationId) {
        formData.append('conversation_id', get().conversationId!);
      }

      const response = await api.post<{
        conversation_id?: string;
        extracted_fields?: ExtractedProductFields;
        readback_audio?: string;
        readback_audio_base64?: string;
      }>('/voice/process', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const data = response.data;
      const readbackAudio = data.readback_audio || data.readback_audio_base64 || null;

      set({
        conversationId: data.conversation_id || null,
        extractedFields: { ...get().extractedFields, ...data.extracted_fields },
        readbackAudioBase64: readbackAudio,
        currentStep: 2, // Proceed to step 2: photo capture
      });

      return true;
    } catch (error) {
      console.error('[ListingStore] Voice processing error:', error);
      return false;
    } finally {
      set({ isProcessingVoice: false });
    }
  },

  // Upload captured image for enhancement
  processCapturedImage: async (imageUri: string) => {
    try {
      set({ isProcessingImage: true, imageUri });

      const response = await uploadImage(imageUri, '/image/enhance');

      if (response && response.enhanced_image_url) {
        set({ enhancedImageUrl: response.enhanced_image_url });
      } else {
        // Fallback to local image URI if backend enhancement service is unreachable
        set({ enhancedImageUrl: imageUri });
      }

      set({ currentStep: 3 }); // Proceed to step 3: preview & review
      return true;
    } catch (error) {
      console.error('[ListingStore] Image processing error:', error);
      set({ enhancedImageUrl: imageUri, currentStep: 3 });
      return false;
    } finally {
      set({ isProcessingImage: false });
    }
  },

  // Submit approved product to POST /products
  approveAndPublishProduct: async () => {
    try {
      set({ isSubmitting: true });
      const { conversationId, extractedFields, enhancedImageUrl, imageUri } = get();

      // Approve extraction log with voice backend if conversation exists
      if (conversationId) {
        await api.post('/voice/approve', {
          conversation_id: conversationId,
          is_approved: true,
          corrected_fields: extractedFields,
        }).catch((err) => console.log('[ListingStore] Non-blocking approve call failed:', err));
      }

      const productPayload = {
        title: extractedFields.title || 'Handmade Craft Item',
        description: extractedFields.description || '',
        category: extractedFields.category || 'Handicraft',
        price: extractedFields.price || 0,
        craft_type: extractedFields.craft_type || '',
        material: extractedFields.material || '',
        image_url: enhancedImageUrl || imageUri || '',
      };

      const response = await api.post<{ id: string }>('/products', productPayload);

      set({
        createdProductId: response.data.id,
        currentStep: 4, // Final confirmation screen
      });

      return true;
    } catch (error) {
      console.error('[ListingStore] Final submission error:', error);
      return false;
    } finally {
      set({ isSubmitting: false });
    }
  },

  resetListing: () =>
    set({
      currentStep: 1,
      conversationId: null,
      audioUri: null,
      imageUri: null,
      enhancedImageUrl: null,
      extractedFields: initialFields,
      readbackAudioBase64: null,
      isProcessingVoice: false,
      isProcessingImage: false,
      isSubmitting: false,
      createdProductId: null,
    }),
}));
import * as ImageManipulator from 'expo-image-manipulator';
import * as FileSystem from 'expo-file-system';
import { api } from './api';

const MAX_DIMENSION = 1080;
const TARGET_MAX_BYTES = 300 * 1024; // 300 KB limit

export interface ImageUploadResponse {
  enhanced_image_url?: string;
  thumbnail_url?: string;
  dimensions?: { width: number; height: number };
}

/**
 * Resize and compress image on device before upload to optimize poor network performance
 */
export const compressImage = async (imageUri: string): Promise<string> => {
  try {
    // First compression pass: 1080px max dimension, 0.75 quality
    let result = await ImageManipulator.manipulateAsync(
      imageUri,
      [{ resize: { width: MAX_DIMENSION } }],
      { compress: 0.75, format: ImageManipulator.SaveFormat.JPEG }
    );

    // Check resulting file size
    let fileInfo = await FileSystem.getInfoAsync(result.uri);
    
    // Second compression pass if size still exceeds 300KB target
    if (fileInfo.exists && fileInfo.size > TARGET_MAX_BYTES) {
      console.log(`[CameraService] Image size ${fileInfo.size} bytes exceeds limit. Re-compressing...`);
      result = await ImageManipulator.manipulateAsync(
        result.uri,
        [{ resize: { width: MAX_DIMENSION } }],
        { compress: 0.5, format: ImageManipulator.SaveFormat.JPEG }
      );
    }

    return result.uri;
  } catch (error) {
    console.error('[CameraService] Failed to compress image:', error);
    return imageUri; // Fallback to original image URI if manipulation fails
  }
};

/**
 * Upload compressed image to backend endpoint using multipart form-data
 */
export const uploadImage = async (
  imageUri: string,
  endpoint: '/image/enhance' | '/image/thumbnail'
): Promise<ImageUploadResponse | null> => {
  try {
    const compressedUri = await compressImage(imageUri);
    const filename = compressedUri.split('/').pop() || 'photo.jpg';

    const formData = new FormData();
    formData.append('image', {
      uri: compressedUri,
      name: filename,
      type: 'image/jpeg',
    } as unknown as Blob);

    const response = await api.post<ImageUploadResponse>(endpoint, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error(`[CameraService] Image upload to ${endpoint} failed:`, error);
    return null;
  }
};
export interface Language {
  code: string; // ISO 639-1 / Bhashini language code
  nativeName: string; // Displayed in native script for low-literacy recognition
  englishName: string;
  isDefault?: boolean;
}

export const SUPPORTED_LANGUAGES: Language[] = [
  { code: 'hi', nativeName: 'हिंदी', englishName: 'Hindi', isDefault: true },
  { code: 'mr', nativeName: 'मराठी', englishName: 'Marathi' },
  { code: 'gu', nativeName: 'ગુજરાતી', englishName: 'Gujarati' },
  { code: 'bn', nativeName: 'বাংলা', englishName: 'Bengali' },
  { code: 'ta', nativeName: 'தமிழ்', englishName: 'Tamil' },
  { code: 'te', nativeName: 'తెలుగు', englishName: 'Telugu' },
  { code: 'kn', nativeName: 'ಕನ್ನಡ', englishName: 'Kannada' },
  { code: 'en', nativeName: 'English', englishName: 'English' },
];

export const DEFAULT_LANGUAGE_CODE = 'hi';

export const getLanguageByCode = (code: string): Language => {
  return (
    SUPPORTED_LANGUAGES.find((lang) => lang.code === code) ||
    SUPPORTED_LANGUAGES.find((lang) => lang.code === DEFAULT_LANGUAGE_CODE)!
  );
};
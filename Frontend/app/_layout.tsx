import React, { useEffect } from 'react';
import { Stack } from 'expo-router';
import { PaperProvider } from 'react-native-paper';
import * as SplashScreen from 'expo-splash-screen';
import { useFonts } from 'expo-font';
import { paperTheme } from '../theme';
import { useAuthStore } from '../stores/authStore';

// Prevent splash screen from auto-hiding until assets and auth session are ready
SplashScreen.preventAutoHideAsync().catch(() => {
    /* Ignore splash prevent error on hot reload */
});

export default function RootLayout() {
    const loadSession = useAuthStore((state) => state.loadSession);
    const isLoading = useAuthStore((state) => state.isLoading);

    // Load essential fonts
    const [fontsLoaded, fontError] = useFonts({
        NotoSansDevanagari: require('../assets/fonts/NotoSansDevanagari-Regular.ttf'),
    });

    useEffect(() => {
        // Attempt session restoration on mount
        loadSession();
    }, [loadSession]);

    useEffect(() => {
        // Hide splash screen once fonts are loaded and auth check is complete
        if ((fontsLoaded || fontError) && !isLoading) {
            SplashScreen.hideAsync().catch((err) =>
                console.error('[RootLayout] Error hiding splash screen:', err)
            );
        }
    }, [fontsLoaded, fontError, isLoading]);

    // Render minimal fallback while preparing core resources
    if (!fontsLoaded && !fontError) {
        return null;
    }

    return (
        <PaperProvider theme={paperTheme}>
            <Stack
                screenOptions={{
                    headerShown: false,
                    contentStyle: { backgroundColor: paperTheme.colors.background },
                    animation: 'fade', // Subtle fade transitions between screens
                }}
            >
                <Stack.Screen name="index" />
                <Stack.Screen name="(auth)" options={{ headerShown: false }} />
                <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
                <Stack.Screen name="listing" options={{ headerShown: false }} />
            </Stack>
        </PaperProvider>
    );
}
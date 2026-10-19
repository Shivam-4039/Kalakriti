import React from 'react';
import { Stack } from 'expo-router';
import { colors } from '../../theme';

export default function ListingLayout() {
    return (
        <Stack
            screenOptions={{
                headerShown: false,
                contentStyle: { backgroundColor: colors.background },
                animation: 'slide_from_right',
            }}
        >
            <Stack.Screen name="voice" />
            <Stack.Screen name="photo" />
            <Stack.Screen name="preview" />
            <Stack.Screen name="success" />
        </Stack>
    );
}
import React from 'react';
import { Tabs } from 'expo-router';
import { Home, Package, User } from 'lucide-react-native';
import { colors, layout, typography } from '../../theme';

export default function TabsLayout() {
    return (
        <Tabs
            screenOptions={{
                headerShown: false,
                tabBarActiveTintColor: colors.primary,
                tabBarInactiveTintColor: colors.textSecondary,
                tabBarStyle: {
                    backgroundColor: colors.surface,
                    borderTopColor: colors.border,
                    borderTopWidth: 1,
                    height: 70,
                    paddingBottom: layout.spacing.xs + 2,
                    paddingTop: layout.spacing.xs,
                },
                tabBarLabelStyle: {
                    fontSize: typography.sizes.caption,
                    fontWeight: '700',
                },
            }}
        >
            <Tabs.Screen
                name="index"
                options={{
                    title: 'होम (Home)',
                    tabBarIcon: ({ color, size }) => <Home size={size || 26} color={color} />,
                }}
            />
            <Tabs.Screen
                name="catalog"
                options={{
                    title: 'सामान (Catalog)',
                    tabBarIcon: ({ color, size }) => <Package size={size || 26} color={color} />,
                }}
            />
            <Tabs.Screen
                name="profile"
                options={{
                    title: 'प्रोफाइल (Profile)',
                    tabBarIcon: ({ color, size }) => <User size={size || 26} color={color} />,
                }}
            />
        </Tabs>
    );
}
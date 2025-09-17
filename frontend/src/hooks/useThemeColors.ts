import { useState, useEffect, useMemo } from 'react';

export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface ThemeColors {
  light: ColorPalette;
  dark: ColorPalette;
}

const defaultThemes: Record<string, ThemeColors> = {
  agrifrika: {
    light: {
      primary: '#22c55e',
      secondary: '#16a34a',
      accent: '#059669',
      background: '#ffffff',
      surface: '#f8fafc',
      text: '#1f2937',
      textSecondary: '#6b7280',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6'
    },
    dark: {
      primary: '#22c55e',
      secondary: '#16a34a',
      accent: '#059669',
      background: '#0f172a',
      surface: '#1e293b',
      text: '#f1f5f9',
      textSecondary: '#94a3b8',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6'
    }
  },
  ocean: {
    light: {
      primary: '#0ea5e9',
      secondary: '#0284c7',
      accent: '#0369a1',
      background: '#ffffff',
      surface: '#f0f9ff',
      text: '#0c4a6e',
      textSecondary: '#475569',
      success: '#059669',
      warning: '#d97706',
      error: '#dc2626',
      info: '#2563eb'
    },
    dark: {
      primary: '#38bdf8',
      secondary: '#0ea5e9',
      accent: '#0284c7',
      background: '#0c1117',
      surface: '#1e293b',
      text: '#e2e8f0',
      textSecondary: '#94a3b8',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6'
    }
  },
  sunset: {
    light: {
      primary: '#f97316',
      secondary: '#ea580c',
      accent: '#dc2626',
      background: '#fffbeb',
      surface: '#fef3c7',
      text: '#92400e',
      textSecondary: '#a3a3a3',
      success: '#059669',
      warning: '#d97706',
      error: '#dc2626',
      info: '#2563eb'
    },
    dark: {
      primary: '#fb923c',
      secondary: '#f97316',
      accent: '#ea580c',
      background: '#1c1917',
      surface: '#292524',
      text: '#fbbf24',
      textSecondary: '#a8a29e',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6'
    }
  },
  purple: {
    light: {
      primary: '#8b5cf6',
      secondary: '#7c3aed',
      accent: '#6d28d9',
      background: '#fefbff',
      surface: '#f3e8ff',
      text: '#581c87',
      textSecondary: '#6b7280',
      success: '#059669',
      warning: '#d97706',
      error: '#dc2626',
      info: '#2563eb'
    },
    dark: {
      primary: '#a78bfa',
      secondary: '#8b5cf6',
      accent: '#7c3aed',
      background: '#1e1b26',
      surface: '#2d2438',
      text: '#c4b5fd',
      textSecondary: '#a1a1aa',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6'
    }
  }
};

interface UseThemeColorsReturn {
  currentTheme: string;
  colors: ColorPalette;
  isDark: boolean;
  availableThemes: string[];
  setTheme: (theme: string) => void;
  generateGradient: (color1: string, color2: string, direction?: string) => string;
  getColorWithOpacity: (color: string, opacity: number) => string;
  adaptiveColor: (lightColor: string, darkColor: string) => string;
}

export const useThemeColors = (initialTheme: string = 'agrifrika'): UseThemeColorsReturn => {
  const [currentTheme, setCurrentTheme] = useState<string>(() => {
    const stored = localStorage.getItem('theme-colors');
    return stored || initialTheme;
  });

  const [isDark, setIsDark] = useState<boolean>(() => {
    const stored = localStorage.getItem('darkMode');
    if (stored !== null) {
      return JSON.parse(stored);
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const handleStorageChange = () => {
      const storedTheme = localStorage.getItem('theme-colors');
      const storedDarkMode = localStorage.getItem('darkMode');
      
      if (storedTheme && storedTheme !== currentTheme) {
        setCurrentTheme(storedTheme);
      }
      
      if (storedDarkMode !== null) {
        setIsDark(JSON.parse(storedDarkMode));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Listen for dark mode changes
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleDarkModeChange = (e: MediaQueryListEvent) => {
      const stored = localStorage.getItem('darkMode');
      if (stored === null) {
        setIsDark(e.matches);
      }
    };

    if (darkModeMediaQuery.addEventListener) {
      darkModeMediaQuery.addEventListener('change', handleDarkModeChange);
    }

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      if (darkModeMediaQuery.removeEventListener) {
        darkModeMediaQuery.removeEventListener('change', handleDarkModeChange);
      }
    };
  }, [currentTheme]);

  const colors = useMemo(() => {
    const themeColors = defaultThemes[currentTheme] || defaultThemes.agrifrika;
    return isDark ? themeColors.dark : themeColors.light;
  }, [currentTheme, isDark]);

  useEffect(() => {
    // Apply CSS custom properties for dynamic theming
    const root = document.documentElement;
    
    Object.entries(colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });

    // Apply theme class to body
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-${currentTheme}`);
  }, [colors, currentTheme]);

  const setTheme = (theme: string) => {
    if (defaultThemes[theme]) {
      setCurrentTheme(theme);
      localStorage.setItem('theme-colors', theme);
    }
  };

  const generateGradient = (color1: string, color2: string, direction: string = '135deg') => {
    return `linear-gradient(${direction}, ${color1}, ${color2})`;
  };

  const getColorWithOpacity = (color: string, opacity: number) => {
    // Convert hex to rgba
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
  };

  const adaptiveColor = (lightColor: string, darkColor: string) => {
    return isDark ? darkColor : lightColor;
  };

  return {
    currentTheme,
    colors,
    isDark,
    availableThemes: Object.keys(defaultThemes),
    setTheme,
    generateGradient,
    getColorWithOpacity,
    adaptiveColor
  };
};
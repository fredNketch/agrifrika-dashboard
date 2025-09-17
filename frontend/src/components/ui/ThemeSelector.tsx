import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckIcon, PaintBrushIcon } from '@heroicons/react/24/outline';
import { useThemeColors } from '../../hooks/useThemeColors';
import { useDarkMode } from '../../hooks/useDarkMode';

interface ThemeSelectorProps {
  className?: string;
}

const themePresets = {
  agrifrika: {
    name: 'Agrifrika',
    description: 'Thème principal vert nature',
    colors: ['#22c55e', '#16a34a', '#059669']
  },
  ocean: {
    name: 'Océan',
    description: 'Tons bleus apaisants',
    colors: ['#0ea5e9', '#0284c7', '#0369a1']
  },
  sunset: {
    name: 'Coucher de soleil',
    description: 'Chaleur orange et rouge',
    colors: ['#f97316', '#ea580c', '#dc2626']
  },
  purple: {
    name: 'Améthyste',
    description: 'Élégance violette',
    colors: ['#8b5cf6', '#7c3aed', '#6d28d9']
  }
};

const ThemeSelector: React.FC<ThemeSelectorProps> = ({ className = '' }) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const { currentTheme, setTheme, availableThemes } = useThemeColors();
  const { isDarkMode, toggle: toggleDarkMode } = useDarkMode();

  return (
    <div className={`relative ${className}`}>
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <PaintBrushIcon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Thèmes
        </span>
      </motion.button>

      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
              onClick={() => setIsOpen(false)}
            />

            {/* Theme Panel */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: -10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: -10 }}
              transition={{ type: "spring", duration: 0.3 }}
              className="absolute top-full right-0 mt-2 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-2xl z-50 overflow-hidden"
            >
              {/* Header */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    Personnalisation
                  </h3>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Dark Mode Toggle */}
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-gray-100">
                      Mode sombre
                    </h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Basculer entre les thèmes clair et sombre
                    </p>
                  </div>
                  <motion.button
                    onClick={toggleDarkMode}
                    className={`relative w-12 h-6 rounded-full transition-colors duration-300 ${
                      isDarkMode ? 'bg-blue-500' : 'bg-gray-300'
                    }`}
                    whileTap={{ scale: 0.95 }}
                  >
                    <motion.div
                      className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-md"
                      animate={{ x: isDarkMode ? 24 : 0 }}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  </motion.button>
                </div>
              </div>

              {/* Theme Options */}
              <div className="p-6">
                <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-4">
                  Palette de couleurs
                </h4>
                <div className="space-y-3">
                  {availableThemes.map((themeKey) => {
                    const theme = themePresets[themeKey as keyof typeof themePresets];
                    if (!theme) return null;

                    const isSelected = currentTheme === themeKey;

                    return (
                      <motion.button
                        key={themeKey}
                        onClick={() => setTheme(themeKey)}
                        className={`w-full p-3 rounded-xl border-2 transition-all duration-300 ${
                          isSelected
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                        }`}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <div className="flex items-center space-x-3">
                          {/* Color Preview */}
                          <div className="flex space-x-1">
                            {theme.colors.map((color, index) => (
                              <div
                                key={index}
                                className="w-4 h-4 rounded-full border-2 border-white shadow-sm"
                                style={{ backgroundColor: color }}
                              />
                            ))}
                          </div>

                          {/* Theme Info */}
                          <div className="flex-1 text-left">
                            <div className="font-medium text-gray-900 dark:text-gray-100">
                              {theme.name}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {theme.description}
                            </div>
                          </div>

                          {/* Selected Indicator */}
                          {isSelected && (
                            <motion.div
                              initial={{ scale: 0 }}
                              animate={{ scale: 1 }}
                              className="flex items-center justify-center w-6 h-6 bg-blue-500 rounded-full"
                            >
                              <CheckIcon className="w-4 h-4 text-white" />
                            </motion.div>
                          )}
                        </div>
                      </motion.button>
                    );
                  })}
                </div>
              </div>

              {/* Footer */}
              <div className="p-6 bg-gray-50 dark:bg-gray-900/50">
                <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                  Les préférences sont sauvegardées automatiquement
                </p>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ThemeSelector;
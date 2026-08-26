import { useEffect } from 'react';

export const useKeyboardShortcuts = (shortcuts) => {
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Check if user is typing in an input field
      const isInputFocused = ['INPUT', 'TEXTAREA', 'SELECT'].includes(
        document.activeElement.tagName
      );
      const isContentEditable = document.activeElement.isContentEditable;

      for (const shortcut of shortcuts) {
        const { key, ctrlKey = false, shiftKey = false, metaKey = false, callback, ignoreInInput = false } = shortcut;
        
        // Skip if in input and shortcut should be ignored
        if (isInputFocused || isContentEditable) {
          if (ignoreInInput) continue;
        }

        // Check if all modifiers match
        const ctrlMatch = ctrlKey === (event.ctrlKey || event.metaKey);
        const shiftMatch = shiftKey === event.shiftKey;
        const metaMatch = metaKey === event.metaKey;
        const keyMatch = key.toLowerCase() === event.key.toLowerCase();

        if (ctrlMatch && shiftMatch && metaMatch && keyMatch) {
          event.preventDefault();
          callback(event);
          break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts]);
};

export default useKeyboardShortcuts;

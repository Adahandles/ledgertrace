import { writable } from 'svelte/store';
import { browser } from '$app/environment';

// Dark mode store with localStorage persistence
function createDarkModeStore() {
    const { subscribe, set, update } = writable(false);
    
    return {
        subscribe,
        init: () => {
            if (browser) {
                // Check localStorage first, then system preference
                const stored = localStorage.getItem('darkMode');
                if (stored !== null) {
                    const isDark = JSON.parse(stored);
                    set(isDark);
                    updateDOM(isDark);
                } else {
                    // Use system preference as default
                    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                    set(prefersDark);
                    updateDOM(prefersDark);
                }
            }
        },
        toggle: () => {
            update(isDark => {
                const newValue = !isDark;
                if (browser) {
                    localStorage.setItem('darkMode', JSON.stringify(newValue));
                    updateDOM(newValue);
                }
                return newValue;
            });
        },
        enable: () => {
            set(true);
            if (browser) {
                localStorage.setItem('darkMode', 'true');
                updateDOM(true);
            }
        },
        disable: () => {
            set(false);
            if (browser) {
                localStorage.setItem('darkMode', 'false');
                updateDOM(false);
            }
        }
    };
}

function updateDOM(isDark) {
    if (browser) {
        const root = document.documentElement;
        if (isDark) {
            root.classList.add('dark');
            root.classList.remove('light');
        } else {
            root.classList.add('light');
            root.classList.remove('dark');
        }
    }
}

export const darkMode = createDarkModeStore();
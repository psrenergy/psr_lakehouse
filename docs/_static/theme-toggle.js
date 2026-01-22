// Theme toggle functionality
(function() {
    'use strict';

    // Get theme from localStorage or default to light
    function getTheme() {
        return localStorage.getItem('theme') || 'light';
    }

    // Set theme
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        updateToggleText(theme);
    }

    // Update toggle text
    function updateToggleText(theme) {
        const textElement = document.querySelector('.theme-toggle-text');
        if (textElement) {
            textElement.textContent = theme === 'dark' ? 'Dark Mode' : 'Light Mode';
        }
    }

    // Toggle theme
    function toggleTheme() {
        const currentTheme = getTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }

    // Create theme toggle switch
    function createThemeToggle() {
        const container = document.createElement('div');
        container.className = 'theme-toggle-container';
        
        const label = document.createElement('label');
        label.className = 'theme-toggle-label';
        
        const text = document.createElement('span');
        text.className = 'theme-toggle-text';
        text.textContent = getTheme() === 'dark' ? 'Dark Mode' : 'Light Mode';
        
        const switchElement = document.createElement('div');
        switchElement.className = 'theme-toggle-switch';
        
        label.appendChild(text);
        label.appendChild(switchElement);
        container.appendChild(label);
        
        label.onclick = toggleTheme;
        
        return container;
    }
  
    // Initialize theme on page load
    function initTheme() {
        const theme = getTheme();
        setTheme(theme);

        // Find sidebar and add theme toggle at the bottom
        const sidebar = document.querySelector('.sphinxsidebar');
        if (sidebar) {
            const themeToggle = createThemeToggle();
            sidebar.appendChild(themeToggle);
        }
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
})();

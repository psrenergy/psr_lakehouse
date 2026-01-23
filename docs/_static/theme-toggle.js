// Theme toggle functionality
(function() {
    'use strict';

    // Get theme from localStorage or default to light
    function getTheme() {
        return localStorage.getItem('theme') || 'light';
    }

    // Update toggle icon
    function updateToggleIcon(theme) {
        const button = document.querySelector('.theme-toggle-btn');
        if (button) {
            button.innerHTML = theme === 'dark' ? getSunIcon() : getMoonIcon();
            button.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        }
    }

    // SVG Icons
    function getSunIcon() {
        return '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
    }

    function getMoonIcon() {
        return '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
    }

    // Toggle theme
    function toggleTheme() {
        const currentTheme = getTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }

    // Create floating theme toggle button
    function createThemeToggle() {
        const button = document.createElement('button');
        button.className = 'theme-toggle-btn';
        button.innerHTML = getTheme() === 'dark' ? getSunIcon() : getMoonIcon();
        button.setAttribute('aria-label', getTheme() === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        button.onclick = toggleTheme;
        return button;
    }

    // Create PSR logo
    function createPSRLogo() {
        const container = document.createElement('div');
        container.className = 'psr-logo-container';
        
        const img = document.createElement('img');
        img.className = 'psr-logo';
        img.alt = 'PSR';
        
        // Set image based on theme
        const theme = getTheme();
        img.src = theme === 'dark' ? '_static/img/psr_dark.png' : '_static/img/psr_light.png';
        
        container.appendChild(img);
        
        return container;
    }

    // Update PSR logo when theme changes
    function updatePSRLogo(theme) {
        const logo = document.querySelector('.psr-logo');
        if (logo) {
            logo.src = theme === 'dark' ? '_static/img/psr_dark.png' : '_static/img/psr_light.png';
        }
    }

    // Create mobile menu toggle button
    function createMobileMenuToggle() {
        const button = document.createElement('button');
        button.className = 'mobile-menu-toggle';
        button.setAttribute('aria-label', 'Toggle navigation menu');
        
        // Create hamburger lines
        for (let i = 0; i < 3; i++) {
            const span = document.createElement('span');
            button.appendChild(span);
        }
        
        return button;
    }

    // Create mobile header
    function createMobileHeader() {
        const header = document.createElement('div');
        header.className = 'mobile-header';

        const menuButton = createMobileMenuToggle();

        const title = document.createElement('span');
        title.className = 'mobile-header-title';
        title.textContent = 'PSR Lakehouse';

        const themeToggle = createThemeToggle();

        header.appendChild(menuButton);
        header.appendChild(title);
        header.appendChild(themeToggle);

        return header;
    }

    // Create mobile menu overlay
    function createMobileOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'mobile-menu-overlay';
        return overlay;
    }

    // Toggle mobile menu
    function toggleMobileMenu() {
        const sidebar = document.querySelector('.sphinxsidebar');
        const overlay = document.querySelector('.mobile-menu-overlay');
        const button = document.querySelector('.mobile-menu-toggle');
        
        if (sidebar && overlay && button) {
            const isActive = sidebar.classList.contains('mobile-active');
            
            if (isActive) {
                sidebar.classList.remove('mobile-active');
                overlay.classList.remove('active');
                button.classList.remove('active');
                document.body.style.overflow = '';
            } else {
                sidebar.classList.add('mobile-active');
                overlay.classList.add('active');
                button.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        }
    }

    // Update theme setter to also update logo and icon
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        updateToggleIcon(theme);
        updatePSRLogo(theme);
    }

    // GitHub icon SVG
    function getGithubIcon() {
        return '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>';
    }

    // Create GitHub button at bottom of sidebar
    function createGithubButton() {
        const container = document.createElement('div');
        container.className = 'github-container';

        const link = document.createElement('a');
        link.href = 'https://github.com/psrenergy/psr_lakehouse';
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.innerHTML = getGithubIcon() + ' GitHub';

        container.appendChild(link);
        return container;
    }

    // Remove existing GitHub elements from Alabaster
    function removeAlabasterGithub() {
        const sidebar = document.querySelector('.sphinxsidebar');
        if (!sidebar) return;

        // Remove any existing GitHub buttons/iframes from Alabaster
        const githubElements = sidebar.querySelectorAll('a.github-button, iframe[src*="github"], p > a[href*="github.com"]');
        githubElements.forEach(el => {
            const parent = el.closest('p');
            if (parent) {
                parent.remove();
            } else {
                el.remove();
            }
        });
    }

    // Clean up sidebar: remove headings, style search box
    function cleanupSidebar() {
        const sidebar = document.querySelector('.sphinxsidebar');
        if (!sidebar) return;

        // Remove "Navigation" and "Quick search" headings
        const headings = sidebar.querySelectorAll('h3');
        headings.forEach(h3 => {
            const text = h3.textContent.toLowerCase();
            if (text.includes('navigation') || text.includes('quick search') || text.includes('search')) {
                h3.remove();
            }
        });

        // Style the search input
        const searchInput = sidebar.querySelector('input[type="text"], input[name="q"]');
        if (searchInput) {
            searchInput.placeholder = 'Search';
            searchInput.classList.add('search-input-styled');
        }

        // Remove the "Go" button
        const goButton = sidebar.querySelector('input[type="submit"], input[value="Go"]');
        if (goButton) {
            goButton.remove();
        }

        // Wrap search input with icon container
        if (searchInput && !searchInput.parentElement.classList.contains('search-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'search-wrapper';

            const icon = document.createElement('span');
            icon.className = 'search-icon';
            icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>';

            searchInput.parentNode.insertBefore(wrapper, searchInput);
            wrapper.appendChild(icon);
            wrapper.appendChild(searchInput);
        }

    }

    // Initialize theme on page load
    function initTheme() {
        const theme = getTheme();
        document.documentElement.setAttribute('data-theme', theme);

        // Find sidebar and add components at the bottom
        const sidebar = document.querySelector('.sphinxsidebar');
        if (sidebar) {
            // Clean up sidebar (remove headings, style search)
            cleanupSidebar();

            // Remove Alabaster's GitHub widget
            removeAlabasterGithub();

            // Add PSR logo first
            const psrLogo = createPSRLogo();
            sidebar.appendChild(psrLogo);

            // Add GitHub button below logo
            const githubButton = createGithubButton();
            sidebar.appendChild(githubButton);
        }

        // Add floating theme toggle button to body
        const themeToggle = createThemeToggle();
        document.body.appendChild(themeToggle);

        // Add mobile header
        const mobileHeader = createMobileHeader();
        const mobileOverlay = createMobileOverlay();

        document.body.insertBefore(mobileHeader, document.body.firstChild);
        document.body.appendChild(mobileOverlay);

        // Add click handlers
        const mobileButton = mobileHeader.querySelector('.mobile-menu-toggle');
        mobileButton.addEventListener('click', toggleMobileMenu);
        mobileOverlay.addEventListener('click', toggleMobileMenu);

        // Close menu when clicking sidebar links on mobile
        if (sidebar) {
            sidebar.addEventListener('click', function(e) {
                if (e.target.tagName === 'A' && window.innerWidth <= 875) {
                    toggleMobileMenu();
                }
            });
        }

        // Update icon after DOM is ready
        updateToggleIcon(theme);
        updatePSRLogo(theme);
    }

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
})();

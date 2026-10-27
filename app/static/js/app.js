/**
 * SETFIT DARK RAGE - Core Client Scripts & Theme Engine
 */

// 1. Dual Theme Toggle Engine (Dark / Light) with Persistence
function initThemeEngine() {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    
    // Read current theme from html data-theme
    function getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') || 'dark';
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try {
            localStorage.setItem('setfit_theme', theme);
        } catch (e) {
            // Privacy mode / quota exceeded fallback
        }
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const newTheme = getCurrentTheme() === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    }
}

// 2. Preloader Auto-Dismissal
function dismissPreloader() {
    const preloader = document.getElementById('appPreloader');
    if (preloader) {
        preloader.classList.add('loaded');
        setTimeout(() => {
            if (preloader.parentNode) {
                preloader.style.display = 'none';
            }
        }, 400);
    }
}

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    // Dismiss preloader
    dismissPreloader();

    // Init Theme Toggle
    initThemeEngine();

    // Auto dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            } catch (e) {}
        }, 6000);
    });

    // Real-time clock if element exists
    const liveClockEl = document.getElementById('liveClock');
    if (liveClockEl) {
        function updateClock() {
            const now = new Date();
            liveClockEl.innerText = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        }
        updateClock();
        setInterval(updateClock, 1000);
    }
});

// Fallback: window load
window.addEventListener('load', () => {
    dismissPreloader();
});

// Safety timeout: dismiss preloader after 800ms max under all conditions
setTimeout(dismissPreloader, 800);

// Copy text utility (e.g. for UPI VPA copy)
function copyToClipboard(text, triggerBtn) {
    if (!navigator.clipboard) return;
    navigator.clipboard.writeText(text).then(() => {
        const originalHtml = triggerBtn.innerHTML;
        triggerBtn.innerHTML = '<i class="fas fa-check text-success"></i> Copied!';
        setTimeout(() => {
            triggerBtn.innerHTML = originalHtml;
        }, 2000);
    }).catch(err => {
        console.error('Clipboard copy failed: ', err);
    });
}

// ============================================
// BioLearn AI - Enhanced UX Utilities
// Smooth transitions and loading states
// ============================================

/**
 * Page transition system
 */
class PageTransition {
    constructor() {
        this.setupTransitions();
    }

    setupTransitions() {
        // Add fade-in class to body on page load
        document.addEventListener('DOMContentLoaded', () => {
            document.body.classList.add('fade-in');
        });

        // Intercept link clicks for smooth transitions
        document.querySelectorAll('a:not([target="_blank"])').forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');

                // Skip if it's a hash link or external link
                if (!href || href.startsWith('#') || href.startsWith('http')) {
                    return;
                }

                // Skip if it's a form submission
                if (link.closest('form')) {
                    return;
                }

                e.preventDefault();

                // Fade out
                document.body.style.opacity = '0';
                document.body.style.transition = 'opacity 0.2s ease-out';

                // Navigate after fade
                setTimeout(() => {
                    window.location.href = href;
                }, 200);
            });
        });
    }
}

/**
 * Loading state manager
 */
class LoadingState {
    constructor(element, options = {}) {
        this.element = element;
        this.originalText = element.textContent;
        this.loadingText = options.loadingText || 'Loading...';
    }

    start() {
        this.element.classList.add('btn-loading');
        this.element.disabled = true;
        this.element.textContent = this.loadingText;
    }

    stop() {
        this.element.classList.remove('btn-loading');
        this.element.disabled = false;
        this.element.textContent = this.originalText;
    }
}

/**
 * Toast notification system
 */
class Toast {
    static show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 24px;
            right: 24px;
            padding: 16px 24px;
            background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#6366F1'};
            color: white;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

/**
 * Skeleton loader helper
 */
class SkeletonLoader {
    static create(count = 3, height = '80px') {
        const skeletons = [];
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'card skeleton';
            skeleton.style.height = height;
            skeletons.push(skeleton);
        }
        return skeletons;
    }

    static replace(container, elements) {
        container.innerHTML = '';
        elements.forEach(el => {
            if (typeof el === 'string') {
                container.innerHTML += el;
            } else {
                container.appendChild(el);
            }
        });
    }
}

/**
 * Form validation helper
 */
class FormValidator {
    static validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    static validatePassword(password) {
        return password.length >= 8;
    }

    static showError(input, message) {
        input.classList.add('input-error');
        const existingError = input.parentElement.querySelector('.field-error');
        if (existingError) existingError.remove();

        const error = document.createElement('div');
        error.className = 'field-error';
        error.style.cssText = 'color: #EF4444; font-size: 12px; margin-top: 4px;';
        error.textContent = message;
        input.parentElement.appendChild(error);
    }

    static clearError(input) {
        input.classList.remove('input-error');
        const error = input.parentElement.querySelector('.field-error');
        if (error) error.remove();
    }
}

/**
 * API helper with loading states
 */
class API {
    static async call(url, options = {}) {
        try {
            const response = await fetch(url, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            Toast.show(error.message || 'Something went wrong', 'error');
            throw error;
        }
    }

    static async get(url) {
        return this.call(url, { method: 'GET' });
    }

    static async post(url, data) {
        return this.call(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
}

/**
 * Utility: Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility: Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Utility: Format time duration
 */
function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
        return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
}

/**
 * Utility: Relative time (e.g., "2 hours ago")
 */
function relativeTime(date) {
    const now = new Date();
    const then = new Date(date);
    const diff = Math.floor((now - then) / 1000); // seconds

    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} days ago`;
    return then.toLocaleDateString();
}

// Initialize page transitions
const pageTransition = new PageTransition();

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }

    .field-error {
        animation: shake 0.3s;
    }

    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        PageTransition,
        LoadingState,
        Toast,
        SkeletonLoader,
        FormValidator,
        API,
        debounce,
        formatNumber,
        formatDuration,
        relativeTime
    };
}

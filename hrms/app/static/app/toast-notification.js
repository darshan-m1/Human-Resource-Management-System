// Toast Notification System for HRMS
class ToastNotification {
    constructor() {
        this.container = null;
        this.activeToasts = new Set();
        this.init();
    }

    init() {
        // Create toast container if it doesn't exist
        if (!document.getElementById('toast-container')) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 12px;
                max-width: 400px;
                width: 100%;
                pointer-events: none;
            `;
            document.body.appendChild(this.container);
        } else {
            this.container = document.getElementById('toast-container');
        }
    }

    show(message, type = 'info', options = {}) {
        const toast = this.createToast(message, type, options);
        this.container.appendChild(toast);
        this.activeToasts.add(toast);

        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
            toast.style.opacity = '1';
            toast.style.transform = 'translateY(0)';
        }, 10);

        // Setup auto-dismiss
        const duration = options.duration || 1600;
        if (duration > 0) {
            const dismissTimer = setTimeout(() => {
                this.removeToast(toast);
            }, duration);
            
            // Store timer reference on toast element for cleanup
            toast._dismissTimer = dismissTimer;
        }

        return toast;
    }

    createToast(message, type, options) {
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.style.cssText = `
            opacity: 0;
            transform: translateY(-20px);
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            max-height: 0;
            overflow: hidden;
        `;
        
        // Get icon and color based on type
        const { icon, gradient, iconClass } = this.getToastConfig(type);
        
        toast.innerHTML = `
            <div class="toast-content glass-card p-3 d-flex align-items-start" style="
                background: rgba(255, 255, 255, 0.98);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                pointer-events: auto;
                border-left: 4px solid ${this.getBorderColor(type)};
            ">
                <div class="icon-wrapper me-3" style="
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: ${gradient};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-shrink: 0;
                ">
                    <i class="${icon} fs-5 text-white"></i>
                </div>
                <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="mb-0 fw-bold" style="
                            background: ${gradient};
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            background-clip: text;
                        ">
                            ${this.capitalizeFirstLetter(type)}
                        </h6>
                        <button type="button" class="btn-close toast-close" 
                                style="font-size: 0.7rem; padding: 0.5rem;"
                                aria-label="Close">
                        </button>
                    </div>
                    <p class="mb-0 text-dark opacity-90" style="font-size: 0.9rem;">
                        ${message}
                    </p>
                    ${options.progress !== false ? `
                        <div class="progress mt-3" style="height: 3px; border-radius: 2px; background: rgba(0,0,0,0.1); overflow: hidden;">
                            <div class="progress-bar progress-animation" style="
                                background: ${gradient};
                                width: 100%;
                                height: 100%;
                                border-radius: 2px;
                            " data-duration="${options.duration || 1600}"></div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Add close button functionality
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.removeToast(toast);
        });

        // Add click to dismiss (optional)
        if (options.clickToDismiss !== false) {
            toast.addEventListener('click', () => {
                this.removeToast(toast);
            });
        }

        // Start progress bar animation
        if (options.progress !== false) {
            setTimeout(() => {
                const progressBar = toast.querySelector('.progress-bar');
                if (progressBar) {
                    const duration = parseInt(progressBar.getAttribute('data-duration')) - 100;
                    progressBar.style.transition = `width ${duration}ms linear`;
                    progressBar.style.width = '0%';
                }
            }, 100);
        }

        return toast;
    }

    getToastConfig(type) {
        const configs = {
            success: {
                icon: 'bi bi-check-circle-fill',
                gradient: 'linear-gradient(135deg, #10b981, #34d399)',
                iconClass: 'text-success'
            },
            error: {
                icon: 'bi bi-x-circle-fill',
                gradient: 'linear-gradient(135deg, #ef4444, #f87171)',
                iconClass: 'text-danger'
            },
            warning: {
                icon: 'bi bi-exclamation-triangle-fill',
                gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)',
                iconClass: 'text-warning'
            },
            info: {
                icon: 'bi bi-info-circle-fill',
                gradient: 'linear-gradient(135deg, #3b82f6, #60a5fa)',
                iconClass: 'text-info'
            },
            primary: {
                icon: 'bi bi-bell-fill',
                gradient: 'linear-gradient(135deg, #4361ee, #3a0ca3)',
                iconClass: 'text-primary'
            }
        };

        return configs[type] || configs.info;
    }

    getBorderColor(type) {
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#3b82f6',
            primary: '#4361ee'
        };
        return colors[type] || colors.info;
    }

    removeToast(toast) {
        if (!toast || !this.activeToasts.has(toast)) return;

        // Clear any existing timer
        if (toast._dismissTimer) {
            clearTimeout(toast._dismissTimer);
        }

        // Animate out
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px) scale(0.95)';
        toast.style.maxHeight = '0';
        toast.style.marginBottom = '0';
        toast.style.pointerEvents = 'none';

        // Remove from DOM after animation
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.activeToasts.delete(toast);
        }, 400);
    }

    capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
}

// Create global instance
window.ToastNotification = new ToastNotification();

// Add CSS for animations
const toastStyles = document.createElement('style');
toastStyles.textContent = `
    .toast-notification {
        animation: toastSlideIn 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
    }
    
    @keyframes toastSlideIn {
        from {
            opacity: 0;
            transform: translateY(-20px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    .toast-notification.exit {
        animation: toastSlideOut 0.3s ease forwards;
    }
    
    @keyframes toastSlideOut {
        to {
            opacity: 0;
            transform: translateY(-20px) scale(0.95);
            max-height: 0;
            margin-bottom: 0;
        }
    }
    
    .toast-content:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .toast-close {
        transition: all 0.2s ease;
    }
    
    .toast-close:hover {
        opacity: 0.8 !important;
        transform: scale(1.1) !important;
    }
    
    .progress-animation {
        transition: width linear !important;
    }
`;
document.head.appendChild(toastStyles);

// Export for use in other modules
export default ToastNotification;

// Helper function for easy usage
window.showNotification = function(message, type = 'info', options = {}) {
    return window.ToastNotification.show(message, type, options);
};
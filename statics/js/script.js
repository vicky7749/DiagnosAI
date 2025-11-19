// DiagnosAI - Main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                bootstrap.Alert.getInstance(alert).close();
            }
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    });

    // Password strength indicator
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const strengthIndicator = document.getElementById('password-strength');
            if (!strengthIndicator) return;

            const password = this.value;
            let strength = 0;

            if (password.length >= 8) strength++;
            if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
            if (password.match(/\d/)) strength++;
            if (password.match(/[^a-zA-Z\d]/)) strength++;

            const strengthText = ['Very Weak', 'Weak', 'Medium', 'Strong', 'Very Strong'][strength];
            const strengthClass = ['danger', 'danger', 'warning', 'success', 'success'][strength];

            strengthIndicator.textContent = strengthText;
            strengthIndicator.className = `badge bg-${strengthClass}`;
        });
    }
});

// API functions
const DiagnosAI = {
    // Predict disease via API
    async predictDisease(diseaseType, symptoms) {
        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    disease_type: diseaseType,
                    symptoms: symptoms
                })
            });
            
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Prediction error:', error);
            return { success: false, error: error.message };
        }
    },

    // Get user prediction history
    async getUserHistory() {
        try {
            const response = await fetch('/api/history');
            return await response.json();
        } catch (error) {
            console.error('History fetch error:', error);
            return { success: false, error: error.message };
        }
    },

    // Validate symptoms input
    validateSymptoms(symptoms) {
        const errors = [];
        
        for (const [symptom, value] of Object.entries(symptoms)) {
            if (value === '' || value === null || value === undefined) {
                errors.push(`${symptom} is required`);
            } else if (isNaN(value)) {
                errors.push(`${symptom} must be a number`);
            } else if (value < 0 || value > 10) {
                errors.push(`${symptom} must be between 0 and 10`);
            }
        }
        
        return errors;
    },

    // Format symptom name for display
    formatSymptomName(symptom) {
        return symptom.replace(/_/g, ' ')
                     .replace(/\b\w/g, l => l.toUpperCase());
    },

    // Show notification
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.querySelector('.container').prepend(notification);
        
        setTimeout(() => {
            if (notification.classList.contains('show')) {
                bootstrap.Alert.getInstance(notification).close();
            }
        }, 5000);
    }
};

// Utility functions
const Utils = {
    // Debounce function for search inputs
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Format date
    formatDate(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(dateString).toLocaleDateString(undefined, options);
    },

    // Copy to clipboard
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            DiagnosAI.showNotification('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
        });
    }
};

// Export for global access
window.DiagnosAI = DiagnosAI;
window.Utils = Utils;
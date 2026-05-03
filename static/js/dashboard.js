document.addEventListener('DOMContentLoaded', function() {
    // Animate health score bar
    const healthFill = document.querySelector('.health-score-fill');
    if (healthFill) {
        const score = parseInt(healthFill.dataset.healthScore) || 0;
        // Delay to allow CSS transition to work
        setTimeout(() => {
            healthFill.style.width = Math.max(0, Math.min(100, score)) + '%';
        }, 100);
    }

    // Format timestamps
    const timestampElements = document.querySelectorAll('[data-timestamp]');
    timestampElements.forEach(el => {
        const timestamp = el.dataset.timestamp;
        if (timestamp) {
            const date = new Date(timestamp);
            if (!isNaN(date.getTime())) {
                const now = new Date();
                const diffMs = now - date;
                const diffMins = Math.floor(diffMs / 60000);
                const diffHours = Math.floor(diffMs / 3600000);
                const diffDays = Math.floor(diffMs / 86400000);

                let text;
                if (diffMins < 1) {
                    text = 'Just now';
                } else if (diffMins < 60) {
                    text = diffMins + ' min ago';
                } else if (diffHours < 24) {
                    text = diffHours + ' hour' + (diffHours > 1 ? 's' : '') + ' ago';
                } else if (diffDays < 7) {
                    text = diffDays + ' day' + (diffDays > 1 ? 's' : '') + ' ago';
                } else {
                    text = date.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                }
                el.textContent = text;
            }
        }
    });

    // Animate metric values on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.panel').forEach(panel => {
        observer.observe(panel);
    });

    // Add click handler for trip sections (accordion-like)
    const tripSectionHeaders = document.querySelectorAll('.trip-section-header');
    tripSectionHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            let nextEl = this.nextElementSibling;
            let steps = [];
            while (nextEl && nextEl.classList.contains('trip-step')) {
                steps.push(nextEl);
                nextEl = nextEl.nextElementSibling;
            }
            
            const isCollapsed = steps[0] && steps[0].style.display === 'none';
            steps.forEach(step => {
                step.style.display = isCollapsed ? 'block' : 'none';
            });
            
            // Toggle icon rotation
            const svg = this.querySelector('svg');
            if (svg) {
                svg.style.transform = isCollapsed ? 'rotate(0deg)' : 'rotate(-90deg)';
                svg.style.transition = 'transform 0.2s';
            }
        });
    });

    // Smooth scroll for nav links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Handle empty states gracefully
    function checkEmptyStates() {
        document.querySelectorAll('.item-list').forEach(list => {
            if (list.children.length === 0) {
                const emptyState = document.createElement('div');
                emptyState.className = 'empty-state';
                emptyState.innerHTML = `
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <p>No items to display</p>
                `;
                list.parentNode.appendChild(emptyState);
            }
        });
    }
    
    checkEmptyStates();
});
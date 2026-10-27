/**
 * SETFIT DARK RAGE - Hero Background Slideshow Engine
 * Automatic crossfading + Manual Next/Prev Controls & Slide Indicators
 * Robust Fallback: Handles offline images and mobile touch navigation
 */
(function() {
    function initHeroSlider() {
        const slides = document.querySelectorAll('.hero-bg-slide');
        const indicators = document.querySelectorAll('.hero-indicator');
        const prevBtn = document.getElementById('heroPrevBtn');
        const nextBtn = document.getElementById('heroNextBtn');

        if (!slides || slides.length === 0) return;

        let currentSlide = 0;
        const totalSlides = slides.length;
        const slideIntervalTime = 5000; // 5 seconds
        let slideTimer = null;

        function showSlide(index) {
            // Remove active from current
            slides[currentSlide].classList.remove('active');
            if (indicators && indicators[currentSlide]) {
                indicators[currentSlide].classList.remove('active');
            }

            // Wrap index
            currentSlide = (index + totalSlides) % totalSlides;

            // Add active to next
            slides[currentSlide].classList.add('active');
            if (indicators && indicators[currentSlide]) {
                indicators[currentSlide].classList.add('active');
            }
        }

        function nextSlide() {
            showSlide(currentSlide + 1);
        }

        function prevSlide() {
            showSlide(currentSlide - 1);
        }

        function startAutoSlide() {
            if (slideTimer) clearInterval(slideTimer);
            slideTimer = setInterval(nextSlide, slideIntervalTime);
        }

        function resetAutoSlide() {
            clearInterval(slideTimer);
            startAutoSlide();
        }

        // Initialize first slide
        showSlide(0);
        startAutoSlide();

        // Manual button listeners
        if (nextBtn) {
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                nextSlide();
                resetAutoSlide();
            });
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                prevSlide();
                resetAutoSlide();
            });
        }

        // Indicator button listeners
        if (indicators && indicators.length > 0) {
            indicators.forEach((indicator, idx) => {
                indicator.addEventListener('click', () => {
                    showSlide(idx);
                    resetAutoSlide();
                });
            });
        }

        // Mobile swipe support
        let touchStartX = 0;
        let touchEndX = 0;
        const heroSection = document.querySelector('.hero-slider-section');
        if (heroSection) {
            heroSection.addEventListener('touchstart', (e) => {
                touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });

            heroSection.addEventListener('touchend', (e) => {
                touchEndX = e.changedTouches[0].screenX;
                if (touchStartX - touchEndX > 50) {
                    nextSlide();
                    resetAutoSlide();
                } else if (touchEndX - touchStartX > 50) {
                    prevSlide();
                    resetAutoSlide();
                }
            }, { passive: true });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initHeroSlider);
    } else {
        initHeroSlider();
    }
})();

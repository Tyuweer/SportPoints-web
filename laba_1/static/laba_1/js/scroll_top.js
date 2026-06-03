class ScrollToTopButton {
    constructor(options = {}) {
        this.scrollThreshold = options.scrollThreshold || 400;
        this.button = null;
        this.init();
    }

    init() {
        this.createButton();
        this.bindEvents();
    }

    createButton() {
        this.button = document.createElement('button');
        this.button.className = 'scroll_top';
        this.button.innerHTML = '&#8593;';
        document.body.appendChild(this.button);
    }

    bindEvents() {

        window.addEventListener('scroll', () => this.handleScroll());

        this.button.addEventListener('click', () => this.scrollToTop());
    }

    handleScroll() {
        const scrollTop = window.pageYOffset

        if (scrollTop > this.scrollThreshold) {
            this.button.classList.add('show');
        } else {
            this.button.classList.remove('show');
        }
    }

    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
}

export default ScrollToTopButton;
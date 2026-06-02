class TelegramModal {
    constructor(options = {}) {
        this.telegramUrl = options.telegramUrl || 'https://t.me/finswimmingnews';
        this.modalId = options.modalId || 'telegram-subscribe-modal';
        this.showDelay = options.showDelay || 2000;
        this.overlay = null;
        this.init();
    }

    init() {
        this.createModal();
        this.bindEvents();

        setTimeout(() => {this.show();}, this.showDelay);
    }

    createModal() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'modal-overlay';
        this.overlay.id = this.modalId;

        this.overlay.innerHTML = `
            <div class="modal-window">
                <div class="modal-header">
                    <h2>Подпишитесь на наш Telegram!</h2>
                    <button class="modal-close" aria-label="Закрыть">&times;</button>
                </div>
                <div class="modal-body">
                    <p>Будьте в курсе всех новостей и обновлений!</p>
                    <p>Подписывайтесь на наш Telegram канал, чтобы не пропустить важную информацию о соревнованиях, результатах и новых возможностях.</p>
                    <a href="${this.telegramUrl}" target="_blank" class="modal-telegram-btn">
                        Подписаться на канал
                    </a>
                </div>
            </div>
        `;

        document.body.appendChild(this.overlay);
    }

    bindEvents() {
        const closeBtn = this.overlay.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => this.hide());


        this.overlay.addEventListener('click', (e) => {
            if (e.target === this.overlay) {
                this.hide();
            }
        });
    }

    show() {
        this.overlay.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    hide() {
        this.overlay.classList.remove('show');
        document.body.style.overflow = '';
    }

    isVisible() {
        return this.overlay.classList.contains('show');
    }
}

export default TelegramModal;
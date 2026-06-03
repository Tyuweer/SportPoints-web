class FormValidator {
    constructor(options = {}) {
        this.stickerContainer = null;
        this.defaultMessages = {
            email: 'Введите корректный email адрес (например: example@mail.ru)',
            phone: 'Введите корректный номер телефона в формате +7 (XXX) XXX-XX-XX',
            password: 'Пароль должен содержать минимум 8 символов, включая буквы и цифры',
            required: 'Это поле обязательно для заполнения'
            
        };
        this.messages = { ...this.defaultMessages, ...options.messages };
        this.init();
    }

    init() {
        this.createStickerContainer();
        this.bindEvents();
    }

    createStickerContainer() {
        this.stickerContainer = document.createElement('div');
        this.stickerContainer.className = 'sticker-container';
        document.body.appendChild(this.stickerContainer);
    }

    bindEvents() {
        const emailInputs = document.querySelectorAll('input[type="email"]');
        const telInputs = document.querySelectorAll('input[type="tel"]');
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        const textInputs = document.querySelectorAll('input[type="text"]');
        const checkboxInputs = document.querySelectorAll('input[type="checkbox"][required]');

        checkboxInputs.forEach(input => {

        input.addEventListener('invalid', (e) => {
            e.preventDefault(); 
            this.validateCheckbox(input, true);
        });

        input.addEventListener('change', () => this.validateCheckbox(input, true));
    });
        checkboxInputs.forEach(input => {
        input.addEventListener('change', () => this.validateCheckbox(input, true));
        })
        emailInputs.forEach(input => {
            input.addEventListener('blur', () => this.validateEmail(input));
            input.addEventListener('input', () => this.validateEmail(input, false));
        });

        telInputs.forEach(input => {
            input.addEventListener('blur', () => this.validatePhone(input));
            input.addEventListener('input', () => this.validatePhone(input));
        });

        passwordInputs.forEach(input => {
            input.addEventListener('blur', () => this.validatePassword(input));
            input.addEventListener('input', () => this.validatePassword(input));
        });

        textInputs.forEach(input => {
            if (input.hasAttribute('required') || input.closest('.form-group')?.querySelector('label.required')) {
                input.addEventListener('blur', () => this.validateRequired(input));
            }
        });

    }

    validateEmail(input, showNotification = true) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        const value = input.value.trim();

        if (value === '') {
            this.clearValidation(input);
            return true;
        }

        if (emailRegex.test(value)) {
            this.setValid(input);
            return true;
        } else {
            this.setError(input, this.messages.email);
            if (showNotification) this.showSticker('error', this.messages.email);
            return false;
        }
    }

    validatePhone(input, showNotification = true) {
        const phoneRegex = /^(\+7|8)\s?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/;
        const value = input.value.trim();

        if (value === '') {
            this.clearValidation(input);
            return true;
        }

        if (phoneRegex.test(value)) {
            this.setValid(input);
            return true;
        } else {
            this.setError(input, this.messages.phone);
            if (showNotification) this.showSticker('error', this.messages.phone);
            return false;
        }
    }

    validatePassword(input, showNotification = true) {
        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
        const value = input.value;

        if (value === '') {
            this.clearValidation(input);
            return true;
        }

        if (passwordRegex.test(value)) {
            this.setValid(input);
            return true;
        } else {
            this.setError(input, this.messages.password);
            if (showNotification) this.showSticker('error', this.messages.password);
            return false;
        }
    }


    validateRequired(input, showNotification = true) {
        const value = input.value.trim();

        if (value === '') {
            this.setError(input, this.messages.required);
            this.showSticker('error', this.messages.required);
            return false;
        } else {
            if (showNotification) this.setValid(input);
            return true;
        }
    }
    validateCheckbox(input, showNotification = true) {
    if (input.checked) {
        this.setValid(input);
        return true;
    } else {
        this.setError(input, this.messages.required);
        if (showNotification) this.showSticker('error', this.messages.required);
        return false;
    }
}

    setError(input, message) {
        input.classList.add('input-error');
        input.classList.remove('input-success');

        this.removeFeedback(input);

        const feedback = document.createElement('span');
        feedback.className = 'validation-feedback error';
        feedback.textContent = message;
        input.parentNode.appendChild(feedback);
    }


    setValid(input) {
        input.classList.remove('input-error');
        input.classList.add('input-success');

        this.removeFeedback(input);
    }

    clearValidation(input) {
        input.classList.remove('input-error', 'input-success');
        this.removeFeedback(input);
    }


    removeFeedback(input) {
        const existingFeedback = input.parentNode.querySelector('.validation-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
    }


    showSticker(type, message, duration = 5000) {
        const sticker = document.createElement('div');
        sticker.className = `sticker sticker-${type}`;

        const icons = {
            error: '❌',
            success: '✅',
            warning: '⚠️'
        };

        sticker.innerHTML = `
            <span class="sticker-icon">${icons[type] || 'ℹ️'}</span>
            <span class="sticker-message">${message}</span>
            <button class="sticker-close" aria-label="Закрыть">&times;</button>
        `;

        this.stickerContainer.appendChild(sticker);

        setTimeout(() => sticker.classList.add('show'), 10);


        const closeBtn = sticker.querySelector('.sticker-close');
        closeBtn.addEventListener('click', () => this.hideSticker(sticker));


        if (duration > 0) {
            setTimeout(() => this.hideSticker(sticker), duration);
        }

        return sticker;
    }


    hideSticker(sticker) {
        sticker.classList.add('hiding');
        setTimeout(() => {
            sticker.remove();
        }, 300);
    }
}

export default FormValidator;

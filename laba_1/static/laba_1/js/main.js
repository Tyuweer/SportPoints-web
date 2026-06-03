import ScrollToTopButton from './scroll_top.js';
import TelegramModal from './modal.js';
import FormValidator from './form_validator.js';
import AjaxHandler from './ajax_handler.js';
import ExcelHandler from './excel_handler.js';
import AthleteListHandler from './athlete_list_handler.js';

document.addEventListener('DOMContentLoaded', () => {
    const scrollButton = new ScrollToTopButton({
        scrollThreshold: 400
    });


    // const telegramModal = new TelegramModal({
    //     telegramUrl: 'https://t.me/finswimmingnews',
    //     showDelay: 2000
    // });

    const formValidator = new FormValidator({
        messages: {
            email: 'Введите корректный email адрес (например: example@mail.ru)',
            phone: 'Введите корректный номер телефона в формате +7 (XXX) XXX-XX-XX',
            password: 'Пароль должен содержать минимум 8 символов, включая буквы и цифры',
            required: 'Это поле обязательно для заполнения'
        }
    });

    const ajaxHandler = new AjaxHandler();  
    const excelHandler = new ExcelHandler(ajaxHandler);

    const athleteTable = document.querySelector('.table');
    if (athleteTable) {
        const athleteListHandler = new AthleteListHandler(ajaxHandler);
        athleteListHandler.init();
    }

    const exportBtn = document.getElementById('export-excel-btn');
    if (exportBtn) {
        exportBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const result = await excelHandler.exportAthletesToExcel();
        });
    }
});

export {
    ScrollToTopButton,
    // TelegramModal,
    FormValidator,
    AjaxHandler,
    ExcelHandler,
    AthleteListHandler,
};
class ExcelHandler {
    constructor(ajaxHandler) {
        this.ajaxHandler = ajaxHandler;
        this.urls = {
            export: '/export-excel/',
        };
    }

    async exportAthletesToExcel() {
        try {
            const response = await this.ajaxHandler.get(this.urls.export);

            if (response.success) {
                const link = document.createElement('a');
                link.href = response.file_url;
                link.download = response.filename || 'athletes.xlsx';
                document.body.appendChild(link);
                link.click();

                this.showNotification('success', response.message);
            } 
            else {
                this.showNotification('error', response.message);
            }
        } catch (error) {
            console.error('Ошибка экспорта Excel:', error);
            this.showNotification('error', 'Ошибка при экспорте файла');
        }
    }


        showNotification(type, message) {
        const existing = document.querySelector('.ajax-notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.className = `ajax-notification ajax-notification-${type}`;
        notification.innerHTML = `
            <span class="notification-icon">${type === 'success' ? ':-)' : ':-('}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close">&times;</button>
        `;
        document.body.appendChild(notification);

        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });

        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }
}

export default ExcelHandler;
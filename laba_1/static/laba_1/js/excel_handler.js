class ExcelHandler {
    constructor(ajaxHandler) {
        this.ajaxHandler = ajaxHandler;
        this.urls = {
            export: '/export-excel/',
        };
    }

    async exportAthletesToExcel() {
        try {
            // Показываем индикатор загрузки
            this.showLoading();
            
            const response = await this.ajaxHandler.get(this.urls.export);

            if (response.success && response.file_url) {
                // Создаем ссылку для скачивания
                const link = document.createElement('a');
                link.href = response.file_url;
                link.download = response.filename || 'athletes_export.xlsx';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                this.showNotification('success', response.message || 'Экспорт успешно выполнен!');
            } else {
                this.showNotification('error', response.message || 'Ошибка при экспорте');
            }
        } catch (error) {
            console.error('Ошибка экспорта Excel:', error);
            this.showNotification('error', 'Ошибка при экспорте файла');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        const btn = document.getElementById('export-excel-btn');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Экспорт...';
        }
    }

    hideLoading() {
        const btn = document.getElementById('export-excel-btn');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-download"></i> Экспорт в Excel';
        }
    }

    showNotification(type, message) {
        const existing = document.querySelector('.ajax-notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.className = `ajax-notification ajax-notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background: ${type === 'success' ? '#28a745' : '#dc3545'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            font-size: 14px;
        `;
        
        notification.innerHTML = `
            <span>${type === 'success' ? '✓' : '✗'}</span>
            <span>${message}</span>
            <button style="background: none; border: none; color: white; cursor: pointer; font-size: 18px;">&times;</button>
        `;
        
        document.body.appendChild(notification);

        notification.querySelector('button').addEventListener('click', () => {
            notification.remove();
        });

        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
              }
          }, 3000);
    }
}

export default ExcelHandler;
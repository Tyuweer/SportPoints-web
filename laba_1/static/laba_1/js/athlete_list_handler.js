class AthleteListHandler {
    constructor(ajaxHandler) {
        this.ajaxHandler = ajaxHandler;
        this.urls = {
            delete: '/athletes/delete-ajax/',
            list: ''
        };
        this.tableBody = null;
    }

    init() {
        this.tableBody = document.querySelector('.table tbody');
        console.log('Table body found:', this.tableBody);
        this.bindEvents();
    }

    bindEvents() {
        if (this.tableBody) {
            this.tableBody.addEventListener('click', (e) => {
                // ИСПРАВЛЕНО: один класс, не три
                const deleteBtn = e.target.closest('.btn-danger');
                console.log('Click on element:', e.target);
                console.log('Delete button found:', deleteBtn);
                
                if (deleteBtn && deleteBtn.getAttribute('data-id')) {
                    console.log('Deleting athlete ID:', deleteBtn.dataset.id);
                    e.preventDefault();
                    const athleteId = deleteBtn.dataset.id;
                    const row = deleteBtn.closest('tr');
                    this.deleteAthlete(athleteId, row);
                }
            });
        } else {
            console.log('Table body NOT found');
        }
    }

    async deleteAthlete(athleteId, row) {
        console.log('deleteAthlete called with ID:', athleteId);
        
        if (!confirm('Вы уверены, что хотите удалить этого спортсмена?')) {
            return;
        }

        try {
            const url = `${this.urls.delete}${athleteId}/`;
            console.log('POST to URL:', url);
            
            const response = await this.ajaxHandler.post(url, {});
            console.log('Response:', response);

            if (response.success) {
                if (row) {
                    row.remove();
                }
                this.showNotification('success', response.message);
                this.updateRowNumbers();
            } else {
                this.showNotification('error', response.message || 'Ошибка при удалении');
            }
        } catch (error) {
            console.error('Ошибка удаления спортсмена:', error);
            this.showNotification('error', 'Ошибка при удалении спортсмена');
        }
    }

    updateRowNumbers() {
        if (!this.tableBody) return;
        
        const rows = this.tableBody.querySelectorAll('tr');
        rows.forEach((row, index) => {
            const firstCell = row.querySelector('td:first-child');
            if (firstCell) {
                firstCell.textContent = index + 1;
            }
        });
    }

showNotification(type, message) {
    const existing = document.querySelector('.ajax-notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = 'ajax-notification';
    
    const text = message || (type === 'success' ? 'Спортсмен успешно удален!' : 'Ошибка при удалении');
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 16px;">${type === 'success' ? '✅' : '❌'}</span>
            <span style="flex: 1; font-size: 13px;">${text}</span>
            <button style="background: none; border: none; color: white; cursor: pointer; font-size: 16px;">&times;</button>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'success' ? '#2ecc71' : '#e74c3c'};
        color: white;
        padding: 10px 16px;
        border-radius: 6px;
        font-family: system-ui, sans-serif;
        font-size: 13px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        z-index: 9999;
        max-width: 280px;
        width: auto;
    `;
    
    document.body.appendChild(notification);
    
    notification.querySelector('button').onclick = () => notification.remove();
    
    setTimeout(() => {
        if (notification.parentNode) notification.remove();
    }, 2500);
}
}


export default AthleteListHandler;
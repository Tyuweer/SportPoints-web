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
        this.tableBody = document.querySelector('.table table-hover mb-0');
        this.bindEvents();
    }

    bindEvents() {
        if (this.tableBody) {
            this.tableBody.addEventListener('click', (e) => {
                if (e.target.classList.contains('btn-delete-ajax')) {
                    e.preventDefault();
                    const athleteId = e.target.dataset.id;
                    const row = e.target.closest('tr');
                    this.deleteAthlete(athleteId, row);
                }
            });
        }
    }

    async loadAthletes() {
        try {
            const response = await this.ajaxHandler.get(this.urls.list);

            if (response.success && this.tableBody) {
                this.renderTable(response.athletes);
                return { success: true, count: response.count };
            } 
            else {
                return { success: false, message: response.message || 'Ошибка загрузки данных' };
            }
        } catch (error) {
            console.error('Ошибка загрузки списка спортсменов:', error);
            return { success: false, message: 'Ошибка при загрузке данных' };
        }
    }

    renderTable(athletes) {
        if (!this.tableBody) return;

        this.tableBody.innerHTML = '';

        if (athletes.length === 0) {
            this.tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="no-data">Список спортсменов пуст.</td>
                </tr>
            `;
            return;
        }

        athletes.forEach(athlete => {
            const row = document.createElement('tr');
            row.dataset.id = athlete.id;
            row.innerHTML = `
                <td>${athlete.row_number}</td>
                <td>${athlete.full_name}</td>
                <td>${athlete.birth_year}</td>
                <td>${athlete.team}</td>
                <td class="actions">
                    <a href="${athlete.detail_url}" class="btn-detail">Подробнее</a>
                    <a href="/athletes/edit/${athlete.id}/" class="btn-edit">Изменить</a>
                    <button type="button" class="btn-delete-ajax" data-id="${athlete.id}">Удалить</button>
                </td>
            `;
            this.tableBody.appendChild(row);
        });
    }

    async deleteAthlete(athleteId, row) {
    if (!confirm('Вы уверены, что хотите удалить этого спортсмена?')) {
        return;
    }

    try {
        const url = `${this.urls.delete}${athleteId}/`;
        const response = await this.ajaxHandler.post(url, {});

        if (response.success) {

            await this.loadAthletes();
            this.showNotification('success', response.message);
        } else {
            this.showNotification('error', response.message || 'Ошибка при удалении');
        }
    } catch (error) {
        console.error('Ошибка удаления спортсмена:', error);
        this.showNotification('error', 'Ошибка при удалении спортсмена');
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

export default AthleteListHandler;
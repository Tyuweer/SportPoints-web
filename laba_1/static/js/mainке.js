/**
 * AJAX фильтрация и поиск спортсменов
 */

document.addEventListener('DOMContentLoaded', function() {
    // Получаем форму поиска
    const filterForm = document.getElementById('filter-form');
    const searchInput = document.querySelector('input[name="q"]');
    const teamSelect = document.querySelector('select[name="team"]');
    
    if (!filterForm) return;
    
    // Debounce функция для живого поиска
    let debounceTimer;
    const debounce = (func, delay) => {
        return function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                func.apply(this, arguments);
            }, delay);
        };
    };
    
    // Live search функция
    const performSearch = debounce(function() {
        const query = searchInput.value;
        const team = teamSelect ? teamSelect.value : '';
        
        if (query.length >= 2 || team) {
            // Отправляем AJAX запрос
            fetch(`?q=${encodeURIComponent(query)}&team=${encodeURIComponent(team)}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.text())
            .then(html => {
                // Обновляем таблицу результатов
                const tableContainer = document.querySelector('.table-responsive');
                if (tableContainer) {
                    const parser = new DOMParser();
                    const newDoc = parser.parseFromString(html, 'text/html');
                    const newTable = newDoc.querySelector('.table-responsive');
                    if (newTable) {
                        tableContainer.outerHTML = newTable.outerHTML;
                    }
                }
            })
            .catch(error => console.error('Search error:', error));
        }
    }, 500);
    
    // Слушаем изменения в поле поиска
    if (searchInput) {
        searchInput.addEventListener('input', performSearch);
    }
    
    // Слушаем изменения в выборе команды
    if (teamSelect) {
        teamSelect.addEventListener('change', performSearch);
    }
    
    // Фильтрация по фильтрам (соревнования, статусу и т.д.)
    const statusFilter = document.querySelector('select[name="status"]');
    const typeFilter = document.querySelector('select[name="type"]');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            filterForm.submit();
        });
    }
    
    if (typeFilter) {
        typeFilter.addEventListener('change', function() {
            filterForm.submit();
        });
    }
});



/**
 * Форматирование таблицы для мобильных устройств
 */
function makeTableResponsive() {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        // Добавляем горизонтальный скролл на мобильных
        if (window.innerWidth < 768) {
            table.parentElement.style.overflowX = 'auto';
        }
    });
}

window.addEventListener('resize', makeTableResponsive);
makeTableResponsive();

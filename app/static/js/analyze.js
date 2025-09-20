function toggleYear(btn) {
    btn.classList.toggle('selected');
}

function toggleMonth(btn) {
    btn.classList.toggle('selected');
}

// Добавляем обработчик формы
document.getElementById('analysis-form').addEventListener('submit', function(e) {
    // Удалить ВСЕ старые скрытые поля с этими именами
    const oldYearInputs = this.querySelectorAll('input[name="selected_years"]');
    const oldMonthInputs = this.querySelectorAll('input[name="selected_months"]');

    oldYearInputs.forEach(input => input.remove());
    oldMonthInputs.forEach(input => input.remove());

    const selectedYears = Array.from(document.querySelectorAll('.btn-year.selected'))
        .map(btn => btn.dataset.year);
    const selectedMonths = Array.from(document.querySelectorAll('.btn-month.selected'))
        .map(btn => btn.dataset.month);

    // Сохраняем выбранные значения в скрытые поля формы
    const hiddenYears = document.createElement('input');
    hiddenYears.type = 'hidden';
    hiddenYears.name = 'selected_years';
    hiddenYears.value = JSON.stringify(selectedYears);
    this.appendChild(hiddenYears);

    const hiddenMonths = document.createElement('input');
    hiddenMonths.type = 'hidden';
    hiddenMonths.name = 'selected_months';
    hiddenMonths.value = JSON.stringify(selectedMonths);
    this.appendChild(hiddenMonths);
});


document.addEventListener('DOMContentLoaded', function() {
    const radioCategory = document.getElementById('analysis-category');
    const radioPeriod = document.getElementById('analysis-period');

    // Функция для включения/отключения кнопок
    function toggleButtons(enabled) {
        document.querySelectorAll('.btn-year, .btn-month').forEach(btn => {
            btn.disabled = !enabled; // Если enabled=true → disabled=false, и наоборот
        });
    }

    // Изначально: если выбрана "категория" — кнопки ВКЛ
    // toggleButtons(radioCategory.checked);

    // Слушаем изменения на радиокнопках
    radioCategory.addEventListener('change', function() {
        if (this.checked) {
            toggleButtons(false);  // Включить кнопки
        }
    });

    radioPeriod.addEventListener('change', function() {
        if (this.checked) {
            toggleButtons(true); // Отключить кнопки
        }
    });
});
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QDateTimeEdit, QTextEdit, QPushButton, QHBoxLayout, QMessageBox, QDoubleSpinBox, QCheckBox, QGroupBox, QTabWidget, QWidget
from PyQt5.QtCore import QDateTime
from PyQt5 import uic
import os
from alg.alg_zone import create_search_area
from alg.alg_calculations import calculate_probability_area, calculate_drift
from qgis.core import QgsProject
class SearchParamsDialog(QDialog):
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.setWindowTitle("Параметры района поиска")
        self.setMinimumSize(800, 600)
        ui_path = os.path.join(os.path.dirname(__file__), 'dialog_search_params.ui')
        if os.path.exists(ui_path):
            uic.loadUi(ui_path, self)
        else:
            self.setup_ui()
        self.connect_buttons()
        self.load_saved_data()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Создание вкладок
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        # Вкладка "Основные параметры"
        self.setup_main_tab()
        # Вкладка "Дрейф и течение"
        self.setup_drift_tab()
        # Вкладка "Расчеты"
        self.setup_calculations_tab()
        # Кнопки
        self.setup_buttons(layout)
    def setup_main_tab(self):
        """Настройка вкладки основных параметров"""
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        # Группа "Идентификация района"
        group_id = QGroupBox("Идентификация района")
        id_layout = QVBoxLayout(group_id)
        lbl_district = QLabel("Номер района поиска:")
        self.txt_district = QLineEdit("1")
        id_layout.addWidget(lbl_district)
        id_layout.addWidget(self.txt_district)
        lbl_prefix = QLabel("Префикс подрайонов:")
        self.txt_prefix = QLineEdit("A")
        id_layout.addWidget(lbl_prefix)
        id_layout.addWidget(self.txt_prefix)
        layout.addWidget(group_id)
        # Группа "Технические параметры"
        group_tech = QGroupBox("Технические параметры")
        tech_layout = QVBoxLayout(group_tech)
        lbl_sru = QLabel("Средство определения местоположения SRU:")
        self.cmb_sru = QComboBox()
        self.cmb_sru.addItems(["GNSS", "Радар", "Визуально", "ADF", "Другое"])
        tech_layout.addWidget(lbl_sru)
        tech_layout.addWidget(self.cmb_sru)
        lbl_accuracy = QLabel("Точность определения (морские мили):")
        self.spin_accuracy = QDoubleSpinBox(minimum=0.1, maximum=50.0, value=1.0)
        tech_layout.addWidget(lbl_accuracy)
        tech_layout.addWidget(self.spin_accuracy)
        layout.addWidget(group_tech)
        # Группа "Временные параметры"
        group_time = QGroupBox("Временные параметры")
        time_layout = QVBoxLayout(group_time)
        lbl_start_time = QLabel("Дата и время начала операции (UTC):")
        self.datetime_start = QDateTimeEdit()
        self.datetime_start.setDateTime(QDateTime.currentDateTime())
        self.datetime_start.setDisplayFormat("dd.MM.yyyy hh:mm")
        time_layout.addWidget(lbl_start_time)
        time_layout.addWidget(self.datetime_start)
        lbl_incident_time = QLabel("Время аварии (UTC):")
        self.datetime_incident = QDateTimeEdit()
        self.datetime_incident.setDateTime(QDateTime.currentDateTime().addSecs(-3600))
        self.datetime_incident.setDisplayFormat("dd.MM.yyyy hh:mm")
        time_layout.addWidget(lbl_incident_time)
        time_layout.addWidget(self.datetime_incident)
        lbl_duration = QLabel("Планируемая продолжительность поиска:")
        duration_layout = QHBoxLayout()
        self.spin_duration_hours = QSpinBox(minimum=1, maximum=72, value=10)
        self.spin_duration_min = QSpinBox(minimum=0, maximum=59, value=0)
        duration_layout.addWidget(self.spin_duration_hours)
        duration_layout.addWidget(QLabel("час"))
        duration_layout.addWidget(self.spin_duration_min)
        duration_layout.addWidget(QLabel("мин"))
        time_layout.addWidget(lbl_duration)
        time_layout.addLayout(duration_layout)
        layout.addWidget(group_time)
        self.tab_widget.addTab(main_widget, "Основные")
    def setup_drift_tab(self):
        """Настройка вкладки дрейфа и течения"""
        drift_widget = QWidget()
        layout = QVBoxLayout(drift_widget)
        # Группа "Ветровые условия"
        group_wind = QGroupBox("Ветровые условия")
        wind_layout = QVBoxLayout(group_wind)
        self.chk_use_wind = QCheckBox("Учитывать влияние ветра")
        self.chk_use_wind.setChecked(True)
        wind_layout.addWidget(self.chk_use_wind)
        wind_params_layout = QHBoxLayout()
        wind_params_layout.addWidget(QLabel("Скорость (м/с):"))
        self.spin_wind_speed = QDoubleSpinBox(minimum=0, maximum=50, value=5.0)
        wind_params_layout.addWidget(self.spin_wind_speed)
        wind_params_layout.addWidget(QLabel("Направление (°):"))
        self.spin_wind_direction = QSpinBox(minimum=0, maximum=359, value=270)
        wind_params_layout.addWidget(self.spin_wind_direction)
        wind_layout.addLayout(wind_params_layout)
        layout.addWidget(group_wind)
        # Группа "Течения"
        group_current = QGroupBox("Течения")
        current_layout = QVBoxLayout(group_current)
        self.chk_use_current = QCheckBox("Учитывать влияние течения")
        self.chk_use_current.setChecked(True)
        current_layout.addWidget(self.chk_use_current)
        current_params_layout = QHBoxLayout()
        current_params_layout.addWidget(QLabel("Скорость (узлы):"))
        self.spin_current_speed = QDoubleSpinBox(minimum=0, maximum=10, value=1.0)
        current_params_layout.addWidget(self.spin_current_speed)
        current_params_layout.addWidget(QLabel("Направление (°):"))
        self.spin_current_direction = QSpinBox(minimum=0, maximum=359, value=90)
        current_params_layout.addWidget(self.spin_current_direction)
        current_layout.addLayout(current_params_layout)
        layout.addWidget(group_current)
        # Группа "Тип объекта"
        group_object = QGroupBox("Характеристики объекта поиска")
        object_layout = QVBoxLayout(group_object)
        lbl_object_type = QLabel("Тип объекта:")
        self.cmb_object_type = QComboBox()
        self.cmb_object_type.addItems([
            "Человек в воде",
            "Спасательный плот (4 чел.)",
            "Спасательный плот (6 чел.)",
            "Спасательный плот (10 чел.)",
            "Спасательная шлюпка",
            "Малое судно",
            "Обломки (легкие)",
            "Обломки (тяжелые)"
        ])
        object_layout.addWidget(lbl_object_type)
        object_layout.addWidget(self.cmb_object_type)
        layout.addWidget(group_object)
        self.tab_widget.addTab(drift_widget, "Дрейф")
    def setup_calculations_tab(self):
        """Настройка вкладки расчетов"""
        calc_widget = QWidget()
        layout = QVBoxLayout(calc_widget)
        # Автоматические расчеты
        self.txt_error_calc = QTextEdit()
        self.txt_error_calc.setReadOnly(True)
        self.txt_error_calc.setMaximumHeight(150)
        layout.addWidget(QLabel("Расчет суммарной вероятной погрешности:"))
        layout.addWidget(self.txt_error_calc)
        # Кнопки расчета
        calc_buttons_layout = QHBoxLayout()
        self.btn_calc_drift = QPushButton("Рассчитать дрейф")
        self.btn_calc_probability = QPushButton("Рассчитать вероятность")
        self.btn_calc_area = QPushButton("Рассчитать площадь")
        calc_buttons_layout.addWidget(self.btn_calc_drift)
        calc_buttons_layout.addWidget(self.btn_calc_probability)
        calc_buttons_layout.addWidget(self.btn_calc_area)
        layout.addLayout(calc_buttons_layout)
        # Результаты расчетов
        self.txt_calc_results = QTextEdit()
        self.txt_calc_results.setReadOnly(True)
        layout.addWidget(QLabel("Результаты расчетов:"))
        layout.addWidget(self.txt_calc_results)
        self.tab_widget.addTab(calc_widget, "Расчеты")
    def setup_buttons(self, layout):
        """Настройка кнопок"""
        buttons_layout = QHBoxLayout()
        self.btn_close = QPushButton("Закрыть")
        self.btn_save = QPushButton("Сохранить")
        self.btn_build = QPushButton("Построить район")
        self.btn_preview = QPushButton("Предварительный просмотр")
        buttons_layout.addWidget(self.btn_close)
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addWidget(self.btn_preview)
        buttons_layout.addWidget(self.btn_build)
        layout.addLayout(buttons_layout)
    def connect_buttons(self):
        """Подключение обработчиков кнопок"""
        self.btn_close.clicked.connect(self.close)
        self.btn_save.clicked.connect(self.save_params)
        self.btn_build.clicked.connect(self.build_search_area)
        self.btn_preview.clicked.connect(self.preview_area)
        # Кнопки расчетов
        if hasattr(self, 'btn_calc_drift'):
            self.btn_calc_drift.clicked.connect(self.calculate_drift)
            self.btn_calc_probability.clicked.connect(self.calculate_probability)
            self.btn_calc_area.clicked.connect(self.calculate_area_size)
        # Автоматическое обновление расчетов при изменении параметров
        self.spin_wind_speed.valueChanged.connect(self.update_calculations)
        self.spin_current_speed.valueChanged.connect(self.update_calculations)
        self.datetime_start.dateTimeChanged.connect(self.update_calculations)
    def load_saved_data(self):
        """Загрузка сохраненных данных"""
        # Загрузка из настроек проекта
        project = QgsProject.instance()
        saved_district = project.readEntry("PoiskMore", "last_district", "1")[0]
        self.txt_district.setText(saved_district)
        saved_prefix = project.readEntry("PoiskMore", "last_prefix", "A")[0]
        self.txt_prefix.setText(saved_prefix)
    def update_calculations(self):
        """Автоматическое обновление расчетов"""
        try:
            self.calculate_error_summary()
        except Exception as e:
            self.txt_error_calc.setText(f"Ошибка расчета: {str(e)}")
    def calculate_error_summary(self):
        """Расчет суммарной погрешности"""
        # Базовая погрешность определения местоположения
        base_error = self.spin_accuracy.value()
        # Временная погрешность (увеличение с течением времени)
        time_elapsed = self.datetime_start.dateTime().secsTo(self.datetime_incident.dateTime()) / 3600.0
        time_error = abs(time_elapsed) * 0.5  # 0.5 морских миль за час
        # Погрешность от ветра и течения
        wind_error = 0
        current_error = 0
        if hasattr(self, 'chk_use_wind') and self.chk_use_wind.isChecked():
            wind_error = self.spin_wind_speed.value() * 0.1
        if hasattr(self, 'chk_use_current') and self.chk_use_current.isChecked():
            current_error = self.spin_current_speed.value() * 0.2
        # Суммарная погрешность
        total_error = math.sqrt(base_error**2 + time_error**2 + wind_error**2 + current_error**2)
        error_text = f"""Расчет суммарной вероятной погрешности:
Базовая погрешность SRU: {base_error:.2f} морских миль
Временная погрешность: {time_error:.2f} морских миль
Погрешность от ветра: {wind_error:.2f} морских миль
Погрешность от течения: {current_error:.2f} морских миль
СУММАРНАЯ ПОГРЕШНОСТЬ: {total_error:.2f} морских миль
Время с момента аварии: {abs(time_elapsed):.1f} часов
Рекомендуемый радиус поиска: {total_error * 2:.2f} морских миль"""
        if hasattr(self, 'txt_error_calc'):
            self.txt_error_calc.setText(error_text)
    def calculate_drift(self):
        """Расчет дрейфа объекта"""
        if not hasattr(self, 'txt_calc_results'):
            return
        try:
            # Получение параметров
            time_hours = abs(self.datetime_start.dateTime().secsTo(self.datetime_incident.dateTime()) / 3600.0)
            wind_data = {
                'speed': self.spin_wind_speed.value() * 1.944,  # Перевод м/с в узлы
                'direction': self.spin_wind_direction.value()
            }
            current_data = {
                'speed': self.spin_current_speed.value(),
                'direction': self.spin_current_direction.value()
            }
            # Начальная точка (условная)
            start_point = QgsPointXY(34.0, 33.0)
            # Расчет дрейфа
            drift_result = calculate_drift(start_point, wind_data, current_data, time_hours)
            result_text = f"""Результаты расчета дрейфа:
Время дрейфа: {time_hours:.1f} часов
Общее расстояние дрейфа: {drift_result['total_distance']:.2f} морских миль
Направление дрейфа: {drift_result['total_bearing']:.0f}°
Компоненты дрейфа:
- От ветра: {drift_result['wind_component']:.2f} морских миль
- От течения: {drift_result['current_component']:.2f} морских миль
Конечная позиция:
- Широта: {drift_result['end_point'].y():.4f}°
- Долгота: {drift_result['end_point'].x():.4f}°"""
            self.txt_calc_results.setText(result_text)
        except Exception as e:
            self.txt_calc_results.setText(f"Ошибка расчета дрейфа: {str(e)}")
    def calculate_probability(self):
        """Расчет области вероятности"""
        if not hasattr(self, 'txt_calc_results'):
            return
        try:
            center_point = QgsPointXY(34.0, 33.0)
            error_radius = self.spin_accuracy.value()
            prob_95 = calculate_probability_area(center_point, error_radius, 0.95)
            prob_50 = calculate_probability_area(center_point, error_radius, 0.50)
            result_text = f"""Расчет областей вероятности:
95% вероятность:
- Радиус: {prob_95['radius_nm']:.2f} морских миль
- Площадь: {prob_95['area_nm2']:.1f} кв. морских миль
50% вероятность:
- Радиус: {prob_50['radius_nm']:.2f} морских миль
- Площадь: {prob_50['area_nm2']:.1f} кв. морских миль
Рекомендации:
- Начинать поиск с области 50% вероятности
- Расширить до области 95% при необходимости"""
            current_text = self.txt_calc_results.toPlainText()
            if current_text:
                self.txt_calc_results.setText(current_text + "\n\n" + result_text)
            else:
                self.txt_calc_results.setText(result_text)
        except Exception as e:
            self.txt_calc_results.append(f"Ошибка расчета вероятности: {str(e)}")
    def calculate_area_size(self):
        """Расчет размера района поиска"""
        if not hasattr(self, 'txt_calc_results'):
            return
        try:
            # Упрощенный расчет размера района
            base_radius = self.spin_accuracy.value() * 2
            area_km2 = 3.14159 * (base_radius * 1.852)**2  # Перевод морских миль в км
            result_text = f"""Расчет размера района поиска:
Базовый радиус: {base_radius:.2f} морских миль
Площадь района: {area_km2:.1f} кв. км
Рекомендуемое время поиска: {self.spin_duration_hours.value()} часов
Оптимизация:
- Для быстрого поиска: уменьшить на 25%
- Для тщательного поиска: увеличить на 50%"""
            current_text = self.txt_calc_results.toPlainText()
            if current_text:
                self.txt_calc_results.setText(current_text + "\n\n" + result_text)
            else:
                self.txt_calc_results.setText(result_text)
        except Exception as e:
            self.txt_calc_results.append(f"Ошибка расчета площади: {str(e)}")
    def save_params(self):
        """Сохранение параметров"""
        params = self.get_params()
        # Сохранение в настройки проекта
        project = QgsProject.instance()
        project.writeEntry("PoiskMore", "last_district", params['district'])
        project.writeEntry("PoiskMore", "last_prefix", params['prefix'])
        project.writeEntry("PoiskMore", "search_params", str(params))
        QMessageBox.information(self, "Сохранено", "Параметры поиска сохранены в проект")
    def preview_area(self):
        """Предварительный просмотр района"""
        try:
            params = self.get_params()
            # Создание временного слоя для предварительного просмотра
            preview_layer = create_search_area(params, mode='preview')
            preview_layer.setName("Предварительный просмотр района")
            QgsProject.instance().addMapLayer(preview_layer)
            QMessageBox.information(self, "Предварительный просмотр",
                "Район добавлен как предварительный просмотр. Нажмите 'Построить район' для создания финального варианта.")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка создания предварительного просмотра: {str(e)}")
    def build_search_area(self):
        """Построение района поиска"""
        try:
            params = self.get_params()
            area_layer = create_search_area(params, mode='two_points')
            QgsProject.instance().addMapLayer(area_layer)
            # Сохранение параметров
            self.save_params()
            QMessageBox.information(self, "Построено",
                f"Район поиска '{params['district']}' построен и добавлен в проект QGIS.")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка построения района: {str(e)}")
    def get_params(self):
        """Получение всех параметров из формы"""
        params = {
            'district': self.txt_district.text(),
            'prefix': self.txt_prefix.text(),
            'sru': self.cmb_sru.currentText(),
            'accuracy': self.spin_accuracy.value(),
            'start_time': self.datetime_start.dateTime(),
            'incident_time': self.datetime_incident.dateTime(),
            'duration_hours': self.spin_duration_hours.value(),
            'duration_min': self.spin_duration_min.value()
        }
        # Добавление параметров дрейфа, если вкладка создана
        if hasattr(self, 'chk_use_wind'):
            params.update({
                'use_wind': self.chk_use_wind.isChecked(),
                'wind_speed': self.spin_wind_speed.value(),
                'wind_direction': self.spin_wind_direction.value(),
                'use_current': self.chk_use_current.isChecked(),
                'current_speed': self.spin_current_speed.value(),
                'current_direction': self.spin_current_direction.value(),
                'object_type': self.cmb_object_type.currentText()
            })
        return params
Продолжить с остальными файлами?
да, также аккуратно
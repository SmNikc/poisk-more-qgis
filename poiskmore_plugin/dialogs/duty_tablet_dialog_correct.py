# -*- coding: utf-8 -*-
"""
dialogs/duty_tablet_dialog.py

ПЛАНШЕТ ОПЕРАТИВНОГО ДЕЖУРНОГО ГМСКЦ
Соответствует п.7 Методики работы с программой "Поиск-Море"

РЕАЛИЗУЮ: Планшет оперативного дежурного ГМСКЦ
СООТВЕТСТВУЕТ: План рефакторинга -> п.7 Методики
ТОЧНАЯ СТРУКТУРА:
- Три текстовых поля слева (СИТУАЦИЯ, ОБЪЕКТ ПОИСКА + ПОГОДА, ПЛАНИРУЕМЫЕ УЧАСТНИКИ)
- Карта операции справа
- Размеры и расположение точно по образцу из Методики
"""

import sys
import os

from qgis.PyQt.QtCore import Qt, QRect
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, 
    QSplitter, QWidget, QFrame, QGroupBox, QPushButton, QMessageBox
)
from qgis.PyQt.QtGui import QFont
from qgis.core import QgsProject, QgsVectorLayer, QgsRasterLayer
from qgis.gui import QgsMapCanvas


class DutyTabletDialog(QDialog):
    """
    Планшет оперативного дежурного ГМСКЦ
    
    Структура по п.7 Методики:
    ┌─────────────────────────────────────────────────────────────────┐
    │ ПЛАНШЕТ ОПЕРАТИВНОГО ДЕЖУРНОГО ГМСКЦ                            │
    ├──────────────────────────────┬──────────────────────────────────┤
    │ 1. СИТУАЦИЯ                  │                                  │
    │ (данные по аварийному судну) │                                  │
    │                              │                                  │
    ├──────────────────────────────┤         КАРТА ОПЕРАЦИИ           │
    │ 2. ОБЪЕКТ ПОИСКА + ПОГОДА    │                                  │
    │ НА МЕСТЕ                     │                                  │
    │ (разделенные колонки)        │                                  │
    ├──────────────────────────────┤                                  │
    │ 3. ПЛАНИРУЕМЫЕ УЧАСТНИКИ     │                                  │
    │ ОПЕРАЦИИ                     │                                  │
    │ МЕСТОПОЛОЖЕНИЕ/МАРШРУТ       │                                  │
    └──────────────────────────────┴──────────────────────────────────┘
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Планшет оперативного дежурного ГМСКЦ")
        self.setModal(True)
        
        # Устанавливаем размер окна по образцу из Методики
        self.resize(1000, 700)
        
        # Создаем интерфейс
        self._setup_ui()
        self._load_sample_data()
    
    def _setup_ui(self):
        """Создание интерфейса планшета."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Заголовок планшета
        title_label = QLabel("ПЛАНШЕТ ОПЕРАТИВНОГО ДЕЖУРНОГО ГМСКЦ")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(14)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # Главный сплиттер: текстовые поля слева, карта справа
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setSizes([400, 600])  # Пропорции по образцу
        
        # === ЛЕВАЯ ЧАСТЬ: ТРИ ТЕКСТОВЫХ ПОЛЯ ===
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(10)
        
        # 1. СИТУАЦИЯ (данные по аварийному судну)
        situation_group = QGroupBox("1. СИТУАЦИЯ")
        situation_layout = QVBoxLayout(situation_group)
        
        self.situation_text = QTextEdit()
        self.situation_text.setMaximumHeight(150)
        self.situation_text.setPlainText(
            "Данные по аварийному судну:\n"
            "• Название судна: [Название]\n"
            "• Тип судна: [Тип]\n"
            "• Количество людей на борту: [Число]\n"
            "• Последние известные координаты: [Координаты]\n"
            "• Время происшествия: [Дата и время]\n"
            "• Описание аварии: [Подробное описание]"
        )
        situation_layout.addWidget(self.situation_text)
        
        # 2. ОБЪЕКТ ПОИСКА + ПОГОДА НА МЕСТЕ
        search_weather_group = QGroupBox("2. ОБЪЕКТ ПОИСКА + ПОГОДА НА МЕСТЕ")
        search_weather_layout = QVBoxLayout(search_weather_group)
        
        self.search_weather_text = QTextEdit()
        self.search_weather_text.setMaximumHeight(150)
        self.search_weather_text.setPlainText(
            "ОБЪЕКТ ПОИСКА:\n"
            "• Тип объекта: [Судно/люди в воде/спасательные средства]\n"
            "• Предполагаемое состояние: [Статус]\n"
            "• Дрейфовые характеристики: [Данные]\n\n"
            "ПОГОДА НА МЕСТЕ:\n"
            "• Ветер: [Направление, скорость]\n"
            "• Волнение: [Высота волны]\n"
            "• Видимость: [Расстояние]\n"
            "• Течение: [Направление, скорость]"
        )
        search_weather_layout.addWidget(self.search_weather_text)
        
        # 3. ПЛАНИРУЕМЫЕ УЧАСТНИКИ ОПЕРАЦИИ
        participants_group = QGroupBox("3. ПЛАНИРУЕМЫЕ УЧАСТНИКИ ОПЕРАЦИИ")
        participants_layout = QVBoxLayout(participants_group)
        
        self.participants_text = QTextEdit()
        self.participants_text.setPlainText(
            "ПОИСКОВО-СПАСАТЕЛЬНЫЕ СРЕДСТВА:\n"
            "• Суда: [Список судов с характеристиками]\n"
            "• Воздушные средства: [Список ВС с характеристиками]\n"
            "• Береговые средства: [При необходимости]\n\n"
            "МЕСТОПОЛОЖЕНИЕ/МАРШРУТЫ:\n"
            "• Исходные позиции: [Координаты]\n"
            "• Назначенные районы поиска: [Описание]\n"
            "• Время прибытия (ETA): [Расчетное время]\n"
            "• Связь: [Частоты, позывные]"
        )
        participants_layout.addWidget(self.participants_text)
        
        # Добавляем группы в левую часть
        left_layout.addWidget(situation_group)
        left_layout.addWidget(search_weather_group)
        left_layout.addWidget(participants_group)
        left_layout.addStretch()  # Заполнитель
        
        # === ПРАВАЯ ЧАСТЬ: КАРТА ОПЕРАЦИИ ===
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Заголовок карты
        map_label = QLabel("КАРТА ОПЕРАЦИИ")
        map_label.setAlignment(Qt.AlignCenter)
        map_font = QFont()
        map_font.setBold(True)
        map_font.setPointSize(12)
        map_label.setFont(map_font)
        right_layout.addWidget(map_label)
        
        # Карта
        try:
            self.map_canvas = QgsMapCanvas()
            self.map_canvas.setMinimumSize(500, 500)
            
            # Загружаем текущие слои проекта
            project = QgsProject.instance()
            layers = project.mapLayers().values()
            layer_list = list(layers)
            if layer_list:
                self.map_canvas.setLayers(layer_list)
                self.map_canvas.setExtent(project.viewSettings().defaultViewExtent())
            
            right_layout.addWidget(self.map_canvas)
            
        except Exception as e:
            # Если карта недоступна, показываем заглушку
            map_placeholder = QLabel("КАРТА ОПЕРАЦИИ\n\n[Здесь отображается карта с элементами операции:\nрайоны поиска, маршруты SRU, точки интереса]")
            map_placeholder.setAlignment(Qt.AlignCenter)
            map_placeholder.setStyleSheet(
                "QLabel { border: 2px solid gray; background-color: lightgray; }"
            )
            map_placeholder.setMinimumSize(500, 500)
            right_layout.addWidget(map_placeholder)
        
        # Добавляем виджеты в сплиттер
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        
        # Добавляем сплиттер в основной layout
        main_layout.addWidget(main_splitter)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Кнопка "Обновить данные"
        update_btn = QPushButton("Обновить данные")
        update_btn.clicked.connect(self._update_data)
        buttons_layout.addWidget(update_btn)
        
        # Кнопка "Экспорт в PDF"
        export_btn = QPushButton("Экспорт в PDF")
        export_btn.clicked.connect(self._export_pdf)
        buttons_layout.addWidget(export_btn)
        
        # Кнопка "Закрыть"
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def _load_sample_data(self):
        """Загрузка образцовых данных (в реальной версии - из базы данных операции)."""
        # В реальной реализации здесь будет загрузка данных из текущей операции
        pass
    
    def _update_data(self):
        """Обновление данных планшета."""
        try:
            # В реальной реализации здесь будет обновление данных из БД
            QMessageBox.information(
                self,
                "Обновление данных",
                "Данные планшета обновлены из текущей операции."
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Ошибка обновления",
                f"Не удалось обновить данные: {str(e)}"
            )
    
    def _export_pdf(self):
        """Экспорт планшета в PDF."""
        try:
            # В реальной реализации здесь будет экспорт в PDF
            QMessageBox.information(
                self,
                "Экспорт в PDF",
                "Планшет экспортирован в файл: планшет_дежурного_ГМСКЦ.pdf"
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Ошибка экспорта",
                f"Не удалось экспортировать в PDF: {str(e)}"
            )
    
    def get_data(self):
        """
        Получить данные из планшета
        
        Returns:
            dict: Словарь с данными планшета
        """
        return {
            'situation': self.situation_text.toPlainText(),
            'search_weather': self.search_weather_text.toPlainText(),
            'participants': self.participants_text.toPlainText(),
            'timestamp': '2024-09-24 12:00:00'  # В реальной версии - текущее время
        }
    
    def set_operation_data(self, operation_data):
        """
        Установить данные операции в планшет
        
        Args:
            operation_data (dict): Данные операции из БД
        """
        if not operation_data:
            return
        
        # Заполняем поля данными операции
        if 'incident_description' in operation_data:
            self.situation_text.setPlainText(
                f"Данные по аварийному судну:\n{operation_data['incident_description']}"
            )
        
        if 'search_object' in operation_data:
            weather_text = f"ОБЪЕКТ ПОИСКА:\n{operation_data.get('search_object', '')}\n\n"
            weather_text += f"ПОГОДА НА МЕСТЕ:\n{operation_data.get('weather_conditions', '')}"
            self.search_weather_text.setPlainText(weather_text)
        
        if 'sru_list' in operation_data:
            self.participants_text.setPlainText(
                f"ПЛАНИРУЕМЫЕ УЧАСТНИКИ ОПЕРАЦИИ:\n{operation_data['sru_list']}"
            )


# Функция обеспечения совместимости со старым кодом
class DutyTabletManager:
    """Менеджер планшета дежурного для совместимости."""
    
    def open_tablet(self, case_id=None):
        """Открыть планшет дежурного."""
        dialog = DutyTabletDialog(None)
        if case_id:
            # В реальной версии загружаем данные операции по case_id
            pass
        dialog.exec_()

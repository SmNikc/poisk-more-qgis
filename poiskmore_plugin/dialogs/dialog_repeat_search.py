# -*- coding: utf-8 -*-
"""
Диалог повторного поиска для плагина ПОИСК-МОРЕ
Полная версия с интеграцией с БД
"""

import sqlite3
from PyQt5.QtWidgets import (
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
    QGroupBox,
    QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QDateTime
from PyQt5.QtGui import QColor

class DialogRepeatSearch(QDialog):
    """Диалог для выбора операции для повторного поиска"""
    
    # Сигнал для передачи выбранной операции
    operation_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Повторный поиск")
        self.setMinimumWidth(900)
        self.setMinimumHeight(500)
        
        self.selected_operation = None
        
        # Создание интерфейса
        self.setup_ui()
        
        # Загрузка операций
        self.load_operations()
    
    def setup_ui(self):
        """Создание интерфейса"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        lbl_title = QLabel("Выберите операцию для возобновления поиска:")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        # Фильтр (только закрытые и приостановленные)
        filter_layout = QHBoxLayout()
        lbl_filter = QLabel("Показать:")
        filter_layout.addWidget(lbl_filter)
        
        self.btn_show_closed = QPushButton("Закрытые")
        self.btn_show_closed.setCheckable(True)
        self.btn_show_closed.setChecked(True)
        self.btn_show_closed.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.btn_show_closed)
        
        self.btn_show_suspended = QPushButton("Приостановленные")
        self.btn_show_suspended.setCheckable(True)
        self.btn_show_suspended.setChecked(True)
        self.btn_show_suspended.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.btn_show_suspended)
        
        self.btn_show_active = QPushButton("Активные")
        self.btn_show_active.setCheckable(True)
        self.btn_show_active.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.btn_show_active)
        
        filter_layout.addStretch()
        
        self.lbl_count = QLabel("Найдено операций: 0")
        filter_layout.addWidget(self.lbl_count)
        
        layout.addLayout(filter_layout)
        
        # Таблица операций
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "№ дела",
            "Дата начала",
            "Дата закрытия",
            "Объект",
            "Тип ситуации",
            "Координаты",
            "Людей спасено",
            "Статус",
            "Причина закрытия"
        ])
        
        # Настройка таблицы
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.doubleClicked.connect(self.select)
        
        layout.addWidget(self.table)
        
        # Панель с деталями операции
        self.details_group = QGroupBox("Детали операции")
        details_layout = QVBoxLayout()
        
        self.txt_details = QTextEdit()
        self.txt_details.setReadOnly(True)
        self.txt_details.setMaximumHeight(100)
        details_layout.addWidget(self.txt_details)
        
        self.details_group.setLayout(details_layout)
        layout.addWidget(self.details_group)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.btn_select = QPushButton("Возобновить поиск")
        self.btn_select.clicked.connect(self.select)
        self.btn_select.setEnabled(False)
        self.btn_select.setStyleSheet("""
            QPushButton:enabled {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
        """)
        btn_layout.addWidget(self.btn_select)
        
        self.btn_view = QPushButton("Просмотреть детали")
        self.btn_view.clicked.connect(self.view_details)
        self.btn_view.setEnabled(False)
        btn_layout.addWidget(self.btn_view)
        
        btn_layout.addStretch()
        
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.load_operations)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def load_operations(self):
        """Загрузка операций из БД"""
        try:
            conn = sqlite3.connect('incidents.db')
            cursor = conn.cursor()
            
            # Загружаем все операции
            cursor.execute('''
                SELECT case_number, datetime, name, situation_type,
                       coords_lat, coords_lon, num_people, status,
                       description, help_needed, mskc
                FROM incidents
                ORDER BY datetime DESC
            ''')
            
            self.all_operations = []
            rows = cursor.fetchall()
            
            for row in rows:
                operation = {
                    'case_number': row[0] or 'N/A',
                    'datetime_start': row[1] or '',
                    'datetime_end': '',  # Нужно добавить в БД
                    'name': row[2] or '',
                    'situation_type': row[3] or '',
                    'coords_lat': row[4] or 0,
                    'coords_lon': row[5] or 0,
                    'num_people': row[6] or 0,
                    'status': row[7] or 'active',
                    'description': row[8] or '',
                    'help_needed': row[9] or '',
                    'mskc': row[10] or '',
                    'close_reason': ''  # Нужно добавить в БД
                }
                self.all_operations.append(operation)
            
            conn.close()
            
            # Применяем фильтр
            self.apply_filter()
            
        except sqlite3.Error as e:
            QMessageBox.warning(
                self,
                "Ошибка БД",
                f"Не удалось загрузить операции:\n{str(e)}"
            )
    
    def apply_filter(self):
        """Применить фильтр к списку операций"""
        filtered = []
        
        for op in self.all_operations:
            status = op['status']
            
            if status == 'closed' and self.btn_show_closed.isChecked():
                filtered.append(op)
            elif status == 'suspended' and self.btn_show_suspended.isChecked():
                filtered.append(op)
            elif status == 'active' and self.btn_show_active.isChecked():
                filtered.append(op)
        
        self.populate_table(filtered)
    
    def populate_table(self, operations):
        """Заполнение таблицы"""
        self.table.setRowCount(len(operations))
        
        for i, op in enumerate(operations):
            # № дела
            item = QTableWidgetItem(op['case_number'])
            self.table.setItem(i, 0, item)
            
            # Дата начала
            item = QTableWidgetItem(op['datetime_start'])
            self.table.setItem(i, 1, item)
            
            # Дата закрытия
            item = QTableWidgetItem(op['datetime_end'])
            self.table.setItem(i, 2, item)
            
            # Объект
            item = QTableWidgetItem(op['name'])
            self.table.setItem(i, 3, item)
            
            # Тип ситуации
            item = QTableWidgetItem(op['situation_type'])
            self.table.setItem(i, 4, item)
            
            # Координаты
            lat = op['coords_lat']
            lon = op['coords_lon']
            coords = f"{lat:.4f}, {lon:.4f}"
            item = QTableWidgetItem(coords)
            self.table.setItem(i, 5, item)
            
            # Людей спасено
            item = QTableWidgetItem(str(op['num_people']))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 6, item)
            
            # Статус
            status = op['status']
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignCenter)
            
            if status == 'active':
                item.setText("Активна")
                item.setBackground(QColor(200, 255, 200))
            elif status == 'closed':
                item.setText("Закрыта")
                item.setBackground(QColor(255, 200, 200))
            elif status == 'suspended':
                item.setText("Приостановлена")
                item.setBackground(QColor(255, 255, 200))
            
            self.table.setItem(i, 7, item)
            
            # Причина закрытия
            item = QTableWidgetItem(op['close_reason'])
            self.table.setItem(i, 8, item)
            
            # Сохраняем данные операции в строке
            self.table.item(i, 0).setData(Qt.UserRole, op)
        
        # Обновляем счетчик
        self.lbl_count.setText(f"Найдено операций: {len(operations)}")
        
        # Автоподбор ширины
        self.table.resizeColumnsToContents()
    
    def on_selection_changed(self):
        """Обработчик изменения выбора"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            # Получаем данные операции
            item = self.table.item(current_row, 0)
            if item:
                operation = item.data(Qt.UserRole)
                if operation:
                    self.selected_operation = operation
                    self.show_details(operation)
                    self.btn_select.setEnabled(True)
                    self.btn_view.setEnabled(True)
                    return
        
        # Если ничего не выбрано
        self.selected_operation = None
        self.txt_details.clear()
        self.btn_select.setEnabled(False)
        self.btn_view.setEnabled(False)
    
    def show_details(self, operation):
        """Показать детали операции"""
        details = f"""Номер дела: {operation['case_number']}
Объект: {operation['name']}
Ситуация: {operation['situation_type']}
Координаты: {operation['coords_lat']:.4f}, {operation['coords_lon']:.4f}
Людей в опасности: {operation['num_people']}
Требуемая помощь: {operation['help_needed']}
МСКЦ: {operation['mskc']}
Описание: {operation['description']}"""
        
        self.txt_details.setText(details)
    
    def view_details(self):
        """Просмотреть полные детали операции"""
        if self.selected_operation:
            # Здесь можно открыть отдельное окно с полными деталями
            QMessageBox.information(
                self,
                f"Операция {self.selected_operation['case_number']}",
                f"Полная информация об операции:\n\n"
                f"Объект: {self.selected_operation['name']}\n"
                f"Тип: {self.selected_operation['situation_type']}\n"
                f"Статус: {self.selected_operation['status']}\n"
                f"Начало: {self.selected_operation['datetime_start']}\n"
                f"Координаты: {self.selected_operation['coords_lat']:.4f}, "
                f"{self.selected_operation['coords_lon']:.4f}\n\n"
                f"Описание:\n{self.selected_operation['description']}"
            )
    
    def select(self):
        """Выбрать операцию для повторного поиска"""
        if self.selected_operation:
            # Проверяем статус
            if self.selected_operation['status'] == 'active':
                reply = QMessageBox.question(
                    self,
                    "Подтверждение",
                    "Эта операция уже активна.\n"
                    "Продолжить работу с ней?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            
            # Создаем копию операции для повторного поиска
            repeat_operation = self.selected_operation.copy()
            repeat_operation['status'] = 'active'
            repeat_operation['repeat_search'] = True
            repeat_operation['original_case'] = repeat_operation['case_number']
            repeat_operation['case_number'] = f"{repeat_operation['case_number']}-R{QDateTime.currentDateTime().toString('HHmmss')}"
            repeat_operation['datetime_start'] = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
            
            # Обновляем в БД
            try:
                conn = sqlite3.connect('incidents.db')
                cursor = conn.cursor()
                
                # Обновляем статус оригинальной операции
                cursor.execute(
                    'UPDATE incidents SET status = ? WHERE case_number = ?',
                    ('repeat_search', self.selected_operation['case_number'])
                )
                
                conn.commit()
                conn.close()
                
                # Передаем операцию
                self.operation_selected.emit(repeat_operation)
                self.accept()
                
            except sqlite3.Error as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось обновить операцию:\n{str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите операцию для повторного поиска"
            )
    
    def get_data(self):
        """Получить выбранную операцию (для совместимости)"""
        return self.selected_operation
    
    def get_selected_case_id(self):
        """Получить ID выбранной операции/случая"""
        if self.selected_operation:
            return self.selected_operation.get('id', None)
        return None
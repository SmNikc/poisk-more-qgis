# -*- coding: utf-8 -*-
"""
Диалог списка операций для плагина ПОИСК-МОРЕ
Исправленная версия с полной функциональностью
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
    QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class DialogOperationList(QDialog):
    """Диалог для отображения и управления списком операций"""
    
    # Сигнал для передачи выбранной операции
    operation_selected = pyqtSignal(dict)
    
    def __init__(self, operations=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Дела и поисковые операции")
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        
        # Список операций (может быть передан извне или загружен из БД)
        self.operations = operations if operations else []
        
        # Создание интерфейса
        self.setup_ui()
        
        # Загрузка данных
        if not self.operations:
            self.load_from_database()
        else:
            self.populate_table()
    
    def setup_ui(self):
        """Создание интерфейса"""
        layout = QVBoxLayout(self)
        
        # Заголовок
        header_layout = QHBoxLayout()
        lbl_title = QLabel("Список поисково-спасательных операций:")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        
        # Счетчик операций
        self.lbl_count = QLabel("Всего операций: 0")
        header_layout.addWidget(self.lbl_count)
        layout.addLayout(header_layout)
        
        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "№ дела",
            "Дата/время",
            "Объект",
            "Тип ситуации",
            "Координаты",
            "Людей",
            "Статус",
            "МСКЦ"
        ])
        
        # Настройка таблицы
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.on_double_click)
        
        layout.addWidget(self.table)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.btn_open = QPushButton("Открыть")
        self.btn_open.clicked.connect(self.open_operation)
        btn_layout.addWidget(self.btn_open)
        
        self.btn_copy = QPushButton("Копировать")
        self.btn_copy.clicked.connect(self.copy_operation)
        btn_layout.addWidget(self.btn_copy)
        
        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.clicked.connect(self.delete_operation)
        self.btn_delete.setStyleSheet("QPushButton { color: red; }")
        btn_layout.addWidget(self.btn_delete)
        
        btn_layout.addStretch()
        
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.refresh)
        btn_layout.addWidget(self.btn_refresh)
        
        self.btn_close = QPushButton("Закрыть")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)
    
    def load_from_database(self):
        """Загрузка операций из базы данных"""
        try:
            conn = sqlite3.connect('incidents.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT case_number, datetime, name, situation_type,
                       coords_lat, coords_lon, num_people, status, mskc
                FROM incidents
                ORDER BY datetime DESC
            ''')
            
            rows = cursor.fetchall()
            self.operations = []
            
            for row in rows:
                operation = {
                    'case_number': row[0] or 'N/A',
                    'datetime': row[1] or '',
                    'name': row[2] or '',
                    'situation_type': row[3] or '',
                    'coords_lat': row[4] or 0,
                    'coords_lon': row[5] or 0,
                    'num_people': row[6] or 0,
                    'status': row[7] or 'active',
                    'mskc': row[8] or ''
                }
                self.operations.append(operation)
            
            conn.close()
            self.populate_table()
            
        except sqlite3.Error as e:
            QMessageBox.warning(
                self,
                "Ошибка БД",
                f"Не удалось загрузить операции:\n{str(e)}"
            )
    
    def populate_table(self):
        """Заполнение таблицы данными"""
        self.table.setRowCount(len(self.operations))
        
        for i, op in enumerate(self.operations):
            # № дела
            item = QTableWidgetItem(op.get('case_number', 'N/A'))
            self.table.setItem(i, 0, item)
            
            # Дата/время
            item = QTableWidgetItem(op.get('datetime', ''))
            self.table.setItem(i, 1, item)
            
            # Объект
            item = QTableWidgetItem(op.get('name', ''))
            self.table.setItem(i, 2, item)
            
            # Тип ситуации
            item = QTableWidgetItem(op.get('situation_type', ''))
            self.table.setItem(i, 3, item)
            
            # Координаты
            lat = op.get('coords_lat', 0)
            lon = op.get('coords_lon', 0)
            coords = f"{lat:.4f}, {lon:.4f}"
            item = QTableWidgetItem(coords)
            self.table.setItem(i, 4, item)
            
            # Людей
            item = QTableWidgetItem(str(op.get('num_people', 0)))
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, item)
            
            # Статус
            status = op.get('status', 'active')
            item = QTableWidgetItem(status)
            item.setTextAlignment(Qt.AlignCenter)
            
            # Цветовая индикация статуса
            if status == 'active':
                item.setBackground(QColor(200, 255, 200))
                item.setText("Активна")
            elif status == 'closed':
                item.setBackground(QColor(255, 200, 200))
                item.setText("Закрыта")
            elif status == 'suspended':
                item.setBackground(QColor(255, 255, 200))
                item.setText("Приостановлена")
            
            self.table.setItem(i, 6, item)
            
            # МСКЦ
            item = QTableWidgetItem(op.get('mskc', ''))
            self.table.setItem(i, 7, item)
        
        # Обновление счетчика
        self.lbl_count.setText(f"Всего операций: {len(self.operations)}")
        
        # Автоподбор ширины колонок
        self.table.resizeColumnsToContents()
    
    def get_selected_operation(self):
        """Получить выбранную операцию"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.operations):
            return self.operations[current_row]
        return None
    
    def on_double_click(self):
        """Обработчик двойного клика"""
        self.open_operation()
    
    def open_operation(self):
        """Открыть выбранную операцию"""
        operation = self.get_selected_operation()
        if operation:
            self.operation_selected.emit(operation)
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите операцию для открытия"
            )
    
    def copy_operation(self):
        """Копировать операцию"""
        operation = self.get_selected_operation()
        if operation:
            # Создаем копию операции с новым номером
            import copy
            from PyQt5.QtCore import QDateTime
            
            new_operation = copy.deepcopy(operation)
            new_operation['case_number'] = f"AC-COPY-{QDateTime.currentDateTime().toString('yyyyMMdd-HHmmss')}"
            new_operation['status'] = 'active'
            
            # Сохраняем в БД
            try:
                conn = sqlite3.connect('incidents.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO incidents (case_number, name, datetime, situation_type,
                                         coords_lat, coords_lon, num_people, status, mskc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    new_operation['case_number'],
                    new_operation.get('name', ''),
                    new_operation.get('datetime', ''),
                    new_operation.get('situation_type', ''),
                    new_operation.get('coords_lat', 0),
                    new_operation.get('coords_lon', 0),
                    new_operation.get('num_people', 0),
                    new_operation['status'],
                    new_operation.get('mskc', '')
                ))
                
                conn.commit()
                conn.close()
                
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Операция скопирована с номером:\n{new_operation['case_number']}"
                )
                
                # Обновляем список
                self.refresh()
                
            except sqlite3.Error as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось скопировать операцию:\n{str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите операцию для копирования"
            )
    
    def delete_operation(self):
        """Удалить операцию"""
        operation = self.get_selected_operation()
        if operation:
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Удалить операцию {operation['case_number']}?\n\n"
                "Это действие необратимо!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    conn = sqlite3.connect('incidents.db')
                    cursor = conn.cursor()
                    
                    cursor.execute(
                        'DELETE FROM incidents WHERE case_number = ?',
                        (operation['case_number'],)
                    )
                    
                    conn.commit()
                    conn.close()
                    
                    QMessageBox.information(
                        self,
                        "Успех",
                        f"Операция {operation['case_number']} удалена"
                    )
                    
                    # Обновляем список
                    self.refresh()
                    
                except sqlite3.Error as e:
                    QMessageBox.critical(
                        self,
                        "Ошибка",
                        f"Не удалось удалить операцию:\n{str(e)}"
                    )
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Выберите операцию для удаления"
            )
    
    def refresh(self):
        """Обновить список операций"""
        self.table.clearContents()
        self.load_from_database()
    
    def get_data(self):
        """Получить выбранную операцию (для совместимости)"""
        return self.get_selected_operation()
# -*- coding: utf-8 -*-
"""
Диалог авторизации системы Поиск-Море
Вариант -1: Работа с внешним REST API сервером
Соответствует OpenAPI спецификации poiskmore.geopallada.ru
"""

from PyQt5.QtWidgets import (
    QDialog, 
    QFormLayout, 
    QLineEdit, 
    QComboBox, 
    QPushButton, 
    QVBoxLayout, 
    QMessageBox,
    QLabel,
    QCheckBox,
    QProgressBar,
    QGroupBox,
    QHBoxLayout
)
from PyQt5.QtCore import QSettings, Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon
from ..utils.api_utils import get_rcc_list, login_to_sar
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any


class AuthenticationThread(QThread):
    """Поток для асинхронной авторизации"""
    
    # Сигналы
    auth_success = pyqtSignal(str, dict)  # token, user_info
    auth_failed = pyqtSignal(str)  # error message
    progress_update = pyqtSignal(str, int)  # status, progress
    
    def __init__(self, login: str, password: str, rcc_id: str, rcc_name: str):
        super().__init__()
        self.login = login
        self.password = password
        self.rcc_id = rcc_id
        self.rcc_name = rcc_name
        
    def run(self):
        """Выполнить авторизацию"""
        try:
            self.progress_update.emit("Подключение к серверу...", 30)
            
            # Вызов API функции
            token = login_to_sar(self.login, self.password, self.rcc_id)
            
            self.progress_update.emit("Получение данных профиля...", 70)
            
            # Формирование информации о пользователе
            user_info = {
                "login": self.login,
                "rcc_id": self.rcc_id,
                "rcc_name": self.rcc_name,
                "auth_time": datetime.now().isoformat(),
                "profile_type": self._determine_profile_type(self.rcc_name)
            }
            
            self.progress_update.emit("Авторизация успешна!", 100)
            self.auth_success.emit(token, user_info)
            
        except ValueError as ve:
            self.auth_failed.emit(str(ve))
        except requests.exceptions.ConnectionError:
            self.auth_failed.emit("Не удалось подключиться к серверу. Проверьте интернет-соединение.")
        except requests.exceptions.Timeout:
            self.auth_failed.emit("Превышено время ожидания ответа от сервера")
        except Exception as e:
            self.auth_failed.emit(f"Ошибка авторизации: {str(e)}")
            
    def _determine_profile_type(self, rcc_name: str) -> str:
        """Определить тип профиля по имени МСКЦ/МСПЦ"""
        if "МСКЦ" in rcc_name:
            return "МСКЦ"
        elif "МСПЦ" in rcc_name:
            return "МСПЦ"
        return "Неизвестный"


class DialogAuthorization(QDialog):
    """
    Диалог авторизации в системе Поиск-Море
    Вариант -1: Работа с внешним REST API
    """
    
    # Сигнал успешной авторизации
    authorized = pyqtSignal(str, dict)  # token, user_info
    
    def __init__(self, parent=None):
        super(DialogAuthorization, self).__init__(parent)
        self.token = None
        self.user_info = None
        self.auth_thread = None
        self.settings = QSettings("PoiskMore", "Auth")
        self._init_ui()
        self._load_saved_data()
        
    def _init_ui(self):
        """Инициализация интерфейса в соответствии с оригинальной формой"""
        self.setWindowTitle("Поиск-Море - Создание профиля")
        self.setWindowIcon(QIcon(":/plugins/poiskmore/icons/auth.png"))
        self.setModal(True)
        self.setMinimumWidth(500)
        
        # Основной layout
        main_layout = QVBoxLayout(self)
        
        # Заголовок
        header_label = QLabel("Авторизация")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Описание
        desc_label = QLabel(
            "Данная функция позволяет завести профиль, от имени которого производится работа.\n"
            "Для авторизации используются учетные данные Информационно-справочного блока."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("QLabel { color: #666; margin: 10px 0; }")
        main_layout.addWidget(desc_label)
        
        # Группа полей авторизации
        auth_group = QGroupBox("Учетные данные")
        auth_layout = QFormLayout()
        
        # Поле логина
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Введите ваш логин")
        auth_layout.addRow("Логин:", self.login_edit)
        
        # Поле пароля
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Введите ваш пароль")
        auth_layout.addRow("Пароль:", self.password_edit)
        
        # Выбор МСКЦ/МСПЦ (имя сетевого профиля)
        self.rcc_combo = QComboBox()
        self.rcc_combo.setEditable(False)
        auth_layout.addRow("Имя сетевого профиля:", self.rcc_combo)
        
        # Чекбокс запоминания
        self.remember_checkbox = QCheckBox("Запомнить логин")
        auth_layout.addRow("", self.remember_checkbox)
        
        auth_group.setLayout(auth_layout)
        main_layout.addWidget(auth_group)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Статусная строка
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("QLabel { color: #0066cc; }")
        self.status_label.setVisible(False)
        main_layout.addWidget(self.status_label)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.auth_button = QPushButton("Войти")
        self.auth_button.setIcon(QIcon(":/plugins/poiskmore/icons/login.png"))
        self.auth_button.setDefault(True)
        self.auth_button.clicked.connect(self.authenticate)
        button_layout.addWidget(self.auth_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setIcon(QIcon(":/plugins/poiskmore/icons/cancel.png"))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
        # Загрузка списка МСКЦ/МСПЦ
        self.load_rcc_list()
        
        # Горячие клавиши
        self.password_edit.returnPressed.connect(self.authenticate)
        
    def _load_saved_data(self):
        """Загрузить сохраненные данные"""
        # Загрузка сохраненного логина
        saved_login = self.settings.value("last_login", "")
        if saved_login:
            self.login_edit.setText(saved_login)
            self.remember_checkbox.setChecked(True)
            
        # Загрузка последнего выбранного МСКЦ/МСПЦ
        saved_rcc_id = self.settings.value("last_rcc_id", "")
        if saved_rcc_id:
            for i in range(self.rcc_combo.count()):
                if self.rcc_combo.itemData(i) == saved_rcc_id:
                    self.rcc_combo.setCurrentIndex(i)
                    break
                    
    def load_rcc_list(self):
        """Загрузить список МСКЦ/МСПЦ с сервера"""
        try:
            self.status_label.setText("Загрузка списка МСКЦ/МСПЦ...")
            self.status_label.setVisible(True)
            
            rcc_list = get_rcc_list()
            
            self.rcc_combo.clear()
            for rcc in rcc_list:
                self.rcc_combo.addItem(rcc['name'], rcc['id'])
                
            if rcc_list:
                self.rcc_combo.setCurrentIndex(0)
                
            self.status_label.setVisible(False)
            
        except requests.RequestException as e:
            self.status_label.setStyleSheet("QLabel { color: #cc0000; }")
            self.status_label.setText("Не удалось загрузить список МСКЦ/МСПЦ")
            QMessageBox.warning(
                self, 
                "Ошибка загрузки",
                f"Не удалось загрузить список МСКЦ/МСПЦ:\n{str(e)}\n\n"
                "Проверьте подключение к интернету и повторите попытку."
            )
            
    def authenticate(self):
        """Выполнить авторизацию"""
        # Получение данных из формы
        login = self.login_edit.text().strip()
        password = self.password_edit.text().strip()
        rcc_id = self.rcc_combo.currentData()
        rcc_name = self.rcc_combo.currentText()
        
        # Валидация
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            self.login_edit.setFocus()
            return
            
        if not password:
            QMessageBox.warning(self, "Ошибка", "Введите пароль")
            self.password_edit.setFocus()
            return
            
        if not rcc_id:
            QMessageBox.warning(self, "Ошибка", "Выберите МСКЦ/МСПЦ")
            self.rcc_combo.setFocus()
            return
            
        # Блокировка интерфейса
        self._set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        
        # Запуск потока авторизации
        self.auth_thread = AuthenticationThread(login, password, rcc_id, rcc_name)
        self.auth_thread.auth_success.connect(self._on_auth_success)
        self.auth_thread.auth_failed.connect(self._on_auth_failed)
        self.auth_thread.progress_update.connect(self._on_progress_update)
        self.auth_thread.start()
        
    def _on_progress_update(self, status: str, progress: int):
        """Обновление прогресса"""
        self.status_label.setText(status)
        self.progress_bar.setValue(progress)
        
    def _on_auth_success(self, token: str, user_info: dict):
        """Обработка успешной авторизации"""
        self.token = token
        self.user_info = user_info
        
        # Сохранение токена и информации
        self.settings.setValue("token", token)
        self.settings.setValue("user_info", json.dumps(user_info))
        
        # Сохранение логина если выбрано
        if self.remember_checkbox.isChecked():
            self.settings.setValue("last_login", self.login_edit.text())
            self.settings.setValue("last_rcc_id", self.rcc_combo.currentData())
        else:
            self.settings.remove("last_login")
            self.settings.remove("last_rcc_id")
            
        # Показ сообщения об успехе
        self.status_label.setStyleSheet("QLabel { color: #00cc00; }")
        self.status_label.setText("Авторизация успешна!")
        
        QMessageBox.information(
            self, 
            "Успех", 
            f"Авторизация успешна!\n\n"
            f"Пользователь: {user_info['login']}\n"
            f"Профиль: {user_info['rcc_name']}\n"
            f"Token сохранен в системе."
        )
        
        # Эмиссия сигнала и закрытие
        self.authorized.emit(token, user_info)
        QTimer.singleShot(500, self.accept)
        
    def _on_auth_failed(self, error_msg: str):
        """Обработка ошибки авторизации"""
        self._set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setStyleSheet("QLabel { color: #cc0000; }")
        self.status_label.setText("Ошибка авторизации")
        
        QMessageBox.critical(self, "Ошибка авторизации", error_msg)
        
    def _set_ui_enabled(self, enabled: bool):
        """Включение/отключение элементов интерфейса"""
        self.login_edit.setEnabled(enabled)
        self.password_edit.setEnabled(enabled)
        self.rcc_combo.setEnabled(enabled)
        self.remember_checkbox.setEnabled(enabled)
        self.auth_button.setEnabled(enabled)
        
    def get_token(self) -> Optional[str]:
        """Получить токен авторизации"""
        return self.token
        
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Получить информацию о пользователе"""
        return self.user_info
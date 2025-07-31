from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
from reportlab.pdfgen import canvas
import os
import json

class SitrepSendForm(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("forms/SitrepSendForm.ui", self)
        self.buttonToPdf.clicked.connect(self.generate_pdf)
        self.buttonSend.clicked.connect(self.send_sitrep)
        self.buttonCancel.clicked.connect(self.close)

    def collect_data(self):
        # Сбор данных со всех вкладок в словарь (по IAMSAR A-N)
        data = {
            "category": self.comboCategory.currentText(),
            "datetime": self.dateTimeUtc.dateTime().toString("dd MMMM yyyy г. HH:mm"),
            "from": self.editFrom.text(),
            "profile": self.comboProfile.currentText(),
            "recipients": [self.listRecipients.item(i).text() for i in range(self.listRecipients.count())],
            "notes": self.textNotes.toPlainText(),
            "object": self.editObject.text(),
            "callsign": self.editCallsign.text(),
            "location": self.editLocation.text(),
            "lat": self.spinLat.value(),
            "lat_dir": self.comboLatDir.currentText(),
            "lon": self.spinLon.value(),
            "lon_dir": self.comboLonDir.currentText(),
            "situation": self.textSituation.toPlainText(),
            "source_info": self.editSourceInfo.text(),
            "event_time": self.dateEventTime.dateTime().toString("dd MMMM yyyy г. HH:mm"),
            "persons": self.spinPersons.value(),
            "assistance": self.textAssistance.toPlainText(),
            "dim": self.editDim.text(),
            "mmsi": self.editMMSI.text(),
            "imo": self.editIMO.text(),
            "hull_color": self.comboHullColor.currentText(),
            "fuel": self.editFuel.text(),
            "cargo": self.textCargo.toPlainText(),
            "owner_name": self.editOwnerName.text(),
            "owner_phone": self.editOwnerPhone.text(),
            "owner_address": self.editOwnerAddress.text(),
            "wind_dir": self.spinWindDir.value(),
            "wind_speed": self.spinWindSpeed.value(),
            "wave_height": self.spinWaveHeight.value(),
            "wave_dir": self.spinWaveDir.value(),
            "visibility": self.spinVisibility.value(),
            "air_temp": self.spinAirTemp.value(),
            "water_temp": self.spinWaterTemp.value(),
            "weather_source": self.editWeatherSource.text(),
            "actions_j": self.textActionsJ.toPlainText(),
            "search_area_k": self.textK.toPlainText(),
            "instructions_l": self.textL.toPlainText(),
            "future_plans_m": self.textM.toPlainText(),
            "additional_n": self.textN.toPlainText()
        }
        return data

    def generate_pdf(self):
        data = self.collect_data()
        filepath = os.path.expanduser("~/Documents/SITREP.pdf")
        c = canvas.Canvas(filepath)
        y = 800
        for key, value in data.items():
            c.drawString(100, y, f"{key.capitalize()}: {value}")
            y -= 20
        c.save()
        QMessageBox.information(self, "PDF", f"PDF сохранён: {filepath}")

    def send_sitrep(self):
        data = self.collect_data()
        # Пример отправки (интегрируйте с ActiveMQ/stomp.py по CS.html)
        try:
            with open(os.path.expanduser("~/Documents/sitrep.json"), "w") as f:
                json.dump(data, f)
            QMessageBox.information(self, "Отправка", "SITREP отправлен (симуляция).")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>SitrepSendForm</class>
 <widget class="QDialog" name="SitrepSendForm">
  <property name="windowTitle"><string>Отправка SITREP</string></property>
  <layout class="QVBoxLayout" name="mainLayout">
   <item>
    <widget class="QTabWidget" name="tabWidget">
     <widget class="QWidget" name="tabHeader">
      <attribute name="title"><string>Заголовок</string></attribute>
      <layout class="QFormLayout" name="layoutHeader">
       <item row="0" column="0"><widget class="QLabel" name="labelCategory"><property name="text"><string>Категория сообщения:</string></property></widget></item>
       <item row="0" column="1"><widget class="QComboBox" name="comboCategory"><item><string>Бедствие</string></item><item><string>Тренировка</string></item></widget></item>
       <item row="1" column="0"><widget class="QLabel" name="labelDateTime"><property name="text"><string>Дата / Время (UTC) *:</string></property></widget></item>
       <item row="1" column="1"><widget class="QDateTimeEdit" name="dateTimeUtc"><property name="displayFormat"><string>dd MMMM yyyy г. HH:mm</string></property><property name="calendarPopup"><bool>true</bool></property></widget></item>
       <item row="2" column="0"><widget class="QLabel" name="labelFrom"><property name="text"><string>От кого:</string></property></widget></item>
       <item row="2" column="1"><widget class="QLineEdit" name="editFrom"/></item>
       <item row="3" column="0"><widget class="QLabel" name="labelProfile"><property name="text"><string>Профиль:</string></property></widget></item>
       <item row="3" column="1"><widget class="QComboBox" name="comboProfile"/></item>
       <item row="4" column="0" colspan="2"><widget class="QGroupBox" name="boxRecipients"><property name="title"><string>Кому:</string></property><layout class="QVBoxLayout" name="layoutRecipients"><item><widget class="QListWidget" name="listRecipients"/></item></layout></widget></item>
       <item row="5" column="0" colspan="2"><widget class="QLabel" name="labelNotes"><property name="text"><string>Дополнительно:</string></property></widget></item>
       <item row="6" column="0" colspan="2"><widget class="QTextEdit" name="textNotes"/></item>
      </layout>
     </widget>
     <widget class="QWidget" name="tabMainInfo">
      <attribute name="title"><string>Основная информация</string></attribute>
      <layout class="QFormLayout" name="layoutMain">
       <item row="0" column="0"><widget class="QLabel" name="labelObject"><property name="text"><string>Объект АС / ЧС:</string></property></widget></item>
       <item row="0" column="1"><widget class="QLineEdit" name="editObject"/></item>
       <item row="0" column="2"><widget class="QLabel" name="labelCallsign"><property name="text"><string>Позывной:</string></property></widget></item>
       <item row="0" column="3"><widget class="QLineEdit" name="editCallsign"/></item>
       <item row="1" column="0"><widget class="QLabel" name="labelLocation"><property name="text"><string>Местоположение / Район аварии:</string></property></widget></item>
       <item row="1" column="1" colspan="3"><widget class="QLineEdit" name="editLocation"/></item>
       <item row="2" column="0"><widget class="QLabel" name="labelCoords"><property name="text"><string>Координаты *:</string></property></widget></item>
       <item row="2" column="1"><widget class="QDoubleSpinBox" name="spinLat"><property name="suffix"><string> °</string></property><property name="decimals"><number>6</number></property></widget></item>
       <item row="2" column="2"><widget class="QComboBox" name="comboLatDir"><item><string>С.Ш.</string></item><item><string>Ю.Ш.</string></item></widget></item>
       <item row="2" column="3"><widget class="QDoubleSpinBox" name="spinLon"><property name="suffix"><string> °</string></property><property name="decimals"><number>6</number></property></widget></item>
       <item row="2" column="4"><widget class="QComboBox" name="comboLonDir"><item><string>В.Д.</string></item><item><string>З.Д.</string></item></widget></item>
       <item row="3" column="0"><widget class="QLabel" name="labelSituation"><property name="text"><string>Ситуация:</string></property></widget></item>
       <item row="3" column="1" colspan="4"><widget class="QTextEdit" name="textSituation"/></item>
       <item row="4" column="0"><widget class="QLabel" name="labelSourceInfo"><property name="text"><string>Источник информации:</string></property></widget></item>
       <item row="4" column="1" colspan="4"><widget class="QLineEdit" name="editSourceInfo"/></item>
       <item row="5" column="0"><widget class="QLabel" name="labelEventTime"><property name="text"><string>Время происшествия UTC:</string></property></widget></item>
       <item row="5" column="1" colspan="2"><widget class="QDateTimeEdit" name="dateEventTime"><property name="displayFormat"><string>dd MMMM yyyy г. HH:mm</string></property><property name="calendarPopup"><bool>true</bool></property></widget></item>
       <item row="6" column="0"><widget class="QLabel" name="labelPersons"><property name="text"><string>Число лиц в опасности:</string></property></widget></item>
       <item row="6" column="1"><widget class="QSpinBox" name="spinPersons"/></item>
       <item row="7" column="0"><widget class="QLabel" name="labelAssistance"><property name="text"><string>Требуемая помощь:</string></property></widget></item>
       <item row="7" column="1" colspan="4"><widget class="QTextEdit" name="textAssistance"/></item>
      </layout>
     </widget>
     <widget class="QWidget" name="tabAdditionalG">
      <attribute name="title"><string>Доп. информация (G)</string></attribute>
      <layout class="QGridLayout" name="layoutG">
       <item row="0" column="0"><widget class="QLabel" name="labelDim"><property name="text"><string>Размерение (Д×Ш×Осадка):</string></property></widget></item>
       <item row="0" column="1"><widget class="QLineEdit" name="editDim"/></item>
       <item row="1" column="0"><widget class="QLabel" name="labelMMSI"><property name="text"><string>MMSI:</string></property></widget></item>
       <item row="1" column="1"><widget class="QLineEdit" name="editMMSI"/></item>
       <!-- Другие поля G: IMO, цвет корпуса, запасы топлива, груз, контакты (владелец/оператор: ФИО, телефон, адрес) -->
       <item row="2" column="0"><widget class="QLabel" name="labelIMO"><property name="text"><string>IMO:</string></property></widget></item>
       <item row="2" column="1"><widget class="QLineEdit" name="editIMO"/></item>
       <item row="3" column="0"><widget class="QLabel" name="labelHullColor"><property name="text"><string>Цвет корпуса:</string></property></widget></item>
       <item row="3" column="1"><widget class="QComboBox" name="comboHullColor"/></item>
       <item row="4" column="0"><widget class="QLabel" name="labelFuel"><property name="text"><string>Запасы топлива:</string></property></widget></item>
       <item row="4" column="1"><widget class="QLineEdit" name="editFuel"/></item>
       <item row="5" column="0"><widget class="QLabel" name="labelCargo"><property name="text"><string>Груз:</string></property></widget></item>
       <item row="5" column="1"><widget class="QTextEdit" name="textCargo"/></item>
       <item row="6" column="0"><widget class="QLabel" name="labelOwnerName"><property name="text"><string>Владелец: ФИО</string></property></widget></item>
       <item row="6" column="1"><widget class="QLineEdit" name="editOwnerName"/></item>
       <item row="7" column="0"><widget class="QLabel" name="labelOwnerPhone"><property name="text"><string>Телефон</string></property></widget></item>
       <item row="7" column="1"><widget class="QLineEdit" name="editOwnerPhone"/></item>
       <item row="8" column="0"><widget class="QLabel" name="labelOwnerAddress"><property name="text"><string>Адрес</string></property></widget></item>
       <item row="8" column="1"><widget class="QLineEdit" name="editOwnerAddress"/></item>
      </layout>
     </widget>
     <widget class="QWidget" name="tabAdditionalHJ">
      <attribute name="title"><string>Доп. информация (H, J)</string></attribute>
      <layout class="QGridLayout" name="layoutHJ">
       <item row="0" column="0" colspan="4"><widget class="QGroupBox" name="boxWeather"><property name="title"><string>Погода на месте</string></property><layout class="QGridLayout" name="gridWeather">
        <item row="0" column="0"><widget class="QLabel" name="labelWindDir"><property name="text"><string>Ветер: Направление (градусы)</string></property></widget></item>
        <item row="0" column="1"><widget class="QSpinBox" name="spinWindDir"><property name="maximum"><number>360</number></property></widget></item>
        <item row="0" column="2"><widget class="QLabel" name="labelWindSpeed"><property name="text"><string>Скорость (м/с)</string></property></widget></item>
        <item row="0" column="3"><widget class="QDoubleSpinBox" name="spinWindSpeed"/></item>
        <item row="1" column="0"><widget class="QLabel" name="labelWaveHeight"><property name="text"><string>Волна: Высота (м)</string></property></widget></item>
        <item row="1" column="1"><widget class="QDoubleSpinBox" name="spinWaveHeight"/></item>
        <item row="1" column="2"><widget class="QLabel" name="labelWaveDir"><property name="text"><string>Направление (градусы)</string></property></widget></item>
        <item row="1" column="3"><widget class="QSpinBox" name="spinWaveDir"><property name="maximum"><number>360</number></property></widget></item>
        <item row="2" column="0"><widget class="QLabel" name="labelVisibility"><property name="text"><string>Видимость (км)</string></property></widget></item>
        <item row="2" column="1"><widget class="QDoubleSpinBox" name="spinVisibility"/></item>
        <item row="3" column="0"><widget class="QLabel" name="labelAirTemp"><property name="text"><string>Температура воздуха (°C)</string></property></widget></item>
        <item row="3" column="1"><widget class="QDoubleSpinBox" name="spinAirTemp"/></item>
        <item row="4" column="0"><widget class="QLabel" name="labelWaterTemp"><property name="text"><string>Температура воды (°C)</string></property></widget></item>
        <item row="4" column="1"><widget class="QDoubleSpinBox" name="spinWaterTemp"/></item>
        <item row="5" column="0"><widget class="QLabel" name="labelWeatherSource"><property name="text"><string>Источник погоды</string></property></widget></item>
        <item row="5" column="1" colspan="3"><widget class="QLineEdit" name="editWeatherSource"/></item>
       </layout></widget></item>
       <item row="6" column="0"><widget class="QLabel" name="labelActionsJ"><property name="text"><string>Начальные предпринимаемые действия (J):</string></property></widget></item>
       <item row="6" column="1" colspan="3"><widget class="QTextEdit" name="textActionsJ"/></item>
      </layout>
     </widget>
     <widget class="QWidget" name="tabAdditionalKLMN">
      <attribute name="title"><string>Доп. информация (K, L, M, N)</string></attribute>
      <layout class="QGridLayout" name="layoutKLMN">
       <item row="0" column="0"><widget class="QLabel" name="labelK"><property name="text"><string>Район поиска (K):</string></property></widget></item>
       <item row="0" column="1"><widget class="QTextEdit" name="textK"/></item>
       <item row="1" column="0"><widget class="QLabel" name="labelL"><property name="text"><string>Инструкции по координации действий (L):</string></property></widget></item>
       <item row="1" column="1"><widget class="QTextEdit" name="textL"/></item>
       <item row="2" column="0"><widget class="QLabel" name="labelM"><property name="text"><string>Планы на будущее (M):</string></property></widget></item>
       <item row="2" column="1"><widget class="QTextEdit" name="textM"/></item>
       <item row="3" column="0"><widget class="QLabel" name="labelN"><property name="text"><string>Дополнительная информация (N):</string></property></widget></item>
       <item row="3" column="1"><widget class="QTextEdit" name="textN"/></item>
      </layout>
     </widget>
    </widget>
   </item>
   <item>
    <layout class="QHBoxLayout" name="buttonsLayout">
     <item><widget class="QPushButton" name="buttonCancel"><property name="text"><string>Отмена</string></property></widget></item>
     <item><widget class="QPushButton" name="buttonToPdf"><property name="text"><string>Сформировать PDF</string></property></widget></item>
     <item><widget class="QPushButton" name="buttonSend"><property name="text"><string>Отправить</string></property></widget></item>
    </layout>
   </item>
  </layout>
 </widget>
 <resources/>
 <connections/>
</ui>
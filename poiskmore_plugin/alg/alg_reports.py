from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.legends import Legend
import os
from datetime import datetime
from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsCoordinateTransform
class SARReportGenerator:
    """Генератор отчетов для поисково-спасательных операций"""
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    def setup_custom_styles(self):
        """Настройка пользовательских стилей"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=1,  # Центрирование
            textColor=colors.navy
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.darkblue
        ))
    def generate_operation_report(self, operation_data, output_path):
        """Генерация отчета об операции"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            story = []
            # Заголовок отчета
            story.append(Paragraph("ОТЧЕТ О ПОИСКОВО-СПАСАТЕЛЬНОЙ ОПЕРАЦИИ",
                                 self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            # Основная информация
            story.extend(self._add_operation_info(operation_data))
            # Временная информация
            story.extend(self._add_time_info(operation_data))
            # Метеорологические условия
            story.extend(self._add_weather_info(operation_data))
            # Параметры поиска
            story.extend(self._add_search_parameters(operation_data))
            # Результаты
            story.extend(self._add_results_section(operation_data))
            # Построение документа
            doc.build(story)
            return True
        except Exception as e:
            print(f"Ошибка генерации отчета: {str(e)}")
            return False
    def _add_operation_info(self, data):
        """Добавление основной информации об операции"""
        story = []
        story.append(Paragraph("1. ОСНОВНАЯ ИНФОРМАЦИЯ", self.styles['SectionHeader']))
        info_data = [
            ['Номер операции:', data.get('operation_number', 'Не указан')],
            ['Тип аварийной ситуации:', data.get('incident_type', 'Не указан')],
            ['Объект поиска:', data.get('search_object', 'Не указан')],
            ['Координатор МСКЦ:', data.get('coordinator', 'МСКЦ local')],
            ['Район поиска:', data.get('search_area', 'Не указан')]
        ]
        table = Table(info_data, colWidths=[4*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        return story
    def _add_time_info(self, data):
        """Добавление временной информации"""
        story = []
        story.append(Paragraph("2. ВРЕМЕННЫЕ ПАРАМЕТРЫ", self.styles['SectionHeader']))
        time_data = [
            ['Время аварии (UTC):', data.get('incident_time', 'Не указано')],
            ['Время начала поиска (UTC):', data.get('search_start_time', 'Не указано')],
            ['Время окончания поиска (UTC):', data.get('search_end_time', 'Не указано')],
            ['Продолжительность поиска:', data.get('search_duration', 'Не указано')],
            ['Время между аварией и началом поиска:', data.get('response_time', 'Не указано')]
        ]
        table = Table(time_data, colWidths=[4*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        return story
    def _add_weather_info(self, data):
        """Добавление метеорологической информации"""
        story = []
        story.append(Paragraph("3. МЕТЕОРОЛОГИЧЕСКИЕ УСЛОВИЯ", self.styles['SectionHeader']))
        weather = data.get('weather', {})
        weather_data = [
            ['Ветер (направление/скорость):', f"{weather.get('wind_direction', 'Н/Д')}° / {weather.get('wind_speed', 'Н/Д')} м/с"],
            ['Волнение (высота/период):', f"{weather.get('wave_height', 'Н/Д')} м / {weather.get('wave_period', 'Н/Д')} с"],
            ['Течение (направление/скорость):', f"{weather.get('current_direction', 'Н/Д')}° / {weather.get('current_speed', 'Н/Д')} уз"],
            ['Температура воздуха:', f"{weather.get('air_temp', 'Н/Д')} °C"],
            ['Температура воды:', f"{weather.get('water_temp', 'Н/Д')} °C"],
            ['Видимость:', f"{weather.get('visibility', 'Н/Д')} км"],
            ['Осадки:', weather.get('precipitation', 'Нет')]
        ]
        table = Table(weather_data, colWidths=[4*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        return story
    def _add_search_parameters(self, data):
        """Добавление параметров поиска"""
        story = []
        story.append(Paragraph("4. ПАРАМЕТРЫ ПОИСКА", self.styles['SectionHeader']))
        search_params = data.get('search_parameters', {})
        params_data = [
            ['Схема поиска:', search_params.get('pattern', 'Не указана')],
            ['Площадь района поиска:', f"{search_params.get('area_size', 'Н/Д')} кв. морских миль"],
            ['Исходные пункты:', search_params.get('datum_points', 'Не указаны')],
            ['Дальность обнаружения:', f"{search_params.get('detection_range', 'Н/Д')} морских миль"],
            ['Расстояние между галсами:', f"{search_params.get('track_spacing', 'Н/Д')} морских миль"],
            ['Покрытие района:', f"{search_params.get('coverage', 'Н/Д')}%"]
        ]
        table = Table(params_data, colWidths=[4*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(table)
        story.append(Spacer(1, 20))
        return story
    def _add_results_section(self, data):
        """Добавление раздела результатов"""
        story = []
        story.append(Paragraph("5. РЕЗУЛЬТАТЫ ОПЕРАЦИИ", self.styles['SectionHeader']))
        results = data.get('results', {})
        story.append(Paragraph(f"<b>Статус операции:</b> {results.get('status', 'Не указан')}",
                             self.styles['Normal']))
        story.append(Spacer(1, 10))
        if results.get('found', False):
            story.append(Paragraph("<b>ОБЪЕКТ НАЙДЕН</b>", self.styles['Heading3']))
            story.append(Paragraph(f"Время обнаружения: {results.get('found_time', 'Не указано')}",
                                 self.styles['Normal']))
            story.append(Paragraph(f"Координаты обнаружения: {results.get('found_position', 'Не указаны')}",
                                 self.styles['Normal']))
            story.append(Paragraph(f"Состояние объекта: {results.get('condition', 'Не указано')}",
                                 self.styles['Normal']))
        else:
            story.append(Paragraph("<b>ОБЪЕКТ НЕ НАЙДЕН</b>", self.styles['Heading3']))
            story.append(Paragraph(f"Причина прекращения: {results.get('termination_reason', 'Не указана')}",
                                 self.styles['Normal']))
        story.append(Spacer(1, 15))
        # Участвующие суда
        if 'vessels' in data:
            story.append(Paragraph("<b>Участвующие суда:</b>", self.styles['Normal']))
            for vessel in data['vessels']:
                story.append(Paragraph(f"• {vessel.get('name', 'Без названия')} - {vessel.get('type', 'Тип не указан')}",
                                     self.styles['Normal']))
        return story
    def generate_sitrep(self, sitrep_data, output_path):
        """Генерация SITREP (ситуационного отчета)"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            # Заголовок SITREP
            story.append(Paragraph("SITREP - СИТУАЦИОННЫЙ ОТЧЕТ", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            # Время и дата
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M UTC")
            story.append(Paragraph(f"<b>Дата/Время:</b> {current_time}", self.styles['Normal']))
            story.append(Spacer(1, 10))
            # От кого
            story.append(Paragraph(f"<b>От:</b> {sitrep_data.get('from', 'МСКЦ local')}", self.styles['Normal']))
            story.append(Spacer(1, 10))
            # Кому
            story.append(Paragraph(f"<b>Кому:</b> {sitrep_data.get('to', 'ОД МСКЦ')}", self.styles['Normal']))
            story.append(Spacer(1, 10))
            # Приоритет
            story.append(Paragraph(f"<b>Приоритет:</b> {sitrep_data.get('priority', 'Срочный')}", self.styles['Normal']))
            story.append(Spacer(1, 20))
            # Содержание отчета
            story.append(Paragraph("СОДЕРЖАНИЕ ОТЧЕТА:", self.styles['SectionHeader']))
            content = sitrep_data.get('content', 'Содержание отчета не указано')
            story.append(Paragraph(content, self.styles['Normal']))
            doc.build(story)
            return True
        except Exception as e:
            print(f"Ошибка генерации SITREP: {str(e)}")
            return False
    def generate_search_plan(self, plan_data, output_path):
        """Генерация плана поиска"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            # Заголовок
            story.append(Paragraph("ПЛАН ПОИСКОВО-СПАСАТЕЛЬНОЙ ОПЕРАЦИИ", self.styles['CustomTitle']))
            story.append(Spacer(1, 20))
            # 1. Ситуация
            story.append(Paragraph("1. СИТУАЦИЯ", self.styles['SectionHeader']))
            story.append(Paragraph(plan_data.get('situation', 'Описание ситуации не указано'),
                                 self.styles['Normal']))
            story.append(Spacer(1, 15))
            # 2. Задача
            story.append(Paragraph("2. ЗАДАЧА", self.styles['SectionHeader']))
            story.append(Paragraph(plan_data.get('mission', 'Задача не указана'),
                                 self.styles['Normal']))
            story.append(Spacer(1, 15))
            # 3. Выполнение
            story.append(Paragraph("3. ВЫПОЛНЕНИЕ", self.styles['SectionHeader']))
            # 3.1 Схема поиска
            story.append(Paragraph("3.1 Схема поиска:", self.styles['Normal']))
            story.append(Paragraph(plan_data.get('search_pattern', 'Схема не указана'),
                                 self.styles['Normal']))
            story.append(Spacer(1, 10))
            # 3.2 Участвующие силы
            story.append(Paragraph("3.2 Участвующие силы:", self.styles['Normal']))
            forces = plan_data.get('forces', [])
            for force in forces:
                story.append(Paragraph(f"• {force}", self.styles['Normal']))
            story.append(Spacer(1, 10))
            # 3.3 Координация
            story.append(Paragraph("3.3 Координация:", self.styles['Normal']))
            story.append(Paragraph(plan_data.get('coordination', 'Не указана'),
                                 self.styles['Normal']))
            story.append(Spacer(1, 15))
            # 4. Обеспечение
            story.append(Paragraph("4. ОБЕСПЕЧЕНИЕ", self.styles['SectionHeader']))
            story.append(Paragraph(plan_data.get('support', 'Не указано'),
                                 self.styles['Normal']))
            story.append(Spacer(1, 15))
            # 5. Связь
            story.append(Paragraph("5. СВЯЗЬ", self.styles['SectionHeader']))
            story.append(Paragraph(plan_data.get('communications', 'Не указана'),
                                 self.styles['Normal']))
            doc.build(story)
            return True
        except Exception as e:
            print(f"Ошибка генерации плана поиска: {str(e)}")
            return False
def generate_standard_forms(form_type, data, output_path):
    """Генерация стандартных форм"""
    generator = SARReportGenerator()
    if form_type == 'operation_report':
        return generator.generate_operation_report(data, output_path)
    elif form_type == 'sitrep':
        return generator.generate_sitrep(data, output_path)
    elif form_type == 'search_plan':
        return generator.generate_search_plan(data, output_path)
    else:
        return False
def export_search_data_to_csv(search_data, output_path):
    """Экспорт данных поиска в CSV"""
    import csv
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Заголовки
            headers = ['Время', 'Широта', 'Долгота', 'Курс', 'Скорость', 'Статус']
            writer.writerow(headers)
            # Данные
            for record in search_data:
                row = [
                    record.get('time', ''),
                    record.get('latitude', ''),
                    record.get('longitude', ''),
                    record.get('course', ''),
                    record.get('speed', ''),
                    record.get('status', '')
                ]
                writer.writerow(row)
        return True
    except Exception as e:
        print(f"Ошибка экспорта в CSV: {str(e)}")
        return False
def create_map_export(layers, output_path, format='PNG'):
    """Экспорт карты с районами поиска"""
    from qgis.core import QgsMapSettings, QgsMapRendererParallelJob
    from qgis.PyQt.QtCore import QSize
    try:
        # Настройки карты
        settings = QgsMapSettings()
        settings.setLayers(layers)
        settings.setOutputSize(QSize(1200, 800))
        settings.setDestinationCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        # Расчет экстента для всех слоев
        extent = None
        for layer in layers:
            if extent is None:
                extent = layer.extent()
            else:
                extent.combineExtentWith(layer.extent())
        if extent:
            settings.setExtent(extent)
        # Рендеринг
        render = QgsMapRendererParallelJob(settings)
        render.start()
        render.waitForFinished()
        img = render.renderedImage()
        img.save(output_path, format)
        return True
    except Exception as e:
        print(f"Ошибка экспорта карты: {str(e)}")
        return False
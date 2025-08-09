from qgis.gui import QgsMapToolEmitPoint, QgsMapToolEdit
from qgis.core import QgsGeometry, QgsFeature, QgsVectorLayer, QgsProject, QgsField, QgsFields, QgsPointXY, QgsRectangle
from qgis.PyQt.QtCore import QVariant, pyqtSignal
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.PyQt.QtGui import QColor
import math
class ManualAreaTool(QgsMapToolEmitPoint):
    """Инструмент для ручного создания района поиска"""
    area_created = pyqtSignal(QgsGeometry)
    def __init__(self, canvas, callback=None):
        super().__init__(canvas)
        self.points = []
        self.callback = callback
        self.canvas = canvas
        self.rubber_band = None
        self.temp_line = None
    def canvasReleaseEvent(self, e):
        """Обработка клика мыши для добавления точки"""
        point = self.toMapCoordinates(e.pos())
        self.points.append(point)
        # Визуализация процесса построения
        self.update_rubber_band()
        # Проверка завершения полигона
        if len(self.points) >= 3:
            # Проверка двойного клика или клика рядом с первой точкой
            first_point = self.points[0]
            distance = math.sqrt((point.x() - first_point.x())**2 + (point.y() - first_point.y())**2)
            if distance < 0.01:  # Если кликнули рядом с первой точкой
                self.finish_polygon()
    def canvasDoubleClickEvent(self, e):
        """Завершение построения полигона двойным кликом"""
        if len(self.points) >= 3:
            self.finish_polygon()
    def finish_polygon(self):
        """Завершение построения полигона"""
        if len(self.points) >= 3:
            # Создание полигона
            polygon_points = self.points + [self.points[0]]  # Замыкание полигона
            poly = QgsGeometry.fromPolygonXY([polygon_points])
            # Валидация полигона
            if self.validate_polygon(poly):
                if self.callback:
                    self.callback(poly)
                self.area_created.emit(poly)
                self.reset_tool()
            else:
                QMessageBox.warning(None, "Ошибка", "Некорректный полигон. Попробуйте снова.")
                self.reset_tool()
    def validate_polygon(self, polygon):
        """Валидация созданного полигона"""
        if not polygon.isGeosValid():
            return False
        area = polygon.area()
        if area < 0.0001:  # Слишком маленькая площадь
            return False
        return True
    def update_rubber_band(self):
        """Обновление визуализации при построении"""
        # Здесь можно добавить код для отображения линий при построении
        pass
    def reset_tool(self):
        """Сброс инструмента"""
        self.points = []
        if self.rubber_band:
            self.canvas.scene().removeItem(self.rubber_band)
            self.rubber_band = None
    def keyPressEvent(self, e):
        """Обработка нажатий клавиш"""
        if e.key() == 27:  # ESC - отмена
            self.reset_tool()
        elif e.key() == 13:  # Enter - завершение
            if len(self.points) >= 3:
                self.finish_polygon()
def manual_area(iface):
    """Запуск инструмента ручного создания района"""
    canvas = iface.mapCanvas()
    tool = ManualAreaTool(canvas, lambda poly: add_manual_layer(poly, iface))
    canvas.setMapTool(tool)
    # Информационное сообщение
    iface.messageBar().pushMessage(
        "Ручное построение района",
        "Кликайте на карте для создания точек полигона. Двойной клик или клик рядом с первой точкой для завершения.",
        level=1
    )
def add_manual_layer(poly, iface):
    """Добавление ручно созданного района в проект"""
    layer = QgsVectorLayer("Polygon?crs=epsg:4326", "Ручной район поиска", "memory")
    pr = layer.dataProvider()
    # Добавление полей атрибутов
    fields = QgsFields()
    fields.append(QgsField("area_name", QVariant.String))
    fields.append(QgsField("area_type", QVariant.String))
    fields.append(QgsField("created_by", QVariant.String))
    fields.append(QgsField("creation_time", QVariant.String))
    fields.append(QgsField("area_km2", QVariant.Double))
    fields.append(QgsField("perimeter_km", QVariant.Double))
    pr.addAttributes(fields)
    layer.updateFields()
    # Расчет характеристик района
    area_km2 = calculate_area_km2(poly)
    perimeter_km = calculate_perimeter_km(poly)
    # Создание feature
    feat = QgsFeature()
    feat.setGeometry(poly)
    feat.setAttributes([
        "Ручной район",
        "Пользовательский",
        "QGIS User",
        "2025-07-23 10:02",
        area_km2,
        perimeter_km
    ])
    pr.addFeatures([feat])
    # Добавление в проект
    QgsProject.instance().addMapLayer(layer)
    # Настройка стиля
    setup_manual_area_style(layer)
    # Уведомление пользователя
    iface.messageBar().pushMessage(
        "Район создан",
        f"Ручной район площадью {area_km2:.2f} км² добавлен в проект",
        level=0
    )
def calculate_area_km2(geometry):
    """Расчет площади в квадратных километрах"""
    # Упрощенный расчет (для точного расчета нужно использовать проекцию)
    area_deg2 = geometry.area()
    # Приблизительный перевод градусов в км² (зависит от широты)
    km2_per_deg2 = 111.32 * 111.32  # Примерно на экваторе
    return area_deg2 * km2_per_deg2
def calculate_perimeter_km(geometry):
    """Расчет периметра в километрах"""
    perimeter_deg = geometry.length()
    km_per_deg = 111.32  # Примерно
    return perimeter_deg * km_per_deg
def setup_manual_area_style(layer):
    """Настройка стиля для ручного района"""
    symbol = layer.renderer().symbol()
    # Настройка заливки
    symbol.setColor(QColor(255, 165, 0, 80))  # Оранжевый с прозрачностью
    # Настройка границы
    symbol.symbolLayer(0).setStrokeColor(QColor(255, 165, 0))
    symbol.symbolLayer(0).setStrokeWidth(2)
    layer.triggerRepaint()
class AreaEditTool(QgsMapToolEdit):
    """Инструмент для редактирования существующих районов"""
    def __init__(self, canvas, layer):
        super().__init__(canvas)
        self.layer = layer
        self.canvas = canvas
    def canvasReleaseEvent(self, e):
        """Обработка редактирования"""
        # Здесь можно добавить логику для редактирования вершин полигона
        pass
def create_predefined_shapes(shape_type, center_point, size):
    """Создание предопределенных форм районов"""
    if shape_type == "circle":
        return create_circle(center_point, size)
    elif shape_type == "square":
        return create_square(center_point, size)
    elif shape_type == "rectangle":
        return create_rectangle(center_point, size, size * 1.5)
    elif shape_type == "sector":
        return create_sector(center_point, size, 0, 90)  # Сектор 90 градусов
    else:
        return create_circle(center_point, size)  # По умолчанию круг
def create_circle(center, radius):
    """Создание кругового района"""
    points = []
    for i in range(36):
        angle = math.radians(i * 10)
        x = center.x() + radius * math.cos(angle)
        y = center.y() + radius * math.sin(angle)
        points.append(QgsPointXY(x, y))
    points.append(points[0])
    return QgsGeometry.fromPolygonXY([points])
def create_square(center, side_length):
    """Создание квадратного района"""
    half_side = side_length / 2
    points = [
        QgsPointXY(center.x() - half_side, center.y() - half_side),
        QgsPointXY(center.x() + half_side, center.y() - half_side),
        QgsPointXY(center.x() + half_side, center.y() + half_side),
        QgsPointXY(center.x() - half_side, center.y() + half_side),
        QgsPointXY(center.x() - half_side, center.y() - half_side)
    ]
    return QgsGeometry.fromPolygonXY([points])
def create_rectangle(center, width, height):
    """Создание прямоугольного района"""
    half_width = width / 2
    half_height = height / 2
    points = [
        QgsPointXY(center.x() - half_width, center.y() - half_height),
        QgsPointXY(center.x() + half_width, center.y() - half_height),
        QgsPointXY(center.x() + half_width, center.y() + half_height),
        QgsPointXY(center.x() - half_width, center.y() + half_height),
        QgsPointXY(center.x() - half_width, center.y() - half_height)
    ]
    return QgsGeometry.fromPolygonXY([points])
def create_sector(center, radius, start_angle, end_angle):
    """Создание секторного района"""
    points = [center]  # Начинаем с центра
    # Добавляем точки дуги
    angle_step = (end_angle - start_angle) / 36
    for i in range(37):  # 37 точек для замыкания
        angle = math.radians(start_angle + i * angle_step)
        x = center.x() + radius * math.cos(angle)
        y = center.y() + radius * math.sin(angle)
        points.append(QgsPointXY(x, y))
    points.append(center)  # Замыкание к центру
    return QgsGeometry.fromPolygonXY([points])
def split_area_into_subareas(geometry, num_subareas):
    """Разделение района на подрайоны для поиска"""
    # Получение bounding box
    bbox = geometry.boundingBox()
    subareas = []
    if num_subareas == 4:
        # Разделение на 4 квадранта
        center_x = bbox.center().x()
        center_y = bbox.center().y()
        quadrants = [
            # Северо-западный
            QgsGeometry.fromRect(QgsRectangle(bbox.xMinimum(), center_y, center_x, bbox.yMaximum())),
            # Северо-восточный
            QgsGeometry.fromRect(QgsRectangle(center_x, center_y, bbox.xMaximum(), bbox.yMaximum())),
            # Юго-западный
            QgsGeometry.fromRect(QgsRectangle(bbox.xMinimum(), bbox.yMinimum(), center_x, center_y)),
            # Юго-восточный
            QgsGeometry.fromRect(QgsRectangle(center_x, bbox.yMinimum(), bbox.xMaximum(), center_y))
        ]
        for i, quad in enumerate(quadrants):
            intersection = geometry.intersection(quad)
            if not intersection.isEmpty():
                subareas.append({
                    'geometry': intersection,
                    'id': f"SA{i+1}",
                    'priority': i + 1
                })
    return subareas
def distant_points_calculation(p1, p2, params): dx = p2.x() - p1.x() dy = p2.y() - p1.y() distance = sqrt(dx2 + dy2)
if distance > params.get('threshold', 1.0): radius = params.get('radius', 0.5) area1 = p1.buffer(radius, 30) area2 = p2.buffer(radius, 30)
angle = atan2(dy, dx) half_width = params.get('width', 0.2) / 2 offset_x = half_width * sin(angle) offset_y = half_width * cos(angle)
rp1 = QgsPointXY(p1.x() - offset_x, p1.y() + offset_y) rp2 = QgsPointXY(p1.x() + offset_x, p1.y() - offset_y) rp3 = QgsPointXY(p2.x() + offset_x, p2.y() - offset_y) rp4 = QgsPointXY(p2.x() - offset_x, p2.y() + offset_y)
rect = QgsGeometry.fromPolygonXY([[rp1, rp2, rp3, rp4]])
full_area = area1.combine(rect).combine(area2) return full_area else: center = QgsPointXY((p1.x() + p2.x())/2, (p1.y() + p2.y())/2) major = distance / 2 + params.get('radius', 0.5) minor = params.get('minor', 0.3) ellipse = center.buffer(major, minor, 30) # Пример, для реального эллипса использовать custom return ellipse
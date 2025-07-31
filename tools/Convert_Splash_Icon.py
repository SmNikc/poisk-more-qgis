from PIL import Image, ImageOps

input_path = r'C:\Projects\poisk-more-qgis\resources\splash.jpg'
output_path = r'C:\Projects\poisk-more-qgis\resources\icon.png'

# Открываем исходное изображение
image = Image.open(input_path)

# Обрезаем меньше снизу (например, 5-7%) для сохранения полной эмблемы
width, height = image.size
cropped_image = image.crop((0, 0, width, height - int(height * 0.07)))

# Делаем изображение квадратным (128×128 пикселей)
square_image = ImageOps.fit(cropped_image, (128, 128), Image.Resampling.LANCZOS)

# Сохраняем результат
square_image.save(output_path, format='PNG')

print(f"Иконка успешно создана: {output_path}")

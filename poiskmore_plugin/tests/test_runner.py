pythonimport subprocess

def run_pytest_in_qgis_env():
    try:
        result = subprocess.run([
            r"C:\Program Files\QGIS 3.40.9\bin\python-qgis-ltr.bat",
            "-m", "pytest", "tests/"
        ], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Ошибка запуска тестов: {e}")
        return False
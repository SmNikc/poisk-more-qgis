import os
import subprocess
import sys

# === Конфигурация ===
GITHUB_USERNAME = "smnikc"  # ← замените, если нужно
IMAGE_NAME = "poiskmore-qgis"
IMAGE_TAG = "3.40.9"
FULL_IMAGE_NAME = f"ghcr.io/{GITHUB_USERNAME}/{IMAGE_NAME}:{IMAGE_TAG}"
DOCKERFILE_PATH = "Dockerfile"
BUILD_CONTEXT = "C:/Projects/poisk-more-qgis"

# === Авторизация в GHCR ===
def login_to_ghcr():
    print("🔐 Введите ваш GitHub Personal Access Token (с правами write:packages):")
    token = input("PAT: ").strip()
    result = subprocess.run(f'echo {token} | docker login ghcr.io -u {GITHUB_USERNAME} --password-stdin', shell=True)
    if result.returncode != 0:
        print("❌ Ошибка авторизации в GHCR")
        sys.exit(1)
    print("✅ Авторизация прошла успешно")

# === Сборка образа ===
def build_image():
    print(f"⚙️ Сборка образа: {FULL_IMAGE_NAME}")
    result = subprocess.run([
        "docker", "build",
        "-t", FULL_IMAGE_NAME,
        "-f", os.path.join(BUILD_CONTEXT, DOCKERFILE_PATH),
        BUILD_CONTEXT
    ])
    if result.returncode != 0:
        print("❌ Ошибка сборки")
        sys.exit(1)
    print("✅ Образ собран успешно")

# === Публикация ===
def push_image():
    print(f"📦 Публикация образа в GHCR: {FULL_IMAGE_NAME}")
    result = subprocess.run(["docker", "push", FULL_IMAGE_NAME])
    if result.returncode != 0:
        print("❌ Публикация не удалась")
        sys.exit(1)
    print("✅ Образ опубликован в GHCR")

# === Запуск ===
if __name__ == "__main__":
    login_to_ghcr()
    build_image()
    push_image()
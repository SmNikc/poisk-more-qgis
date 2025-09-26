"""
Миграция БД для добавления таблиц расписания ветра и течений
"""

def migrate_database_for_weather_schedule(conn):
    """Добавляет таблицы для расписания метеоусловий"""
    
    cursor = conn.cursor()
    
    # Таблица расписания ветра
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wind_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            t_utc TEXT NOT NULL,                    -- Время UTC
            dir_from_deg REAL NOT NULL,             -- Направление откуда (градусы)
            speed_ms REAL NOT NULL,                 -- Скорость м/с
            speed_kn REAL,                          -- Скорость в узлах
            gust_ms REAL,                           -- Порывы м/с
            height_m REAL DEFAULT 10,               -- Высота измерения (метры)
            source TEXT,                            -- Источник данных
            weight REAL DEFAULT 1.0,                -- Вес для усреднения
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
        )
    """)
    
    # Индекс для быстрого поиска
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_wind_schedule_incident_time 
        ON wind_schedule(incident_id, t_utc)
    """)
    
    # Таблица расписания течений
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS current_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            t_utc TEXT NOT NULL,                    -- Время UTC
            dir_to_deg REAL NOT NULL,               -- Направление куда (градусы)
            speed_kn REAL NOT NULL,                 -- Скорость в узлах
            depth_m REAL DEFAULT 0,                 -- Глубина (0 = поверхностное)
            type TEXT DEFAULT 'surface',            -- Тип течения
            source TEXT,                            -- Источник
            weight REAL DEFAULT 1.0,                -- Вес для усреднения
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
        )
    """)
    
    # Индекс
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_current_schedule_incident_time 
        ON current_schedule(incident_id, t_utc)
    """)
    
    # Таблица коэффициентов ливея для разных объектов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leeway_coefficients (
            id INTEGER PRIMARY KEY,
            object_type TEXT UNIQUE NOT NULL,       -- Тип объекта
            dwl_slope REAL NOT NULL,                -- Downwind slope
            dwl_intercept REAL NOT NULL,            -- Downwind intercept
            cwl_slope REAL NOT NULL,                -- Crosswind slope
            cwl_intercept REAL NOT NULL,            -- Crosswind intercept
            sigma_dwl REAL,                         -- Стандартное отклонение DWL
            sigma_cwl REAL,                         -- Стандартное отклонение CWL
            divergence_rate REAL,                   -- Скорость расхождения
            reference TEXT                          -- Ссылка на источник (IAMSAR)
        )
    """)
    
    # Заполняем стандартные коэффициенты из IAMSAR Appendix N
    leeway_data = [
        ('Спасательный плот с тентом', 0.0110, 0.0, 0.0060, 0.0, 0.1, 0.1, 0.1, 'IAMSAR Vol.II App.N'),
        ('Спасательный плот без тента', 0.0160, 0.0, 0.0100, 0.0, 0.15, 0.15, 0.15, 'IAMSAR Vol.II App.N'),
        ('Человек в спасжилете', 0.0120, 0.0, 0.0050, 0.0, 0.1, 0.1, 0.08, 'IAMSAR Vol.II App.N'),
        ('Человек без спасжилета', 0.0100, 0.0, 0.0040, 0.0, 0.1, 0.1, 0.05, 'IAMSAR Vol.II App.N'),
        ('Малое судно <20м', 0.0420, 0.0, 0.0480, 0.0, 0.2, 0.2, 0.2, 'IAMSAR Vol.II App.N'),
        ('Среднее судно 20-50м', 0.0330, 0.0, 0.0420, 0.0, 0.15, 0.15, 0.15, 'IAMSAR Vol.II App.N'),
        ('Большое судно >50м', 0.0280, 0.0, 0.0380, 0.0, 0.1, 0.1, 0.1, 'IAMSAR Vol.II App.N'),
        ('Парусная яхта (киль)', 0.0400, 0.0, 0.0400, 0.0, 0.15, 0.15, 0.15, 'IAMSAR Vol.II App.N'),
        ('Парусная яхта (дрейф)', 0.0600, 0.0, 0.0800, 0.0, 0.2, 0.2, 0.25, 'IAMSAR Vol.II App.N'),
        ('Рыболовное судно', 0.0350, 0.0, 0.0450, 0.0, 0.15, 0.15, 0.15, 'IAMSAR Vol.II App.N'),
        ('Обломки', 0.0150, 0.0, 0.0100, 0.0, 0.2, 0.2, 0.3, 'IAMSAR Vol.II App.N'),
        ('Морская авиация', 0.0200, 0.0, 0.0200, 0.0, 0.1, 0.1, 0.1, 'IAMSAR Vol.II App.N')
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO leeway_coefficients 
        (object_type, dwl_slope, dwl_intercept, cwl_slope, cwl_intercept, 
         sigma_dwl, sigma_cwl, divergence_rate, reference)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, leeway_data)
    
    # Таблица результатов расчета дрейфа
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drift_calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            calculation_time TEXT DEFAULT CURRENT_TIMESTAMP,
            
            -- Исходные данные
            lkp_lat REAL NOT NULL,                  -- Last Known Position
            lkp_lon REAL NOT NULL,
            lkp_time TEXT NOT NULL,
            object_type TEXT NOT NULL,
            
            -- Результаты расчета
            datum_left_lat REAL,                    -- Левая ветвь датума
            datum_left_lon REAL,
            datum_right_lat REAL,                   -- Правая ветвь датума  
            datum_right_lon REAL,
            datum_center_lat REAL,                  -- Центр
            datum_center_lon REAL,
            
            total_drift_nm REAL,                    -- Общее смещение (мили)
            drift_direction REAL,                   -- Направление дрейфа
            divergence_nm REAL,                     -- Расхождение датумов
            
            -- Погрешности
            position_error_nm REAL,                 -- X
            drift_error_nm REAL,                    -- De
            navigation_error_nm REAL,               -- Y
            total_probable_error_nm REAL,           -- E = sqrt(X²+De²+Y²)
            
            -- Дополнительно
            asw_speed_ms REAL,                      -- Средний ветер
            asw_direction REAL,
            twc_speed_kn REAL,                      -- Среднее течение
            twc_direction REAL,
            
            notes TEXT,
            
            FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
        )
    """)
    
    # Таблица траектории дрейфа по времени
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drift_track (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            calculation_id INTEGER NOT NULL,
            t_utc TEXT NOT NULL,
            
            -- Компоненты дрейфа
            wind_speed_ms REAL,
            wind_dir REAL,
            dwl_kn REAL,                           -- Downwind leeway
            cwl_kn REAL,                           -- Crosswind leeway (со знаком)
            leeway_speed_kn REAL,
            leeway_dir REAL,
            
            current_speed_kn REAL,
            current_dir REAL,
            
            drift_speed_kn REAL,                   -- Итоговый дрейф
            drift_dir REAL,
            
            -- Позиции
            left_lat REAL,                         -- Левая ветвь
            left_lon REAL,
            right_lat REAL,                        -- Правая ветвь  
            right_lon REAL,
            
            divergence_nm REAL,                    -- Расхождение на этот момент
            
            FOREIGN KEY (calculation_id) REFERENCES drift_calculations(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    print("✅ База данных обновлена для хранения расписания ветра и течений")


def save_wind_schedule(conn, incident_id, wind_data):
    """Сохранить расписание ветра"""
    cursor = conn.cursor()
    
    # Удаляем старые записи
    cursor.execute("DELETE FROM wind_schedule WHERE incident_id = ?", (incident_id,))
    
    # Вставляем новые
    for entry in wind_data:
        cursor.execute("""
            INSERT INTO wind_schedule 
            (incident_id, t_utc, dir_from_deg, speed_ms, speed_kn, gust_ms, height_m, source, weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_id, 
            entry['time'],
            entry['direction'],
            entry['speed_ms'],
            entry.get('speed_kn', entry['speed_ms'] * 1.94384),  # Конвертация
            entry.get('gust'),
            entry.get('height', 10),
            entry.get('source', 'Manual'),
            entry.get('weight', 1.0)
        ))
    
    conn.commit()


def save_current_schedule(conn, incident_id, current_data):
    """Сохранить расписание течений"""
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM current_schedule WHERE incident_id = ?", (incident_id,))
    
    for entry in current_data:
        cursor.execute("""
            INSERT INTO current_schedule
            (incident_id, t_utc, dir_to_deg, speed_kn, depth_m, type, source, weight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_id,
            entry['time'],
            entry['direction'],
            entry['speed_kn'],
            entry.get('depth', 0),
            entry.get('type', 'surface'),
            entry.get('source', 'Manual'),
            entry.get('weight', 1.0)
        ))
    
    conn.commit()


def load_wind_schedule(conn, incident_id):
    """Загрузить расписание ветра"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t_utc, dir_from_deg, speed_ms, speed_kn, gust_ms, height_m, source
        FROM wind_schedule
        WHERE incident_id = ?
        ORDER BY t_utc
    """, (incident_id,))
    
    return cursor.fetchall()


def load_current_schedule(conn, incident_id):
    """Загрузить расписание течений"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t_utc, dir_to_deg, speed_kn, depth_m, type, source
        FROM current_schedule  
        WHERE incident_id = ?
        ORDER BY t_utc
    """, (incident_id,))
    
    return cursor.fetchall()

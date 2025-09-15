def _create_service_menu(self):
        """Создать меню 'Сервис' - настройки и авторизация."""
        service_menu = QMenu("Сервис", self.main_menu)
        service_menu.setObjectName("service_menu")
        self.menus['service'] = service_menu
        
        # 1. Характер аварийной ситуации
        action_emergency = QAction(
            self._get_icon('emergency_type.png'),
            "Характер аварийной ситуации",
            self.iface.mainWindow()
        )
        action_emergency.setStatusTip("Настройка типов аварийных ситуаций и их характеристик")
        action_emergency.triggered.connect(self._on_emergency_types)
        service_menu.addAction(action_emergency)
        self.actions['emergency_types'] = action_emergency
        
        # 2. Авторизация
        action_auth = QAction(
            self._get_icon('authorization.png'),
            "Авторизация",
            self.iface.mainWindow()
        )
        action_auth.setShortcut("Ctrl+L")
        action_auth.setStatusTip("Авторизация пользователя в системе")
        action_auth.triggered.connect(self._on_authorization)
        service_menu.addAction(action_auth)
        self.actions['authorization'] = action_auth
        
        # 3. Синхронизировать адресную книгу
        action_sync = QAction(
            self._get_icon('sync_contacts.png'),
            "Синхронизировать адресную книгу",
            self.iface.mainWindow()
        )
        action_sync.setStatusTip("Синхронизация контактов поисково-спасательных служб")
        action_sync.triggered.connect(self._on_sync_contacts)
        action_sync.setEnabled(False)  # Активно после авторизации
        service_menu.addAction(action_sync)
        self.actions['sync_contacts'] = action_sync

        self.main_menu.addMenu(service_menu)
    
    def _create_datum_menu(self):
        """Создать меню 'Исходный пункт' - расчет исходных точек поиска."""
        datum_menu = QMenu("Исходный пункт", self.main_menu)
        datum_menu.setObjectName("datum_menu")
        self.menus['datum'] = datum_menu
        
        # 1. Вычислить исходные пункты
        action_calculate = QAction(
            self._get_icon('calculate_datum.png'),
            "Вычислить исходные пункты",
            self.iface.mainWindow()
        )
        action_calculate.setShortcut("Ctrl+D")
        action_calculate.setStatusTip("Расчет исходных пунктов с учетом дрейфа")
        action_calculate.triggered.connect(self._on_calculate_datum)
        action_calculate.setEnabled(False)  # Активно при наличии операции
        datum_menu.addAction(action_calculate)
        self.actions['calculate_datum'] = action_calculate
        
        # 2. Исходная линия
        action_line = QAction(
            self._get_icon('datum_line.png'),
            "Исходная линия",
            self.iface.mainWindow()
        )
        action_line.setStatusTip("Построение исходной линии между пунктами")
        action_line.triggered.connect(self._on_datum_line)
        action_line.setEnabled(False)  # Активно при наличии операции
        datum_menu.addAction(action_line)
        self.actions['datum_line'] = action_line
        
        self.main_menu.addMenu(datum_menu)
    
    def _create_area_menu(self):
        """Создать меню 'Район' - управление районами поиска."""
        area_menu = QMenu("Район", self.main_menu)
        area_menu.setObjectName("area_menu")
        self.menus['area'] = area_menu
        
        # 1. Подменю "Создать район"
        create_area_menu = QMenu("Создать район", area_menu)
        create_area_menu.setIcon(self._get_icon('create_area.png'))
        self.menus['create_area'] = create_area_menu
        
        # Типы районов поиска согласно методике IAMSAR
        area_types = [
            {
                'id': 'two_points',
                'name': 'Поиск от двух исходных пунктов',
                'icon': 'area_two_points.png',
                'description': 'Район между двумя рассчитанными исходными пунктами'
            },
            {
                'id': 'far_districts',
                'name': 'Поиск в далеко разнесенных районах',
                'icon': 'area_far_districts.png',
                'description': 'Несколько отдельных районов поиска'
            },
            {
                'id': 'line_between_far',
                'name': 'Линия между далеко разнесенными районами',
                'icon': 'area_line_between.png',
                'description': 'Связующая линия между удаленными районами'
            }

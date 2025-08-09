def standard_forms(self):
        # dialog = StandardFormsDialog(self.iface)
        # dialog.exec_()
        # generate_pdf_from_form()
        QMessageBox.information(self.iface.mainWindow(), "Стандартные формы", "Функционал стандартных форм не реализован.")
    def search_plan(self):
        # dialog = SearchPlanDialog(self.iface)
        # if dialog.exec_() == QDialog.Accepted:
        # generate_word_plan()
        QMessageBox.information(self.iface.mainWindow(), "План поиска", "Функционал плана поиска не реализован.")
    def gmskc_tablet(self):
        # open_gmskc_tablet_in_word()
        QMessageBox.information(self.iface.mainWindow(), "Планшет ГМСКЦ", "Функционал планшета ГМСКЦ не реализован.")
    def incident_type(self):
        dialog = IncidentObjectDialog(self.iface)
        dialog.exec_()
    def about_program(self):
        QMessageBox.about(self.iface.mainWindow(), "О программе", "Поиск-Море - Плагин для QGIS для поисково-спасательных операций.")
    def documentation(self):
        os.startfile(os.path.join(self.plugin_dir, 'docs/manual.pdf'))
    def unload(self):
        self.iface.removePluginMenu("Поиск-Море", self.menu.menuAction())
        self.menu.deleteLater()
        self.actions.clear()
from dialogs.dialog_duty_tablet import DialogDutyOfficerTablet
class DutyTabletManager:
def open_tablet(self, case_id):
dialog = DialogDutyOfficerTablet(None)
dialog.exec_()
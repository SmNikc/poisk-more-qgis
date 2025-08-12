"""Dialog for entering parameters for search area creation.

The real plugin contains a rather complex dialog defined in the ``forms``
directory, however for the purposes of the tests in this kata a very small
subset is required.  The previous implementation only provided an ``OK``
button and a spin box, but it lacked a method to return the user provided
values which resulted in ``AttributeError`` being raised when the dialog was
used by :func:`mainPlugin.search_two_points`.

This module now exposes a tiny dialog with a ``get_params`` method returning
the parameters needed by the ``create_search_area`` helper.
"""

from PyQt5.QtWidgets import (
    QDialog,
    QDoubleSpinBox,
    QPushButton,
    QVBoxLayout,
    QLabel,
)


class SearchParamsDialog(QDialog):
    """Minimal dialog for specifying search parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Параметры поиска:"))

        # Width of the search area corridor (in degrees).
        self.width = QDoubleSpinBox(minimum=0.1, value=0.2)
        layout.addWidget(self.width)

        btn = QPushButton("OK")
        btn.clicked.connect(self.ok)
        layout.addWidget(btn)

    def ok(self):
        self.accept()

    def get_params(self):
        """Return parameters selected in the dialog.

        Returns
        -------
        dict
            Dictionary with keys understood by ``create_search_area``.
        """

        # ``create_search_area`` expects a ``width`` value when operating in
        # ``two_points`` mode.  The dialog only exposes a single spin box so we
        # simply forward its value.
        return {"width": float(self.width.value())}

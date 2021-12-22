from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEvent

from .view import View


class TabletApplication(QApplication):
    """
    Custom QApplication to avoid the tablet event bug.
    """

    def __init__(self, argv):
        """
        Store the main window object for event(self, a0: Event) to use.

        Args:
            argv: Only used to inherit the parent class.

        """

        super(TabletApplication, self).__init__(argv)
        self._window = None

    def event(self, a0: QEvent) -> bool:
        """
        catch the tablet event of QGraphicsView.

        Args:
            a0: Event loop.

        Returns:
            Inherit the parent class

        """
        if self._window:
            if a0.type() in (QEvent.TabletEnterProximity, QEvent.TabletLeaveProximity):
                View.tablet_used = a0.type() == QEvent.TabletEnterProximity

        return super(TabletApplication, self).event(a0)

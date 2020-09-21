# -*- coding: utf-8 -*-
# flake8: noqa

################################################################################
## Form generated from reading UI file 'boundary_dialog.ui'
##
## Created by: Qt User Interface Compiler version 5.14.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QMetaObject, QObject, QPoint,
    QRect, QSize, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QLinearGradient, QPalette, QPainter, QPixmap,
    QRadialGradient)
from PySide2.QtWidgets import *


class Ui_BoundaryDialog(object):
    def setupUi(self, BoundaryDialog):
        if BoundaryDialog.objectName():
            BoundaryDialog.setObjectName(u"BoundaryDialog")
        BoundaryDialog.resize(400, 141)
        self.verticalLayout = QVBoxLayout(BoundaryDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.form_layout = QFormLayout()
        self.form_layout.setObjectName(u"form_layout")
        self.edit_label = QLabel(BoundaryDialog)
        self.edit_label.setObjectName(u"edit_label")

        self.form_layout.setWidget(0, QFormLayout.LabelRole, self.edit_label)

        self.user_edit = QLineEdit(BoundaryDialog)
        self.user_edit.setObjectName(u"user_edit")

        self.form_layout.setWidget(0, QFormLayout.FieldRole, self.user_edit)

        self.display_label = QLabel(BoundaryDialog)
        self.display_label.setObjectName(u"display_label")

        self.form_layout.setWidget(1, QFormLayout.LabelRole, self.display_label)

        self.user_display = QComboBox(BoundaryDialog)
        self.user_display.setObjectName(u"user_display")

        self.form_layout.setWidget(1, QFormLayout.FieldRole, self.user_display)


        self.verticalLayout.addLayout(self.form_layout)

        self.button_box = QDialogButtonBox(BoundaryDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Help|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(BoundaryDialog)
        self.button_box.accepted.connect(BoundaryDialog.accept)
        self.button_box.rejected.connect(BoundaryDialog.reject)

        QMetaObject.connectSlotsByName(BoundaryDialog)
    # setupUi

    def retranslateUi(self, BoundaryDialog):
        BoundaryDialog.setWindowTitle(QCoreApplication.translate("BoundaryDialog", u"Dialog", None))
        self.edit_label.setText(QCoreApplication.translate("BoundaryDialog", u"User editable text:", None))
        self.display_label.setText(QCoreApplication.translate("BoundaryDialog", u"User selectable display type:", None))
    # retranslateUi


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'simulation_dialog.ui'
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


class Ui_SimulationDialog(object):
    def setupUi(self, SimulationDialog):
        if SimulationDialog.objectName():
            SimulationDialog.setObjectName(u"SimulationDialog")
        SimulationDialog.resize(400, 141)
        self.verticalLayout = QVBoxLayout(SimulationDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.form_layout = QFormLayout()
        self.form_layout.setObjectName(u"form_layout")
        self.edit_label = QLabel(SimulationDialog)
        self.edit_label.setObjectName(u"edit_label")

        self.form_layout.setWidget(0, QFormLayout.LabelRole, self.edit_label)

        self.user_edit = QLineEdit(SimulationDialog)
        self.user_edit.setObjectName(u"user_edit")

        self.form_layout.setWidget(0, QFormLayout.FieldRole, self.user_edit)

        self.type_label = QLabel(SimulationDialog)
        self.type_label.setObjectName(u"type_label")

        self.form_layout.setWidget(1, QFormLayout.LabelRole, self.type_label)

        self.user_type = QComboBox(SimulationDialog)
        self.user_type.setObjectName(u"user_type")

        self.form_layout.setWidget(1, QFormLayout.FieldRole, self.user_type)


        self.verticalLayout.addLayout(self.form_layout)

        self.button_box = QDialogButtonBox(SimulationDialog)
        self.button_box.setObjectName(u"button_box")
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Help|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.button_box)


        self.retranslateUi(SimulationDialog)
        self.button_box.accepted.connect(SimulationDialog.accept)
        self.button_box.rejected.connect(SimulationDialog.reject)

        QMetaObject.connectSlotsByName(SimulationDialog)
    # setupUi

    def retranslateUi(self, SimulationDialog):
        SimulationDialog.setWindowTitle(QCoreApplication.translate("SimulationDialog", u"Dialog", None))
        self.edit_label.setText(QCoreApplication.translate("SimulationDialog", u"User editable text:", None))
        self.type_label.setText(QCoreApplication.translate("SimulationDialog", u"User selectable type:", None))
    # retranslateUi


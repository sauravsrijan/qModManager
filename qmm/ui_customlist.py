# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qmm/resources/list-view.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CustomList(object):
    def setupUi(self, CustomList):
        CustomList.setObjectName("CustomList")
        CustomList.setEnabled(True)
        CustomList.resize(448, 171)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CustomList.sizePolicy().hasHeightForWidth())
        CustomList.setSizePolicy(sizePolicy)
        CustomList.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLayout = QtWidgets.QVBoxLayout(CustomList)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.topBar = QtWidgets.QWidget(CustomList)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.topBar.sizePolicy().hasHeightForWidth())
        self.topBar.setSizePolicy(sizePolicy)
        self.topBar.setMinimumSize(QtCore.QSize(0, 28))
        self.topBar.setMaximumSize(QtCore.QSize(16777215, 28))
        self.topBar.setObjectName("topBar")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.topBar)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelWidget = QtWidgets.QLabel(self.topBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelWidget.sizePolicy().hasHeightForWidth())
        self.labelWidget.setSizePolicy(sizePolicy)
        self.labelWidget.setMaximumSize(QtCore.QSize(16777215, 28))
        self.labelWidget.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelWidget.setIndent(0)
        self.labelWidget.setObjectName("labelWidget")
        self.horizontalLayout.addWidget(self.labelWidget)
        self.plusButton = QtWidgets.QPushButton(self.topBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plusButton.sizePolicy().hasHeightForWidth())
        self.plusButton.setSizePolicy(sizePolicy)
        self.plusButton.setMaximumSize(QtCore.QSize(28, 28))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.plusButton.setFont(font)
        self.plusButton.setIconSize(QtCore.QSize(28, 28))
        self.plusButton.setFlat(True)
        self.plusButton.setObjectName("plusButton")
        self.horizontalLayout.addWidget(self.plusButton)
        spacerItem = QtWidgets.QSpacerItem(5, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.horizontalLayout.addItem(spacerItem)
        self.minusButton = QtWidgets.QPushButton(self.topBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.minusButton.sizePolicy().hasHeightForWidth())
        self.minusButton.setSizePolicy(sizePolicy)
        self.minusButton.setMaximumSize(QtCore.QSize(28, 28))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.minusButton.setFont(font)
        self.minusButton.setIconSize(QtCore.QSize(28, 28))
        self.minusButton.setFlat(True)
        self.minusButton.setObjectName("minusButton")
        self.horizontalLayout.addWidget(self.minusButton)
        self.verticalLayout.addWidget(self.topBar)
        self.listWidget = QtWidgets.QListWidget(CustomList)
        self.listWidget.setResizeMode(QtWidgets.QListView.Adjust)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)

        self.retranslateUi(CustomList)
        QtCore.QMetaObject.connectSlotsByName(CustomList)

    def retranslateUi(self, CustomList):
        _translate = QtCore.QCoreApplication.translate
        self.labelWidget.setText(_translate("CustomList", "Use the + or - button to add or remove items from the list"))
        self.plusButton.setText(_translate("CustomList", "+"))
        self.minusButton.setText(_translate("CustomList", "-"))
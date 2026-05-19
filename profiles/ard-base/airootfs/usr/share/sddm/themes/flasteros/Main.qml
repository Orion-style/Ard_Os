import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    color: "#101820"

    Image {
        anchors.fill: parent
        source: config.background
        fillMode: Image.PreserveAspectCrop
    }

    Rectangle {
        anchors.fill: parent
        color: "#101820"
        opacity: 0.22
    }

    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(parent.width - 80, 420)
        spacing: 18

        Image {
            source: config.logo
            Layout.alignment: Qt.AlignHCenter
            sourceSize.width: 92
            sourceSize.height: 92
        }

        Label {
            text: "FlasterOS"
            color: "#f4f8fb"
            font.pixelSize: 34
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        ComboBox {
            id: userBox
            model: userModel
            textRole: "name"
            Layout.fillWidth: true
        }

        TextField {
            id: password
            placeholderText: "Password"
            echoMode: TextInput.Password
            Layout.fillWidth: true
            focus: true
            Keys.onReturnPressed: sddm.login(userBox.currentText, password.text, session.index)
        }

        ComboBox {
            id: session
            model: sessionModel
            textRole: "name"
            Layout.fillWidth: true
        }

        Button {
            text: "Log In"
            Layout.fillWidth: true
            onClicked: sddm.login(userBox.currentText, password.text, session.index)
        }

        Label {
            text: sddm.hostName
            color: "#9fb2bd"
            Layout.alignment: Qt.AlignHCenter
        }
    }

    RowLayout {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 24
        spacing: 10
        Button { text: "Reboot"; onClicked: sddm.reboot() }
        Button { text: "Shutdown"; onClicked: sddm.powerOff() }
    }
}

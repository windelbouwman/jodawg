import QtQuick 2.0
import QtQuick.Controls 1.0
import QtQuick.Layouts 1.0

Rectangle {

  function sendMsg() {
    chatlog.say(tf_msg.text);
    tf_msg.text = '';
    // TODO: chatlog.onRowsInserted: 
    chatLogView.positionViewAtEnd();
  }


  Component {
    id: msgDelegate
    Item {
     height: childrenRect.height
     width: childrenRect.width

     Row {
       spacing: 5
       FancyText { color: "yellow"; text: cl_time; }
       FancyText { color: "green"; text: cl_name; }
       FancyText { color: "gray"; text: cl_msg; }
     }
    }
  }

  radius: 5
  color: "lightgray"

  ColumnLayout {
  anchors.fill: parent
  ListView {
    id: chatLogView
    Layout.fillHeight: true
    Layout.fillWidth: true
    model: chatlog
    delegate: msgDelegate
    clip: true
    spacing: 5
    anchors.margins: 5
    add: Transition {
      NumberAnimation { property: "scale"; from: 0; to: 1.0; duration: 200 }
    }
    displaced: Transition {
      NumberAnimation { property: "x"; duration: 400; easing.type: Easing.OutBounce }
    }
  }

  RowLayout {
    spacing: 5
    anchors.margins: 5
    TextField { 
        id: tf_msg
        onAccepted: sendMsg(); 
        focus: true
        Layout.fillWidth: true
    }

    Button {
     text: "Send"
     onClicked: sendMsg();
    }
   } 
   }
}



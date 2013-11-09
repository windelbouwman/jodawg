import QtQuick 2.0

Rectangle {
  property string text
  radius: 5 
  height: childrenRect.height
  width: childrenRect.width
  Text { 
    text: parent.text;
    anchors.margins: 15
  }
}


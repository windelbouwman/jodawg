import QtQuick 2.0
import QtQuick.Controls 1.0

Item {
  function sendMsg() {
    var txt = tf_msg.text;
    console.log(txt);
    tf_msg.text = '';
    chatlog.say("t2", txt);
    chatLogView.positionViewAtEnd()
  }
  width: 400
  height: 300
  ListModel {
    id: logX
    ListElement {
     name: 'aa'
     msg: 'hello'
    }
    ListElement {
     name: 'Hhkjfsd'
     msg: 'world'
    }
  }

  Component {
   id: msgDelegate
   Item {
     height: childrenRect.height + 5
     width: childrenRect.width + 20

     Row {
       spacing: 5
       Rectangle {
         anchors.margins: 5
         radius: 5; color: "green"
         height: childrenRect.height + 5
         width: childrenRect.width + 50
         Text {
           text: cl_name + cl_time
         }
       }
       Rectangle {
         anchors.margins: 5
         radius: 5; color: "gray"
         height: childrenRect.height + 15
         width: childrenRect.width + 50
        Text { 
          text: cl_msg
        }
       }
     }
   }
  }

  Column {
  anchors.fill: parent
  ListView {
    id: chatLogView
    height: 200
    width: parent.width
    model: chatlog
    delegate: msgDelegate
    clip: true
  }


  Row {
    TextField { id: tf_msg; onAccepted: sendMsg(); }

    Button {
     text: "Send"
     onClicked: sendMsg();
    }
   } 
  }
}



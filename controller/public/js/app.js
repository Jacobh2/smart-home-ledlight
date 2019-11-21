import { Header } from './header.js';
import { ColorCircle } from './colorpicker.js'
import { PresetsRow } from './presets.js'
import { Alarm } from './alarm.js'
// import { Snackbar } from './snackbar.js'

function hexToRgb(hex) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
  } : null;
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.setColorPicker = this.setColorPicker.bind(this);
    this.getColorCircle = this.getColorCircle.bind(this);

    this.addListener = this.addListener.bind(this);
    this.trigger = this.trigger.bind(this);

    this.state = {
      colorPicker: null,
      color: hexToRgb(props.initialColor),
      listeners: new Map()
    }

  }

  setColorPicker(colorPicker){
    this.setState({colorPicker: colorPicker});
  }

  getColorCircle(){
    return this.state.colorPicker;
  }

  addListener(what, who){
    var l = this.state.listeners;
    l.set(what, who);
    this.setState({
      listeners: l
    });
  }

  trigger(what, payload){
    var fn = this.state.listeners.get(what);
    if(fn !== undefined){
      fn(payload);
    }
  }

  render() {
    return React.createElement(
      "div",
      null,
      React.createElement(Header, {initialOnState: this.props.initialOnState, addListener: this.addListener, roomName:this.props.roomName}),
      React.createElement(ColorCircle, {setColorCircleFn: this.setColorPicker, initialOnState: this.props.initialOnState, color: this.props.initialColor, trigger: this.trigger, roomName: this.props.roomName}),
      React.createElement(PresetsRow, {getColorCircle: this.getColorCircle, roomName: this.props.roomName}),
      React.createElement(Alarm, {alarmTime: this.props.initialAlarm, roomName: this.props.roomName})
      // React.createElement(Snackbar, {
      //   visible: this.state.snackbarVisible,
      //   setVisibility: this.setVisibility
      // })
    );
  }
}


const mountRoot = document.getElementById('root');
ReactDOM.render(React.createElement(App, {initialColor: initialColor, initialOnState: initialOnState, initialAlarm: initialAlarm, roomName: roomName}), mountRoot);
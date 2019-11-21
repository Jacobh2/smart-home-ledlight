import { GoogleButtonIcon } from './iconbutton.js'
import { cancelAlarm, setAlarm } from './ledstripe.js'



export class Alarm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      alarmTime: props.alarmTime
    };
    this.handleTimeSet = this.handleTimeSet.bind(this);
    this.handleAlarmToggle = this.handleAlarmToggle.bind(this);
    this.timeIsSet = this.timeIsSet.bind(this);

    this.AlarmToggle = React.createElement(GoogleButtonIcon, {
      activated: this.state.alarmTime != null,
      size: "bigicon",
      activatedState: "alarm_on",
      deactivatedState: "alarm",
      togglefn: this.handleAlarmToggle,
      checkAllowedChangeFn: this.timeIsSet
    });
  }

  timeIsSet(){
    return this.state.alarmTime.length !== 0;
  }

  handleTimeSet(e){
    this.setState({alarmTime: e.target.value});
  }

  handleAlarmToggle(checked){
    if(checked){
      setAlarm(this.state.alarmTime, this.props.roomName);
    } else {
      cancelAlarm(this.props.roomName);
    }
  }

  render() {
    return React.createElement(
      "div",
      null,
      React.createElement("p", null, React.createElement("b", null, "Wakeup time")),
      React.createElement(
        "div",
        { className: "flex-container-row" },
        React.createElement("input", {
          className: "timeselector",
          type: "time",
          defaultValue: this.state.alarmTime,
          onChange: this.handleTimeSet
        }),
        this.AlarmToggle
      )
    );
  }
}

import { GoogleButtonIcon, updateActivateState, SimpleGoogleButtonIcon } from './iconbutton.js';
import { togglePower } from './ledstripe.js';


export class Header extends React.Component {
  constructor(props) {
    super(props);
    this.handleToggle = this.handleToggle.bind(this);
    this.onColorChange = this.onColorChange.bind(this);

    props.addListener("onColorChange", this.onColorChange);
    this.state = {activated: props.initialOnState};

    this.checkbox = React.createElement(GoogleButtonIcon, {
      activated: this.state.activated,
      size: "mediumicon",
      activatedState: "check_box",
      deactivatedState: "check_box_outline_blank",
      togglefn: this.handleToggle,
      checkAllowedChangeFn: () => true
    })

    this.backbutton = React.createElement(SimpleGoogleButtonIcon, {
      name: "arrow_back",
      size: "mediumicon",
      onClick: () => {
        console.log("W:", window);
        window.location.pathname = '/';
      },
    })
  }

  onColorChange(color){
    if(color.r + color.g + color.b === 0){
      updateActivateState(false);
    } else {
      updateActivateState(true);
    }
  }

  handleToggle(power){
    togglePower(power, this.props.roomName);
  }

  render() {
    return React.createElement(
      "div",
      { className: "flex-container-row" },
      this.backbutton,
      React.createElement(
        "h1",
        null,
        React.createElement("b", null, this.props.roomName)
      ),
      this.checkbox
    );
  }
}

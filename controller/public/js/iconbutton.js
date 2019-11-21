
export function updateActivateState(activated){
  this.setState({activated: activated})
}

export class GoogleButtonIcon extends React.Component {
  constructor(props) {
    super(props);
    console.log("Creating icon button", props.activatedState, "With activated:", props.activated);
    this.state = {
      activated: props.activated,
      toggleFunction: props.togglefn,
      class: "material-icons " + props.size + " flex-item",
      activatedState: props.activatedState,
      deactivatedState: props.deactivatedState,
      checkAllowedChangeFn: props.checkAllowedChangeFn
      // disregardFirstActivateUpdate: !props.activated
    };

    this.handleToggle = this.handleToggle.bind(this);
    updateActivateState = updateActivateState.bind(this);
  }

  handleToggle(e){
    if(this.state.checkAllowedChangeFn()){
      var checked = e.target.innerHTML !== this.state.activatedState;
      this.setState({
        activated: checked
      });
      this.state.toggleFunction(checked);
    } 
  }

  render() {
    if (this.state.activated) {
      console.log("Will render Activated");
      //Show the box checked
      return React.createElement("i",
        {
          className: this.state.class,
          onClick: this.handleToggle
        },
        this.state.activatedState
      );
    } else {
      console.log("Will render Deactivated");
      // Show the box unchecked
      return React.createElement("i",
        {
          className: this.state.class,
          onClick: this.handleToggle
        },
        this.state.deactivatedState
      );
    }
  }
}

export class SimpleGoogleButtonIcon extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      class: "material-icons " + props.size,
    };
  }

  render() {
    return React.createElement("i",
      {
        className: this.state.class,
        onClick: this.props.onClick
      },
      this.props.name
    )
  }
}

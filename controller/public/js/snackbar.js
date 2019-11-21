
export class Snackbar extends React.Component {
  constructor(props) {
    super(props);
    this.setVisibility = props.setVisibility
  }

  render() {
    if(this.props.visible){
      console.log("++++++++");
      const thi$ = this;
      setTimeout(function(){
        thi$.setVisibility(false);
      }, 3000);
      return React.createElement(
        "div",
        { id: "snackbar show" },
        "EXAMPLE TEXT SHOW"
      );
    }
    console.log("--------");
    return React.createElement(
      "div",
      { id: "snackbar" },
      "EXAMPLE TEXT HIDDEN"
    );
  }
}

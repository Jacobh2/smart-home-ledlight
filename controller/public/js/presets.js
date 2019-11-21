
var presetColors = {
  pink: {r: 255, g: 0, b: 15},
  red: {r: 255, g: 0, b: 0},
  sunset: {r: 255, g: 20, b: 0},
  warmWhite: {r: 255, g: 60, b: 20}
};


class Preset extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      active: false,
      color: props.color,
      name: props.name,
      getColorCircle: props.getColorCircle
    };
    this.handleColor = this.handleColor.bind(this);
  }

  handleColor(e){
    this.state.getColorCircle().color.set(this.state.color);
  }

  render() {
    return React.createElement("button",
      {
        className: "preset",
        onClick: this.handleColor
      },
      this.state.name
    );
  }
}

export class PresetsRow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      getColorCircle:props.getColorCircle
    }
  }

  renderPreset(name, color){
    return React.createElement(Preset, {
      color:color,
      name:name,
      getColorCircle:this.state.getColorCircle
    });
  }

  render() {
    return React.createElement(
      "div",
      { className: "preset-row top-padding" },
        this.renderPreset("Pink", presetColors.pink),
        this.renderPreset("Red", presetColors.red),
        this.renderPreset("Sunset", presetColors.sunset),
        this.renderPreset("Warm White", presetColors.warmWhite)
    );
  }
}

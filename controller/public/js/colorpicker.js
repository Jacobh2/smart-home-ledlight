import { setColor } from './ledstripe.js';


function loadColorCircle(callback){
  var script = document.createElement("script")
  script.type = "text/javascript";
  script.onload = function(){
      callback();
  };
  script.src = '/js/iro.min.js';
  document.getElementsByTagName("head")[0].appendChild(script);
}


function debounce(func, wait, immediate) {
  var timeout;
  return function() {
      var context = this, args = arguments;
      var later = function() {
          timeout = null;
          if (!immediate) func.apply(context, args);
      };
      var callNow = immediate && !timeout;
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
      if (callNow) func.apply(context, args);
  };
}

export class ColorCircle extends React.Component {
  constructor(props) {
    super(props);
    var thi$ = this;

    this.state = {
      loaded: false,
      skipFirstChange: !props.initialOnState
    };

    this.handleChange = this.handleChange.bind(this);

    loadColorCircle(() => {

      // Check if color is loaded!

      thi$.setState({loaded: true});

      thi$.colorPicker = new iro.ColorPicker("#color-picker-container", {
          markerRadius: 10,
          padding: 4,
          sliderMargin: 24,
          sliderHeight: 36,
          borderWidth: 5,
          borderColor: "#000",
          anticlockwise: true,
          color: thi$.props.color
      });
      thi$.colorPicker.on('color:change', debounce(thi$.handleChange, 20, false));
      thi$.props.setColorCircleFn(thi$.colorPicker);
    });
  }

  handleChange(color){
    if(this.state.skipFirstChange){
      this.setState({skipFirstChange: false});
    } else {
      console.log("Color change from wheel")

      // Toggle power to API
      setColor(color.rgb, this.props.roomName);
      //Tell the power button  - color.r, color.g, color.b
      this.props.trigger("onColorChange", color.rgb);

    }
  }

  render() {
    return React.createElement("div",
      {
        id: "color-picker-container"
      }
    );
  }
}

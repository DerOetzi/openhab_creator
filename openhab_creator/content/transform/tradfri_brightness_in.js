(function (x) {
    var tmp = JSON.parse(x);
    // The brightness value is received as integer 1-254 but needed as percentage
    var brightness = Math.round(tmp.brightness / 254 * 100);

    return tmp.color.x + ',' + tmp.color.y + ',' + brightness
})(input)
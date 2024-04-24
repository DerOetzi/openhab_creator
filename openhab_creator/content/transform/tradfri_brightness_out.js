(function (x) {
    var tmp = x.split(',');
    // The brightness value is received as percentage but needed as integer 1-254
    tmp[2] = tmp[2] * 2.54;

    return '{"color":{"x":"' + tmp[0] + '","y":"' + tmp[1] + '"},"brightness":"' + tmp[2] + '"}'
})(input)
function parseViewBoxString (string) {
  var list = string.split(' ').map(Number);
  return {
    x: list[0],
    y: list[1],
    width: list[2],
    height: list[3]
  };
}

function calcScaledRect (rect, scaleFactor) {
  return {
    x: Math.round(rect.x * scaleFactor),
    y: Math.round(rect.y * scaleFactor),
    width: Math.round(rect.width * scaleFactor),
    height: Math.round(rect.height * scaleFactor)
  };
}

function rectToViewBoxString (rect) {
  return [rect.x, rect.y, rect.width, rect.height].join(' ');
}

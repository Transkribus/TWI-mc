function Zoomable (rootNode, imageWidth, imageHeight, onZoomChange) {

  // var scrollNode = rootNode;
  var scrollNode = document.querySelector('.js-scrollable');
  var zoomNode = document.querySelector('.js-zoomable');
  // var zoomNode = rootNode.querySelector('.js-zoomable');
  // var viewNode = document.querySelector('.js-view');

  var zoomFactor = scrollNode.clientWidth / imageWidth;
  var initialZoomFactor = scrollNode.clientWidth / imageWidth;

  var ZOOM_DELTA = 0.075;

  var minZoomFactor = scrollNode.clientHeight / imageHeight;
  var maxZoomFactor = 3 * scrollNode.clientWidth / imageWidth;

  initialize();

  function initialize () {
    handleZoomChange();
    scrollNode.focus();
  }

  function handleZoomChange () {
    if (typeof onZoomChange === 'function')
      onZoomChange({type: 'zoomchange', detail: {factor: zoomFactor}});
  }

  function zoomWithAnchor (delta, clickX, clickY) {

    if (delta === 0)
      newZoomFactor = scrollNode.clientWidth / imageWidth; // initial zoom factor
    else
      newZoomFactor = sanitize(zoomFactor + delta * ZOOM_DELTA);

    var anchorX = clickX + scrollNode.scrollLeft;
    var anchorY = clickY + scrollNode.scrollTop;

    zoomNode.style.width = Math.round(imageWidth * newZoomFactor) + 'px';

    scrollNode.scrollLeft += (newZoomFactor - zoomFactor) * anchorX / zoomFactor;
    scrollNode.scrollTop += (newZoomFactor - zoomFactor) * anchorY / zoomFactor;

    zoomFactor = newZoomFactor;

    handleZoomChange();

  }

  function sanitize (x) {
    return Math.max(minZoomFactor, Math.min(maxZoomFactor, x));
  }

  var zoomThreshold = 0.05;

  return {
    zoomWithAnchor: function (delta, anchorX, anchorY) {
      zoomWithAnchor(delta, anchorX, anchorY);
    },
    zoom: function (delta) {
      zoomWithAnchor(delta, scrollNode.clientWidth / 2, scrollNode.clientHeight / 2);
    },
    isZoomed: function () {
      // Return: true if image is zoomed in / out
      return Math.abs(Math.floor(10 * (zoomFactor - scrollNode.clientWidth / imageWidth))) > 0;
    },
    mustZoom: function (rect) {
      var newZoomFactor = scrollNode.clientWidth / rect.width;
      // console.log('diff', zoomFactor - newZoomFactor);
      if (zoomFactor - newZoomFactor < 0)
        return true;

      if (zoomFactor - newZoomFactor < zoomThreshold)
        return false;

      return true;

    },
    zoomIntoView: function (rect) {
      // FIXME: zoomIntoViewIfNeeded, i.e. zoom only if required, otherwise just scroll element into view
      // FIXME: use max(rect.width, rect.height)

      // rect.width is 100% of viewport width
      var k = scrollNode.clientWidth / rect.width;
      console.log({
        zoomFactor: zoomFactor,
        newZoomFactor: k,
        delta: k - zoomFactor
      });
      zoomNode.style.width = Math.round(k * imageWidth) + 'px';

      scrollNode.scrollLeft = Math.round(k * rect.x);
      // scrollNode.scrollTop = Math.round(k * rect.y - 0.5 * scrollNode.clientHeight + 0.5 * k * rect.height);
      scrollNode.scrollTop = Math.round(k * (rect.y + rect.height / 2) - scrollNode.clientHeight / 2);

      zoomFactor = k;

      handleZoomChange();

    }
  };

}

Zoomable.IN = 1;
Zoomable.OUT = -1;
Zoomable.RESET = 0;

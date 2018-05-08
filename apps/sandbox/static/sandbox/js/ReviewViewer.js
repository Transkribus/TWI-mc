function ReviewViewer (imageUrl, pageRoot, onSelect, onFocus) {

  /* FIXTHIS: take into account ReadingOrder */
  /* FIXTHIS: make sure it works in browers other than firefox 59 */
  /* FIXTHIS: display some sort of counter */
  /* FIXTHIS: cannot zoom */
  /* FIXTHIS: try to access DOM less often */
  /* FIXTHIS: store and restore state */
  /* FEATURE: enable allow selecting multiple lines at once, e.g. shift, dblclick and drag mouse to last one, coloring the items in-between  */
  /* TODO: merge this with image viewer */

  var S = {
    Page: 'PcGts > Page',
    TextRegion: 'PcGts > Page > TextRegion',
    TextLine: 'PcGts > Page > TextRegion > TextLine',
    Coords: 'PcGts > Page > TextRegion > TextLine > Coords',
    Baseline: 'PcGts > Page > TextRegion > TextLine > Baseline',
    // 'Coords[points]': 'PcGts > Page > TextRegion > TextLine > Coords',
    // 'Baseline[points]': 'PcGts > Page > TextRegion > TextLine > Baseline[points]',
    // Test: 'X > Y > Z'
  };

  var errorList = [];

  for (var nodeName in S) {
    var s = S[nodeName];
    if (pageRoot.querySelector(s) === null) {
      errorList.push(nodeName);
    }
  }

  if (errorList.length > 0) {
    handleError("Invalid document! The following tags are missing: " + errorList.join(', '));
  }

  var svgNode = document.querySelector('svg');

  var imageNode = svgNode.querySelector('.js-image');

  var maskNode = svgNode.querySelector('.js-mask');
  var rectNode = svgNode.querySelector('.js-rect');
  var groupNode = svgNode.querySelector('.js-group');

  var lastPolygonNode;
  var firstPolygonNode;     

  initialize();

  function initialize () {

    var pageNode = pageRoot.querySelector('Page');

    var imageWidth = parseInt(pageNode.getAttribute('imageWidth'));
    var imageHeight = parseInt(pageNode.getAttribute('imageHeight'));

    svgNode.setAttribute('viewBox', [0, 0, imageWidth, imageHeight].join(' '));

    loadIMG(imageUrl, imageNode).catch(function (error) {
      console.error(error);
    });

    render(pageRoot);

  }

  function render (pageRoot) {

    var coordsList = Array.from(pageRoot.querySelectorAll('Page > TextRegion > TextLine > Coords'));

    for (var index = 0; index < coordsList.length; index++) {

      var coordsNode = coordsList[index];
      var node = buildPolygon(coordsNode);

      var lineId = coordsNode.parentNode.getAttribute('id');
      console.assert(typeof lineId === 'string' && lineId !== '', lineId);

      var tempNode = node.cloneNode(true);

      tempNode.setAttribute('id', 'mask-' + lineId);
      tempNode.classList.add('mask');

      maskNode.appendChild(tempNode);

      node.classList.add('polygon', 'js-polygon');
      node.setAttribute('id', lineId);
      node.setAttribute('tabindex', 1);
      node.setAttribute('vector-effect', 'non-scaling-stroke');
      node.addEventListener('click', handleClick, false);
      node.addEventListener('dblclick', handleClick, false);
      node.addEventListener('keydown', handleKeydown, false);
      node.addEventListener('focus', handleFocus, false);

      if (index === 0)
        firstPolygonNode = node;
      else if (index === coordsList.length - 1)
        lastPolygonNode = node;

      groupNode.appendChild(node);

    }

    svgNode.appendChild(groupNode);

    firstPolygonNode.focus();
  }

  function togglePolygonState (node) {

    var maskId = 'mask-' + node.getAttribute('id');
    var maskNode = document.querySelector('#' + maskId);
    var isDisabled = maskNode.classList.toggle('disabled');

    onSelect(node.getAttribute('id'), node.classList.toggle('disabled'));

  }

  function handleClick (evt) {
    evt.preventDefault();

    if (evt.cancelable)
      evt.stopPropagation();

    togglePolygonState(evt.target);

  }

  function handleKeydown (evt) {

    switch (evt.key) {
      case 'Enter':
      case 'ArrowDown':
      case 'ArrowRight':
        if (evt.target.nextElementSibling !== null)
          evt.target.nextElementSibling.focus();
        else
          firstPolygonNode.focus();
        evt.preventDefault();
        break;
      case 'ArrowUp':
      case 'ArrowLeft':
        if (evt.target.previousElementSibling !== null)
          evt.target.previousElementSibling.focus();
        else
          lastPolygonNode.focus();
        evt.preventDefault();
        break;
      case ' ':
        togglePolygonState(evt.target);
        evt.preventDefault();
        if (evt.cancelable)
          evt.stopPropagation();
        break;
    }
  }

  function handleFocus (evt) {
    onFocus(evt.target.getAttribute('id'));
  }

  return {
    render: function (newPageRoot) {

      while (groupNode.firstElementChild !== null)
        groupNode.removeChild(groupNode.firstElementChild);

      /* NOTE: keep first element (=mask rect) */
      while (maskNode.lastElementChild !== maskNode.firstElementChild)
        maskNode.removeChild(maskNode.lastElementChild);

      render(newPageRoot);
    }
  };
}

function buildPolygon (coordsNode) {

  var pointList = parsePointsAttribute(coordsNode.getAttribute('points'));
  var polygonNode = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');

  var pointString = pointList.map(function (p) {
    return p
    // return {x: toScale(p.x), y: toScale(p.y)};
  }).map(pointToString).join(' ');

  polygonNode.setAttribute('points', pointString);

  return polygonNode;

}

function handleError (message) {

  alert(message);

  throw new Error(message);

}

function renderWithTable (imageUrl, pageUrl) {
  /* FIXTHIS: maintain hierarchy when rendering */

  var rootNode = document.querySelector('main');
  var svgNode = rootNode.querySelector('.js-svg');
  var layoutNode = svgNode.querySelector('.js-layout');
  var imageNode = svgNode.querySelector('.js-image');

  initialize();

  function log (error) {
    console.error(error);
  }

  function initialize () {

    loadIMG(imageUrl, imageNode).then(function () {
      getXML(pageUrl).then(renderPageXML).then(function () {
        document.body.classList.remove('loading');

        if (getQueryParam('demo', parseInt) === 1) {
          imageNode.classList.toggle('hidden');
          // layoutNode.classList.toggle('hidden');
          ['TextRegion', 'TableRegion', 'TableCell', 'TextLine', 'Baseline'].forEach(function (nodeName) {
            var itemList = Array.from(layoutNode.querySelectorAll('.' + nodeName));
            itemList.forEach(function (node) {
              node.classList.toggle('hidden');
            });
          });
        }

      }).catch(log);
    }).catch(log);

  }

  var renderMethods = {
    TableRegion: renderFromCoords,
    TextRegion: renderFromCoords,
    TableCell: renderFromCoords,
    TextLine: renderFromCoords,
    Baseline: renderFromPoints,
  };

  function getRenderMethod (node) {
    var f = renderMethods[node.nodeName];
    if (typeof f === 'function')
      f(node);
  }

  function traverse (root, visit) {

    /* breadth-first iterator */

    var queue = [root];

    while (queue.length > 0) {

      var node = queue.shift();

      visit(node);

      var nodeList = Array.from(node.children);

      for (var index = 0; index < nodeList.length; index++) {
        queue.push(nodeList[index]);
      }

    }
  }

  function renderPageXML (pageXML) {

    var pageNode = pageXML.querySelector('Page');

    var imageWidth = parseInt(pageNode.getAttribute('imageWidth'));
    var imageHeight = parseInt(pageNode.getAttribute('imageHeight'));

    svgNode.setAttribute('viewBox', [0, 0, imageWidth, imageHeight].join(' '));

    traverse(pageXML, getRenderMethod)

  }

  function renderFromPoints (node) {
    
    var pointList = parsePointsAttribute(node.getAttribute('points'));     
    var polylineNode = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');

    polylineNode.classList.add(node.nodeName);

    var pointString = pointList.map(pointToString).join(' ');

    polylineNode.setAttribute('points', pointString);
    polylineNode.setAttribute('vector-effect', 'non-scaling-stroke');

    return layoutNode.appendChild(polylineNode);
  }

  function renderFromCoords (node) {

    var coordsNode = node.querySelector('Coords');
    var pointList = parsePointsAttribute(coordsNode.getAttribute('points'));

    var polygonNode = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');

    polygonNode.classList.add(node.nodeName);
    polygonNode.style.fill = randomRGBA(0.5);

    var pointString = pointList.map(pointToString).join(', ');

    polygonNode.setAttribute('points', pointString);
    polygonNode.setAttribute('vector-effect', 'non-scaling-stroke');

    return layoutNode.appendChild(polygonNode);

  }

  Array.from(document.querySelectorAll('button')).forEach(function (node) {
    node.addEventListener('click', handleClick);
  });

  function handleClick (evt) {
    evt.preventDefault();

    switch (evt.target.value) {
      case 'image':
        imageNode.classList.toggle('hidden');
        break;
      case 'layout':
        layoutNode.classList.toggle('hidden');
      case 'TextRegion':
      case 'TableRegion':
      case 'TableCell':
      case 'TextLine':
      case 'Baseline':
        var itemList = Array.from(layoutNode.querySelectorAll('.' + evt.target.value));
        itemList.forEach(function (node) {
          node.classList.toggle('hidden');
        });
        break;
      default:
        console.warn("Unhandled case", evt.target.value);
    }
  }

  function randInt (min, max) {
    return min + Math.round(Math.random() * (max - min));
  }

  function randomRGBA (opacity) {
    return 'rgba(' + [
      randInt(0, 255), randInt(0, 255), randInt(0, 255), randInt(0, 50) / 100
    ].join(',') + ')';
  }
}

// function removeEverything () {
//   var rootNode = document.querySelector('main');
//   var svgNode = rootNode.querySelector('.js-svg');
//   var layoutNode = svgNode.querySelector('.js-layout');
//   while (layoutNode.firstElementChild !== null)
//     layoutNode.removeChild(layoutNode.firstElementChild);
// }

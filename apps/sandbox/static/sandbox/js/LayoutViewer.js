function LayoutViewer (imageUrl, pageXML, callback) {

  /* FIXTHIS: should change focus element using arrow keys? */
  /* FIXTHIS: enable more interactivity */
  /* FIXTHIS: allow handling of focus event */
  /* TODO: work out color scheme */
  /* FIXTHIS: keep layout elements associated with page xml, e.g. get text when element is clicked */

  /* FIXTHIS: chrome does not scroll element into view when focused */

  var NAMESPACE = 'http://www.w3.org/2000/svg';

  var rootNode = document.querySelector('.js-layout-viewer');
  var svgNode = rootNode.querySelector('.js-svg');
  var layoutNode = svgNode.querySelector('.js-layout');
  var imageNode = svgNode.querySelector('.js-image');

  var zoom;

  var renderMethods = {
    Page: renderWithClassName,
    TableRegion: renderWithClassName,
    TextRegion: renderWithClassName,
    TextLine: renderWithClassName,
    TableCell: renderWithClassName,
    Coords: renderCoords,
    Baseline: renderBaseline,
  };

  initialize();

  function initialize () {

    renderImage(imageUrl);
    renderPageXML(pageXML);

    layoutNode.addEventListener('focus', callback, true);

    // if (getQueryParam('demo', parseInt) === 1) {
    //   imageNode.classList.toggle('hidden');
    //   // layoutNode.classList.toggle('hidden');
    //   ['TextRegion', 'TableRegion', 'TableCell', 'TextLine', 'Baseline'].forEach(function (nodeName) {
    //     var itemList = Array.from(layoutNode.querySelectorAll('.' + nodeName));
    //     itemList.forEach(function (node) {
    //       node.classList.toggle('hidden');
    //     });
    //   });
    // }

  }

  function renderImage (imageUrl) {
    imageNode.setAttribute('xlink:href', imageUrl);
  }

  function renderPageXML (pageXML) {

    var pageNode = pageXML.querySelector('Page');

    var imageWidth = parseInt(pageNode.getAttribute('imageWidth'));
    var imageHeight = parseInt(pageNode.getAttribute('imageHeight'));

    svgNode.setAttribute('viewBox', [0, 0, imageWidth, imageHeight].join(' '));

    traverse(pageXML, layoutNode, getRenderMethod)

    zoom = new Zoomable(rootNode, imageWidth, imageHeight);

    /* NOTE: enable scrolling using arrow keys */
    // document.documentElement.focus();
    document.body.focus();

  }

  function getRenderMethod (xmlNode, svgNode) {
    var f = renderMethods[xmlNode.nodeName];
    if (typeof f === 'function')
      f(xmlNode, svgNode);
  }

  function traverse (xml, svg) {

    /* breadth-first iterator */

    var queue = [[xml, svg]];

    var render;

    while (queue.length > 0) {

      var item = queue.shift();

      var xml = item[0];
      var svg = item[1];

      render = renderMethods[xml.nodeName];

      if (typeof render === 'function')
        svg = svg.appendChild(render(xml));

      var nodeList = Array.from(xml.children);
      for (var index = 0; index < nodeList.length; index++) {
        queue.push([nodeList[index], svg]);
      }

    }
  }

  function renderWithClassName (pageNode) {
    var groupNode = document.createElementNS(NAMESPACE, 'g');
    groupNode.classList.add(pageNode.nodeName);

    if (pageNode.nodeName !== 'Page')
      groupNode.setAttribute('id', pageNode.getAttribute('id'));

    return groupNode;
  }

  function renderCoords (coordsNode) {
    var pointList = parsePointsAttribute(coordsNode.getAttribute('points'));

    var polygonNode = document.createElementNS(NAMESPACE, 'polygon');

    polygonNode.classList.add(coordsNode.nodeName);
    polygonNode.style.fill = randomRGBA(0.5);

    var pointString = pointList.map(pointToString).join(', ');

    polygonNode.setAttribute('points', pointString);
    polygonNode.setAttribute('vector-effect', 'non-scaling-stroke');

    polygonNode.setAttribute('tabindex', 0);

    return polygonNode;

  }

  function renderBaseline (node) {
    
    var pointList = parsePointsAttribute(node.getAttribute('points'));     
    var polylineNode = document.createElementNS(NAMESPACE, 'polyline');

    polylineNode.classList.add(node.nodeName);

    var pointString = pointList.map(pointToString).join(' ');

    polylineNode.setAttribute('points', pointString);
    polylineNode.setAttribute('vector-effect', 'non-scaling-stroke');

    return polylineNode;
  }

  function randInt (min, max) {
    return min + Math.round(Math.random() * (max - min));
  }

  function randomRGBA (opacity) {
    return 'rgba(' + [
      randInt(0, 255), randInt(0, 255), randInt(0, 255), randInt(0, 25) / 100
    ].join(',') + ')';
  }

  return {
    /* TODO: element with focus as zoom anchor */
    zoom: function (delta) {
      zoom.zoom(delta);
    },
    toggle: function (className) {
      switch (className) {
        case 'image':
          imageNode.classList.toggle('hidden');
          break;
        case 'layout':
          layoutNode.classList.toggle('hidden');
          break;
        case 'TextRegion':
        case 'TableRegion':
        case 'TableCell':
        case 'TextLine':
        case 'Baseline':
          var nodeList = Array.from(layoutNode.querySelectorAll('.' + className));
          for (var index = 0; index < nodeList.length; index++) {
            nodeList[index].classList.toggle('hidden');
          }
          break;
        default:
          console.warn("Invalid value for 'className':", className);
          break;
      }
    }
  };
}

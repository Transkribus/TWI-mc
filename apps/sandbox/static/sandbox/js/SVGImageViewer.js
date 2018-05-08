function SVGImageViewer (imageUrl, pageXML, callback) {

  /* FIXME: bug when image height < window height, zoom out scrolls image down */

  /* FIXTHIS: should change focus element using arrow keys? */
  /* FIXTHIS: enable more interactivity */
  /* FIXTHIS: allow handling of focus event */

  /* TODO: work out color scheme */

  /* FIXTHIS: keep layout elements associated with page xml, e.g. get text when element is clicked */

  /* FIXTHIS: chrome does not scroll element into view when focused */

  var NAMESPACE = 'http://www.w3.org/2000/svg';

  var viewNode = document.querySelector('.js-image-viewer--svg');
  var svgNode = viewNode.querySelector('.js-svg');
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

  return {
    scrollIntoView: function (id) {
      var node = svgNode.querySelector('#' + id);
      console.assert(node !== null, id);
      viewNode.scrollIntoView({behavior: 'smooth', block: 'end'});
    },
    zoom: function (delta) {
      zoom.zoom(delta);
    },
    resize: function () {},
    highlight: function () {},
    zoomIntoView: function (id) {
      /* TODO: element with focus as zoom anchor */
      throw new Error("Not implemented");
    }
  };

  function initialize () {

    renderImage(imageUrl);
    renderPageXML(pageXML);

    layoutNode.addEventListener('focus', callback, true);

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

    zoom = new Zoomable(viewNode, imageWidth, imageHeight);

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
    var pointString = pointList.map(pointToString).join(', ');

    polygonNode.classList.add(coordsNode.nodeName);

    polygonNode.setAttribute('points', pointString);
    polygonNode.setAttribute('vector-effect', 'non-scaling-stroke');

    polygonNode.setAttribute('tabindex', 0);

    return polygonNode;

  }

  function renderBaseline (node) {
    
    var pointList = parsePointsAttribute(node.getAttribute('points'));     
    var polylineNode = document.createElementNS(NAMESPACE, 'polyline');
    var pointString = pointList.map(pointToString).join(' ');

    polylineNode.classList.add(node.nodeName);

    polylineNode.setAttribute('points', pointString);
    polylineNode.setAttribute('vector-effect', 'non-scaling-stroke');

    return polylineNode;
  }

}

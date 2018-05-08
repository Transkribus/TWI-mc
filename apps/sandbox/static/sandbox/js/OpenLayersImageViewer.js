function OpenLayersImageViewer (imageUrl, doc, onSelect) {

  // TODO >> ENHANCEMENT

  // TODO: onSelect(lineId): call when line is selected, see here https://openlayers.org/en/latest/examples/select-features.html
  // TODO: get axis orientation right for drawing features
  // TOOD: draw features for TextLine in page xml draw Coords and Baseline
  // TODO: method for highlighting a feature

  // ENHANCEMENT: keep user from panning image out of viewport

  var SELECTORS = {
    Page: 'PcGts > Page',
    TextRegion: 'PcGts > Page > TextRegion',
    TextLine: 'PcGts > Page > TextRegion > TextLine',
    Coords: 'PcGts > Page > TextRegion > TextLine > Coords',
    Baseline: 'PcGts > Page > TextRegion > TextLine > Baseline',
    // 'Coords[points]': 'PcGts > Page > TextRegion > TextLine > Coords',
    // 'Baseline[points]': 'PcGts > Page > TextRegion > TextLine > Baseline[points]',
    // Test: 'X > Y > Z'
  };

  var viewNode = document.querySelector('.js-image-viewer');

  console.assert(viewNode instanceof HTMLElement);

  var map;
  var view;
  var vector;
  var extent;
  var projection;

  // see note IMPORTANT below
  var renderMethods = {
    // Page: renderPage,
    // TableRegion: renderTableRegion,
    // TextRegion: renderTextRegion,
    TextLine: renderTextLine,
    // TableCell: renderTableCell,
    Coords: renderCoords,
    Baseline: renderBaseline,
  };

  initialize();

  return {
    resize: function (changes) {
      // TODO: top left point should stay as is?
      map.updateSize();

      view.setCenter([extent[2] / 2, extent[3] / 2 - changes.height * view.getZoom()]);

    },
    highlight: function (lineId) {
      // zoomIntoView
      // highlight line
    },
    zoomIntoView: function (lineId) {

      console.warn("zoomIntoView is not yet implemented")

      // TODO: get real values for line

      // var node = doc.querySelector('TextLine[id= yadda yadda

      var minX = 0;
      var minY = 0;
      var maxX = 0;
      var maxY = 0;

      // NOTE: view.fit expects an openlayers extent

      view.fit([minX, minY, maxX, maxY], {
        // nearest: true,
        // constrainResolution: true,
        // TODO: find suitable maxZoom when selected feature is very small
        maxZoom: 4,
        easing: ol.easeIn,
        duration: 250
      });

      // ENHANCEMENT: zoom / scroll only if required

    }
  };

  function initialize () {

    checkPageXML(doc);

    // TODO: get extent from page xml Page.imageWidth, Page.imageHeight
    // extent = ... 

    try {
      initializeImage(imageUrl, getImageExtent(doc));
      initializeFeatures(doc);
    }
    catch (e) {
      console.error(e);
    }

    addEventListeners();

  }

  function checkPageXML (doc) {
    var errorList = [];

    for (var nodeName in SELECTORS) {
      var s = SELECTORS[nodeName];
      if (doc.querySelector(s) === null) {
        errorList.push(nodeName);
      }
    }

    // NOTE: let's be picky about our documents while in development
    if (errorList.length > 0)
      throw new Error("There is a problem with this document!");
  }

  function getImageExtent (doc) {
    var pageNode = doc.querySelector('Page');

    console.assert(pageNode instanceof Element);

    var width = parseInt(pageNode.getAttribute('imageWidth'));
    var height = parseInt(pageNode.getAttribute('imageHeight'));

    console.assert([NaN, 0].indexOf(width) < 0);
    console.assert([NaN, 0].indexOf(height) < 0);

    // this the format for openlayers' extent
    return [0, 0, width, height];
  }

  var proj2;

  function initializeImage (imageUrl, imageExtent) {

    extent = imageExtent;

    projection = new ol.proj.Projection({
      code: 'image',
      units: 'pixels',
      extent: extent,       
      // NOTE: get axis orientation right .. does not work

      // it's just a hint for parsers ... https://gis.stackexchange.com/a/140186

      axisOrientation: 'neu',

      // axisOrientation: 'neu'
      //  axisOrientation: 'esu'
      // axisOrientation: 'neu'
      // axisOrientation: 'end'
      // axisOrientation: 'end'
    });

    proj2 = new ol.proj.Projection({
      code: 'x',
      units: 'pixels',
      extent: extent,       
      axisOrientation: 'esu'
    });

    // console.log(ol.proj.proj4.get());

    console.debug(projection.getAxisOrientation());
    console.debug(proj2.getAxisOrientation());

    ol.proj.addProjection(projection);
    ol.proj.addCoordinateTransforms(
      projection, proj2,
      function(coordinate) {
        return [coordinate[0] / Math.PI, -coordinate[1] / 10];
      },
      function(coordinate) {
        return [coordinate[0] / Math.PI, -coordinate[1] * 10];
      }
    );

    view = new ol.View({
      projection: projection,
      // projection: 'image',
      // projection: projection,
      // center: [0, extent[3]],
      center: ol.extent.getCenter(extent),
      zoom: 1,
      minZoom: 2,
      maxZoom: 6
    });

    // NOTE: could also use geojson format for creating features, e.g. page xml > geojson first

    // var geoJsonObject = {};

    vector = new ol.source.Vector({
      projection: proj2,
      // features: (new ol.format.GeoJSON()).readFeatures(geoJsonObject),
      style: function (feature) {

        // NOTE: this is how openlayers handle the styles of the geometric shapes, it calls this function to get styles for each redraw

        // TODO: style features according to state, e.g. selected

        return undefined;
      }
    });

    map = new ol.Map({
      layers: [
        new ol.layer.Image({
          source: new ol.source.ImageStatic({
            attributions: 'these are the attributions',
            url: imageUrl,
            // projection: 'image',
            projection: projection,
            imageExtent: extent
          })
        }),
        new ol.layer.Vector({
          source: vector,
          // renderMode: 'image'
        })
      ],
      target: viewNode,
      view: view,
      controls: [], // make controls disappear
      // renderer: 'webgl'
    });

  }

  function initializeFeatures (doc) {

    var extent = getImageExtent(doc);

    // get viewport
    console.log('viewport', map.getView().calculateExtent(map.getSize()));

    console.log('getZoom', view.getZoom());

    // the openlayers part of things

    vector.addFeature(new ol.Feature(new ol.geom.Circle([0, extent[3] - 0], 100)));
    vector.addFeature(new ol.Feature(new ol.geom.Polygon([
      [[0, extent[3] - 0], [1000, extent[3] - 1000], [3000, extent[3] - 0]]
    ])));

    var geom = new ol.geom.Polygon([
      [[0, extent[3] - 0], [1000, extent[3] - 1000], [4000, extent[3] - 0]]
    ]);

    vector.addFeature(new ol.Feature(geom));

    var feature = new ol.Feature({
      name: "My Feature",
      geometry: ol.geom.Polygon([
        [100, extent[3] - 100],
        [200, extent[3] - 200],
        [300, extent[3] - 300]
      ])
    });

    vector.addFeature(feature);

    // the page xml part of things

    var pageNode = pageXML.querySelector('Page');

    var nodeList = Array.from(pageNode.querySelectorAll('TextRegion > TextLine'));

    var lineMap = {
      lineId: 0
    }

    /* IMPORTANT:

       at this point, one might as well just querySelectorAll for
       TextLine and then create a feature for all of those which have
       a Coords and Baseline Element as child. this way both regular
       lines in TextRegion as well as TableCells can be handled (TableCell > TextLine)
       

       ENHANCEMENT: figure out if features in openlayers can have children, probably
       some kind of grouping is possible ..

       however, at a later stage when other layout elements are to be drawn as
       well similar to the svg rendering in LayoutViewer.js, traverse, getRenderMethod, renderXXX
       could be used. see below.

    */
             
    // traverse(pageNode, svgNode, getRenderMethod)

  }

  function addEventListeners() {
    // var mousePosition = new ol.control.MousePosition({
    //   coordinateFormat: ol.coordinate.createStringXY(2),
    //   projection: projection,
    //   target: document.getElementById('position'),
    //   undefinedHTML: '&nbsp;'
    // });
    // map.addControl(mousePosition);
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

  function getRenderMethod (xmlNode, svgNode) {
    var f = renderMethods[xmlNode.nodeName];
    if (typeof f === 'function')
      f(xmlNode, svgNode);
  }

  function renderTextLine (textLineNode) {
    throw Error("Not implemented");
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

}

function SVGImageViewer (onFocus, onZoomChange) {

  /* TODO: take into account reading order ... */

  /* NOTE: this viewer is built upon the premise that it might be nice
     having scrollbars. this might be true when viewing a document. however,
     when transcribing, the ability to animate scaling and translation
     might be more valuable. this viewer is not very suitable in such
     situations.
  */

  /*
    NOTE: usage is intended as follows: first, user sets the desired zoom
    level for the document. then scrollIntoView is used to show next
    line for transcription.
   */

  /* BUG: after zoom into view, zooming does not work (anchor not set?)
     similarly, resetting zoom does not take into account currently focused
     element. in this case, keep anchor point vertically in same location
  */

  /* FIXME: when zoom is increased / decreased for active region, make sure it is proberly visible */

  /* FIXME: use anchor with hash rather than groups for focus-able
     shapes, maybe this way chrome scrollIntoView hack can be gotten
     rid of
  */
  /* TODO: load image as data url, (response.type = 'blob');
  /* FIXME: limit max zoom in zoomIntoView */
  /* FIXME: should change focus element using arrow keys? */

  var NAMESPACE = 'http://www.w3.org/2000/svg';

  var viewNode = document.querySelector('.js-image-viewer--svg');
  var svgNode = viewNode.querySelector('.js-svg');
  var layoutNode = svgNode.querySelector('.js-layout');
  var imageNode = svgNode.querySelector('.js-image');

  // var focusNode = null;

  var doc;
  var img;

  var zoom;
  var drag;

  var renderMethods = {
    Page: renderWithClassName,
    TableRegion: renderWithClassName,
    TextRegion: renderWithClassName,
    TextLine: renderWithClassName,
    Word: renderWithClassName,
    // TextLine: renderTextLine,
    TableCell: renderWithClassName,
    Coords: renderCoords,
    Baseline: renderBaseline,
  };

  var CONST = {
    ACTIVE: 'highlighted'
  };

  var activeNode = null;

  return {
    // update: function (newDoc, newImg) {
    //   doc = newDoc;
    //   imageUrl = newImg
    // },
    render: function (newImg, newDoc) {
      img = newImg;
      doc = newDoc;
      return render(img, doc);
    },
    highlight: function (id) {

      var node = svgNode.getElementById(id);

      if (activeNode !== null && activeNode.classList.contains(CONST.ACTIVE))
        activeNode.classList.remove(CONST.ACTIVE);

      if (!node.classList.contains(CONST.ACTIVE))
        node.classList.add(CONST.ACTIVE);

      activeNode = node;
    },
    scrollIntoView: (function () {

      /* NOTE: in chrome coordsNode.scrollIntoView does not work, most
         likely because it is not a direct child of the scrollable element.
         therefore, a fake element is inserted and moved to where the
         polygon is located. this node is then used for scrollIntoView.
      */

      var fakeNode = document.createElement('div');
      fakeNode.setAttribute('id', 'fakeNode');
      fakeNode.style.position = 'absolute';
      fakeNode.style.zIndex = -999999;
      fakeNode.style.backgroundColor = 'transparent';

      viewNode.appendChild(fakeNode);

      // FIXME: update fake node when zoom changes ...

      return function (id) {

        var node = svgNode.getElementById(id);
        console.assert(node !== null, id);
        var coordsNode = node.querySelector('.Coords');
        console.assert(coordsNode !== null, id);

        // TODO: does the computation also work when there is another element above image-viewer

        // FIXME: probably not very efficient, can pre-compute?
        var rect = coordsNode.getBoundingClientRect();

        // FIXME: can use translate here too?
        fakeNode.style.width = rect.width + 'px';
        fakeNode.style.height = rect.height + 'px';

        // NOTE: bounding client rect is relative to scroll offfset
        fakeNode.style.top = viewNode.scrollTop + rect.y + 'px';
        fakeNode.style.left = viewNode.scrollLeft + rect.x + 'px';

        try {
          fakeNode.scrollIntoView({behavior: 'smooth', block: 'center'});
        }
        catch (e) {

          console.warn(e);

          try {
            fakeNode.scrollIntoView({behavior: 'smooth', block: 'start'});
          }
          catch (e) {

            console.warn(e);

            fakeNode.scrollIntoView(true);

          }
        }

      }
    }()),

    zoom: function (delta) {
      zoom.zoom(delta, viewNode.clientWith / 2, viewNode.clientHeight / 2);
    },
    resize: function () {},
    resetZoom: function () {

      if (!zoom.isZoomed())
        return;

      var pageNode = doc.querySelector('Page');
      var imageWidth = parseInt(pageNode.getAttribute('imageWidth'));

      var rect = {
        x: 0,
        width: imageWidth
      };

      if (activeNode !== null) {

        var node = doc.getElementById(activeNode.getAttribute('id'));
        var coordsNode = node.querySelector('Coords')
        console.assert(coordsNode !== null);

        var nodeRect = toRect(parsePointsAttribute(coordsNode.getAttribute('points')));

        rect.y = nodeRect.y;
        rect.height = nodeRect.height;

        // FIXME: maintain position relative to viewport
        zoom.zoomIntoView(rect);
      }
      else {
        var imageHeight = parseInt(pageNode.getAttribute('imageHeight'));
        // rect.y = 0;
        // rect.height = imageHeight;
        rect.y = imageHeight * viewNode.scrollTop / viewNode.scrollHeight;
        rect.height = imageWidth * viewNode.clientHeight / viewNode.scrollHeight;
      }

      zoom.zoomIntoView(rect);

    },
    zoomIn: function () {

      // FIXME: does not yet seem quite right

      if (activeNode !== null) {
        var rect = activeNode.getBoundingClientRect();
        zoom.zoomWithAnchor(+1, rect.x + rect.width / 2, rect.y + rect.height / 2);
      }
      else {
        zoom.zoom(+1);
      }

    },
    zoomOut: function () {
      if (activeNode !== null) {
        var rect = activeNode.getBoundingClientRect();
        zoom.zoomWithAnchor(-1, rect.x + rect.width / 2, rect.y + rect.height / 2);
      }
      else {
        zoom.zoom(-1);
      }

    },
    zoomIntoView: function (id) {

      var node = doc.getElementById(id);
      console.assert(node !== null);
      var coordsNode = node.querySelector('Coords')
      console.assert(coordsNode !== null);

      var rect = toRect(parsePointsAttribute(coordsNode.getAttribute('points')));

      // determine padding
      rect.x -= rect.height * 0.25;
      rect.width += 2 * 0.25 * rect.height;

      zoom.zoomIntoView(rect);

      // activeNode = node;

      // if (zoom.mustZoom(rect))
      //   zoom.zoomIntoView(rect);
      // else
      //   this.scrollIntoView(id);

    }
  };

  function initialize () {

    renderImage(imageUrl);
    renderPageXML(doc);

    // layoutNode.addEventListener('focus', onFocus, true);

  }

  function render (img, doc) {
    return Promise.all([
      renderImage(img.src),
      renderPageXML(doc)
    ]);
  }

  function renderImage (imageUrl) {
    return new Promise(function (resolve) {
      imageNode.onload = function (evt) {
        resolve(evt);
      };
      imageNode.setAttribute('xlink:href', imageUrl);
    });
  }

  function renderPageXML (doc) {

    return new Promise(function (resolve) {
      requestAnimationFrame(function () {
        // FIXME: might take > 30 ms
        var pageNode = doc.querySelector('Page');

        var imageWidth = parseInt(pageNode.getAttribute('imageWidth'));
        var imageHeight = parseInt(pageNode.getAttribute('imageHeight'));

        svgNode.setAttribute('viewBox', [0, 0, imageWidth, imageHeight].join(' '));

        traverse(doc, layoutNode, getRenderMethod)

        zoom = new Zoomable(viewNode, imageWidth, imageHeight, onZoomChange);
        drag = new Draggable(viewNode);

        resolve();

      });
    });
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


  function renderTextLine (textLineNode) {
    var anchorNode = document.createElementNS(NAMESPACE, 'a');

    var id = textLineNode.getAttribute('id');

    if (typeof id === 'string' && id !== '') {
      anchorNode.setAttribute('id', id);
      anchorNode.setAttribute('href', '#' + id + 'x');
    }

    anchorNode.classList.add(textLineNode.nodeName);

    return anchorNode;
  }

  function renderCoords (coordsNode) {

    var pointList = parsePointsAttribute(coordsNode.getAttribute('points'));
    var polygonNode = document.createElementNS(NAMESPACE, 'polygon');
    var pointString = pointList.map(pointToString).join(', ');

    polygonNode.classList.add(coordsNode.nodeName);

    polygonNode.setAttribute('points', pointString);
    polygonNode.setAttribute('vector-effect', 'non-scaling-stroke');

    polygonNode.setAttribute('tabindex', 0);

    polygonNode.addEventListener('focus', handleFocus, false);
    // polygonNode.addEventListener('blur', handleBlur, false);

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

  function handleFocus (evt) {

    var node = evt.currentTarget;

    // NOTE: highlight TextLine > Coords only
    if (!node.parentNode.classList.contains('TextLine')) {
      evt.preventDefault();
      return;
    }

    if (activeNode !== null && activeNode.classList.contains(CONST.ACTIVE)) {
      activeNode.classList.remove(CONST.ACTIVE);
    }

    // FIXME: pick parent for highlight if target is Coords
    if (node.classList.contains('Coords'))
      node = node.parentNode;
      

    // reset previous highlight ...
    if (node !== null && !node.classList.contains(CONST.ACTIVE))
      node.classList.add(CONST.ACTIVE);

    if (typeof onFocus === 'function')
      onFocus({
        type: 'imagetextlinefocus',
        target: node,
        detail: {
          id: node.getAttribute('id')
        }
      });

    activeNode = node;

  }

  function handleBlur (evt) {

    // if (evt.currentTarget.classList.contains('highlight'))
    //   evt.currentTarget.classList.remove('highlight');

    // console.log(evt.type, evt);
  }

}

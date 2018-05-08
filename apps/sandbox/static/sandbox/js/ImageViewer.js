function ImageViewer (imageUrl, pageXML, callback) {

  /* FIXTHIS: find more suitable place for this ... */

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
    if (pageXML.querySelector(s) === null) {
      errorList.push(nodeName);
    }
  }

  if (errorList.length > 0) {
    Dialog.getInstance().then(function (dialog) {
      dialog.handleError("Invalid document! The following tags are missing: " + errorList.join(', '));
    });
  }

  var viewNode = document.querySelector('.js-image-viewer');
  var svgNode = viewNode.querySelector('svg');

  var lineList = Array.from(pageXML.querySelectorAll('Page > TextRegion > TextLine'));
  var layoutNode = svgNode.querySelector('.js-layout');

  var focusNode = null;

  var nodeList = [];

  initialize();

  function initialize () {
    /* FIXTHIS: group node disables default focus behavior ... */

    /* Render all the things ... */

    for (var index = 0; index < lineList.length; index++) {

      var lineNode = lineList[index];

      var groupNode = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      groupNode.classList.add('TextLine');
      groupNode.setAttribute('id', lineNode.getAttribute('id'));

      if ([null, ''].indexOf(lineNode.getAttribute('id')) >= 0)
        throw new Error("TextLine missing attribute 'id'");

      var coordsNode = lineNode.querySelector(':scope > Coords');

      /* build coords */

      var pointsList = parsePointsAttribute(coordsNode.getAttribute('points'));
      var node = buildNode('polygon', pointsList);
      node.classList.add('Coords', 'js-coords');
      // https://www.w3.org/TR/SVGTiny12/painting.html#NonScalingStroke
      node.setAttribute('vector-effect', 'non-scaling-stroke');

      /* NOTE: in a perfect world, <g> would play this role, however
         firefox 59 does not handle scrollIntoView functionality
         correctly for group
      */
      node.setAttribute('tabindex', 1);

      node.addEventListener('click', handleClick, false);
      node.addEventListener('dblclick', handleClick, false);
      node.addEventListener('keydown', handleKeydown, false);
      node.addEventListener('focus', handleFocus, false);

      nodeList.push(node);

      // node.setAttribute('tabindex', 1);

      groupNode.appendChild(node);

      var baselineNode = lineNode.querySelector(':scope > Baseline');
      var pointsList = parsePointsAttribute(baselineNode.getAttribute('points'));

      node = buildNode('polyline', pointsList);

      node.classList.add('Baseline', 'js-baseline');
      node.setAttribute('vector-effect', 'non-scaling-stroke');

      groupNode.appendChild(node);

      layoutNode.appendChild(groupNode);
      // svgNode.appendChild(groupNode);

    }

    layoutNode.firstElementChild.focus();

  }

  function handleClick (evt) {
    evt.preventDefault();

    if (evt.cancelable)
      evt.stopPropagation();

    // handleFocus(evt.currentTarget);
  }

  function handleKeydown (evt) {
    /* FIXTHIS: re-use ... same handler as for text viewer ... */

    var index = nodeList.indexOf(evt.target);

    var node = null;

    switch (evt.key) {
      case 'Enter':
      case 'ArrowDown':
      case 'ArrowRight':
        var node = nodeList[index + 1] || nodeList[0];
        node.focus();
        evt.preventDefault();
        break;
      case 'ArrowUp':
      case 'ArrowLeft':
        var node = nodeList[index - 1] || nodeList[nodeList.length - 1];
        node.focus();
        evt.preventDefault();
        break;
      case ' ':
        /* put some possible action here ... */
        evt.preventDefault();
        if (evt.cancelable)
          evt.stopPropagation();
        break;
    }

    /* FIXTHIS: keypress results in setting scrollTop to 0*/

  }

  function handleFocus (evt) {

    var node = evt.target.parentNode;

    console.assert(node.nodeName === 'g', node.nodeName);

    // scrollIntoView(viewNode, node);

    if (typeof callback === 'function')
      callback(node.getAttribute('id'), node);
  }

  function scrollIntoView (scrollNode, node) {
    /*

      scrollNode: scrollable ancestor
      node: node to be scrolled into view.

      - use transparent dom elements in html DOM for this

      - somehow make immedate ancestor, e.g. the layout group scrollable

    */

    /* NOTE: these calls have side effcts ! */
    // var rect = node.getBoundingClientRect();
    // var scrollRect = scrollNode.getBoundingClientRect();

    console.warn("srollIntoView is not implemented!");

    /* TODO: implement scrollIntoView method

       behavior: pretty much standard behavior as in any text editor or textarea with a scrollbar
       
        - if element is wholly in view: do nothing

        - otherwise scroll ancestor by mininum amount to get node into view

    */

    /* check if in view, if so do nothing */

    /* otherwise scroll by min amount up or down */

  }

  function buildNode (nodeName, pointList) {

    console.assert(nodeName === 'polygon' || nodeName === 'polyline');

    var node = document.createElementNS('http://www.w3.org/2000/svg', nodeName);

    var pointString = pointList.map(pointToString).join(' ');

    node.setAttribute('points', pointString);

    return node;

  }

  /* NOTE: save and restore focus when when switching text editor */
  viewNode.addEventListener('mouseleave', function (evt) {

    focusNode = document.activeElement;

    if (focusNode !== null && focusNode.classList.contains('TextLine'))
      if (!focusNode.classList.contains('selected'))
        focusNode.classList.add('selected');

  }, false);

  viewNode.addEventListener('mouseenter', function (evt) {

    if (focusNode !== null) {
      if (focusNode.classList.contains('selected'))
        focusNode.classList.remove('selected');

      focusNode.focus();
    }

  }, false);

  return {
    scrollIntoView: function (id) {
      var node = viewNode.querySelector('#' + id);
      console.assert(node !== null, id);
      // node.firstElementChild.scrollIntoView(false);
      node.firstElementChild.scrollIntoView({behavior: 'smooth', block: 'end'});
      /* highlight the node ... */
    }
  };

}

function Layout (params, onChange) {

  params = params || {}

  // TODO: use percentages for width, height, see https://jsfiddle.net/68p4nk15/2/

  // TODO: turn layout into template, block image, block text, e.g. layout extends base and has {% block image %}, {% block text %}, app.html extens layout.html

  // TODO: put handle in second item so it is not covered by scrollbar
  // TODO: make horizontal layout resizeable via mouse too
  // TODO: ensure flexbox cross-browser compatibility
  // TODO: persist layout somehow
  // TODO: test what happens when there is also an element to the right of the layout container and the resize handle is dragged there
  // TODO: make resizing available on touch devices?

  var layoutNode = document.querySelector('.js-layout');
  var handleNode = layoutNode.querySelector('.js-handle');

  var items = Array.from(layoutNode.children);

  var layout = {
    isHorizontal: params.isHorizontal == undefined ? false : params.isHorizontal,
    isReversed: params.isReversed === undefined ? false : params.isReversed,
    width: params.width === undefined ? null : params.width,
    height: params.height === undefined ? null : params.height
  };

  var itemNode = document.querySelector('.item:first-child');

  var isDragging = false;

  var startX;
  var startY;

  var isReady = true

  handleNode.addEventListener('mousedown', startDrag, false);
  document.addEventListener('mousemove', drag, false);
  document.addEventListener('mouseup', stopDrag, false);

  handleChange(layout);

  return {
    setExtent: function (index, extent) {

      // NOTE: this is untested
      // TODO: check if this is still required ...

      console.warn("Layout.setExtent has not been tested");

      console.assert(typeof index === 'number' && index < items.length);
      console.assert(typeof extent === 'number');

      var extent;

      // always apply width / height to first item
      if (index === 1) {
        index = 0;
        var totalExtent = layout.isHorizontal ? layoutNode.clientHeight : layoutNode.clientWidth;
        extent = totalExtent - extent;
      }

      if (layout.isHorizontal)
        handleChange({height: extent});
      else
        handleChange({width: extent});

    },
    update: function (layout) {
      layout = layout || {};
      console.assert('isHorizontal' in layout || 'isReversed' in layout || 'width' in layout || 'height' in layout);
      handleChange(layout);
    }
  }

  function handleChange (changes) {


    var delta = {};

    // update model
    for (var key in changes) {

      // delta
      if (layout[key] !== changes[key]) {
        if ('width' in changes)
          delta.width = changes.width - (layout.width === null ? layoutNode.offsetWidth / 2 : layout.width);
        else if ('height' in changes)
          delta.height = changes.height - (layout.height === null ? layoutNode.offsetHeight / 2 : layout.height);
        else if ('isHorizontal')
          delta.isHorizontal = changes.isHorizontal;
      }

      layout[key] = changes[key];
    }

    // update view
    if ('width' in changes || 'height' in changes || 'isHorizontal' in changes) {

      var extent = layout.isHorizontal ? layout.height : layout.width;

      if (extent === null) { // not yet defined, default to 50 / 50 split
        itemNode.style['-webkit-flex'] = '1';
        itemNode.style.flex = '1';
      }
      else {
        itemNode.style['-webkit-flex'] = 'none';
        itemNode.style.flex = 'none';
        itemNode.style['-webkit-flex-basis'] = extent + 'px';
        itemNode.style.flexBasis = extent + 'px';
      }
    }

    if ('isHorizontal' in changes || 'isReversed' in changes) {
      var classList = ['layout'];

      if (layout.isHorizontal === true)
        classList.push('horizontal');
      else
        classList.push('vertical');

      if (layout.isReversed)
        classList.push('reversed')

      layoutNode.className = classList.join(' ');
    }

    // notify master
    if (typeof onChange === 'function')
      // event similar to CustomEvent

      onChange({
        type: 'layoutchange',
        target: layoutNode,
        // immutable
        detail: {
          width: layout.width,
          height: layout.height,
          isHorizontal: layout.isHorizontal,
          isReversed: layout.isReversed,
          delta: delta
        }
      });
  }

  function startDrag (evt) {

    evt.preventDefault();

    if (evt.cancelable)
      evt.stopPropagation();

    startX = evt.clientX;
    startY = evt.clientY;

    handleNode.classList.add('dragging');

    isDragging = true;

  }

  function drag (evt) {
    if (!isDragging)
      return;

    if (!isReady)
      return;

    evt.preventDefault();

    if (evt.cancelable)
      evt.stopPropagation();

    var deltaX = evt.clientX - startX;
    var deltaY = evt.clientY - startY;

    isReady = false;

    requestAnimationFrame(function () {
      if (!isDragging) { // NOTE: stopped dragging already
        isReady = true;
	return;
      }	
      if (layout.isHorizontal) {
  	handleNode.style.transform = 'translate(0,' + deltaY + 'px)';
      }
      else {
  	handleNode.style.transform = 'translate(' + deltaX + 'px,0)';
      }

      isReady = true;

    });

  }

  function stopDrag (evt) {

    if (!isDragging)
      return;

    evt.preventDefault();


    // NOTE: handle isReversed correctly, because now the other item is being resized ...
    var c = layout.isReversed ? -1 : 1;
    var deltaX = c * (evt.clientX - startX);
    var deltaY = c * (evt.clientY - startY);

    if (layout.isHorizontal) {

      var height = Math.min(layoutNode.offsetHeight, Math.max(handleNode.offsetHeight, itemNode.offsetHeight + deltaY));

      handleNode.style.transform = '';
      handleNode.classList.remove('dragging');

      handleChange({height: height});

    }
    else {

      var width = Math.min(layoutNode.offsetWidth, Math.max(handleNode.offsetWidth, itemNode.offsetWidth + deltaX));

      // itemNode.style.flex = '0';
      // itemNode.style.flexBasis = width + 'px';

      handleNode.style.transform = '';
      handleNode.classList.remove('dragging');

      handleChange({width: width});

    }

    isDragging = false;
  }

}

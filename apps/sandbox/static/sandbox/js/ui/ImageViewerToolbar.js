function ImageViewerToolbar (methods) {

  console.assert(methods instanceof Object);

  var rootNode = document.querySelector('.js-image-viewer-toolbar');
  var formNode = rootNode.querySelector('.js-form');

  formNode.addEventListener('submit', function (evt) {
    evt.preventDefault();
  }, false);

  Array.from(formNode.children).forEach(function (node) {
    node.addEventListener('click', handleClick, false);
  });

  function handleClick (evt) {

    evt.preventDefault();

    var method = methods[evt.target.name];

    console.assert(typeof method === 'function');

    if (typeof method === 'function')
      method(evt.target.value);
    else {
      console.warn("Invalid name:", evt.target.name);
    }

    // NOTE: set focus on body so arrow keys can perform scroll
    document.body.focus();

  }

  return {
    setZoomFactor: function (x) {
      var node = formNode.querySelector('.js-zoom-factor');
      node.textContent = x + '%';
    }
  }

}

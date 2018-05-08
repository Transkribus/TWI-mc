function TaggingEditor (pageDoc, onSomeCallback, onSomeOtherCallback) {

  var scopeNode = document.querySelector('.js-tagging-editor');
  var tmplNode = scopeNode.querySelector('.js-templates');
  var helloTmpl = tmplNode.querySelector('.js-hello');

  var pageRoot = pageDoc.documentElement;

  console.assert(pageDoc instanceof Document);
  console.assert(pageRoot.nodeName === 'PcGts');

  initialize();

  function initialize () {
    if (typeof onSomeCallback === 'function')
      onSomeCallback();
  }

  function renderHelloWorld () {
    var node = helloTmpl.cloneNode(true);
    scopeNode.appendChild(node);
  }

  return {
    render: function () {

      renderHelloWorld();

      if (typeof onSomeOtherCallback === 'function')
        onSomeOtherCallback();

    }
  };
}

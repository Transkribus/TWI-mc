function TextViewer (pageXML, callback) {

  /* FIXTHIS: highlight active elements */

  var SELECTOR = 'PcGts > Page > TextRegion > TextLine';

  var viewNode = document.querySelector('.js-text-viewer');

  var inputNodes = [];

  initialize();

  function initialize () {

    var lineList = Array.from(pageXML.querySelectorAll(SELECTOR));

    var itemTmpl = document.createElement('div');
    itemTmpl.classList.add('TextLine');
    itemTmpl.appendChild(document.createElement('div'));
    itemTmpl.firstElementChild.classList.add('TextEquiv');

    for (var index = 0; index < lineList.length; index++) {
      var lineNode = lineList[index];
      var unicodeNode = lineNode.querySelector('TextEquiv > Unicode');

      var itemNode = itemTmpl.cloneNode(true);

      var textNode = document.createElement('input');
      textNode.classList.add('Unicode');

      //textNode.setAttribute('id', lineNode.getAttribute('id'));
      /* NOTE: id is already used by image viewer */
      textNode.setAttribute('name', lineNode.getAttribute('id'));
      textNode.setAttribute('type', 'text');
      textNode.addEventListener('change', handleChange, false);
      textNode.addEventListener('keypress', handleKeypress, false);
      textNode.addEventListener('focus', handleFocus, false);
      textNode.value = unicodeNode.textContent;

      inputNodes.push(textNode);

      itemNode.firstElementChild.appendChild(textNode);

      viewNode.appendChild(itemNode);

    }
  }

  function handleFocus (evt) {
    if (typeof callback === 'function')
      callback(evt.target.getAttribute('name'), evt.target);
  }

  function handleChange (evt) {}

  function handleKeypress (evt) {

    var index = inputNodes.indexOf(evt.target);

    if (index < 0)
      throw new Error(":/");

    switch (evt.key) {
      case 'ArrowDown':
      case 'Enter':
        var node = inputNodes[index + 1] || inputNodes[0];
        node.focus();
        break;
      case 'ArrowUp':
        var node = inputNodes[index - 1] || inputNodes[inputNodes.length - 1];
        node.focus();
        break;
    }        
  }

  return {
    scrollIntoView: function (id) {
      /* also highlight the thing ... */
      var node = viewNode.querySelector('.Unicode[name=' + id + ']')
      console.assert(node !== null);
      // node.scrollIntoView(false);
      node.scrollIntoView({behavior: 'smooth'});
    }
  };

}

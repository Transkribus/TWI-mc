function PlainTextEditor (onLineChange) {

  // TODO: maybe also take text region into account?

  var KEYS = [
    'Enter' ,'Backspace',
    'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight',
  ];

  var viewNode = document.querySelector('.js-plain-text-editor');
  var listNode = viewNode.querySelector('.js-list');

  var tmplNode = viewNode.querySelector('.js-templates');
  var itemTmpl = tmplNode.querySelector('.js-item');

  var nodeList = [];

  var textLineList = [];

  var hiliteNode = null;

  listNode.addEventListener('keydown', handleKeydown, false);
  listNode.addEventListener('input', handleInput, false);

  return {
    highlight: function (index) {

      // FIXME: highlight does not get stuck, e.g. update on focus

      if (hiliteNode !== null)
        hiliteNode.classList.remove('highlighted');

      hiliteNode = nodeList[index];

      hiliteNode.classList.add('highlighted');
      
    },
    select: function (index) {
      if (index > 0 && index < nodeList.length) {
        var inputNode = nodeList[index].firstElementChild;
        inputNode.setSelectionRange(0, 0);
        inputNode.focus();
      }
    },
    focus: function () {
      if (nodeList.length > 0) {
        var inputNode = nodeList[0].firstElementChild;
        inputNode.setSelectionRange(0, 0);
        inputNode.focus();
      }
    },
    getResult: function () {
      var results = [];
      for (var index = 0; index < nodeList.length; index++) {
        results.push(nodeList[index].firstElementChild.value);
      }
      return results;
    },
    update: function (newTextLineList) {
      console.assert(newTextLineList instanceof Array);
      textLineList.length = 0;
      textLineList.push.apply(textLineList, newTextLineList);
    },
    render: function () {
      // return new Promise(function (resolve) {

        if (nodeList.length > 0) {
          for (var index = 0; index < nodeList.length; index++)
            listNode.removeChild(nodeList[index]);
          nodeList.length = 0;
        }

        for (var index = 0; index < textLineList.length; index++) {
          var node = itemTmpl.cloneNode(true);
          var inputNode = node.firstElementChild;
          inputNode.value = textLineList[index];
          nodeList.push(listNode.appendChild(node));
        }
      // });
    }
  };

  function handleInput (evt) {

    var index = nodeList.indexOf(evt.target.parentNode);

    if (index < 0)
      return;

    textLineList[index] = evt.target.value;

  }

  function handleKeydown (evt) {

    if (KEYS.indexOf(evt.key) < 0)
      return;

    var node = evt.target.parentNode;
    var inputNode = node.firstElementChild;

    var index = nodeList.indexOf(node);

    if (index < 0)
      return;

    var deltaY;
    var offsetX = 0;

    switch (evt.key) {

      case 'Enter':
        deltaY = 1;
        offsetX = 0;
        break;

      case 'Backspace':

        if (inputNode.selectionStart > 0)
          return;

        // allow to delete selected text at beginning of line
        if (Math.abs(inputNode.selectionStart - inputNode.selectionEnd) > 0)
          return;

        deltaY = -1;
        offsetX = Infinity;

        break;

      case 'ArrowUp':
        deltaY = -1;
        offsetX = inputNode.selectionStart;
        break;

      case 'ArrowDown':
        deltaY = 1;
        offsetX = inputNode.selectionStart;
        break;

      case 'ArrowLeft':
        if (inputNode.selectionStart > 0)
          return;

        deltaY = -1;
        offsetX = Infinity;

        break;

      case 'ArrowRight':
        if (inputNode.selectionEnd < textLineList[index].length)
          return;

        deltaY = 1;
        offsetX = 0;

        break;
    }

    evt.preventDefault();

    // update data

    var nextIndex = sanitize(index + deltaY);

    if (nextIndex !== index && typeof onLineChange === 'function')
      onLineChange({
        type: 'linechange',
        detail: {newLine: nextIndex, oldLine: index}
      });

    index = nextIndex;

    // update ui

    inputNode = nodeList[index].firstElementChild;
    inputNode.focus();

    if (offsetX === Infinity) {
      offsetX = textLineList[index].length;
    }
    else
      offsetX = Math.min(offsetX, textLineList[index].length);

    inputNode.setSelectionRange(offsetX, offsetX);

  }

  function sanitize (index) {
    if (index < 0)
      index = textLineList.length - 1;
    else if (index > textLineList.length - 1)
      index = 0;
    return index;
  }

  function reset () {
    while (listNode.firstChild !== null)
      listNode.removeChild(listNode.firstChild);
  }

}

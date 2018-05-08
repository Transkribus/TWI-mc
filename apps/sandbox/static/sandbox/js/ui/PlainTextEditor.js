function PlainTextEditor (onLineChange) {

  // TODO: maybe also take text region into account?
  // TODO: render table as table

  // FIXME: for right-to-left writing direction, arrow keys are disabled 

  var CONST = {
    ACTIVE: 'highlighted'
  };

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

  var activeNode = null;

  var isRTL = false;

  listNode.addEventListener('keydown', handleKeydown, false);
  listNode.addEventListener('input', handleInput, false);

  return {
    scrollIntoView: function (index) {
      var node = nodeList[index];
      node.scrollIntoView({behavior: 'smooth', block: 'center'});
    },
    highlight: function (index) {

      // FIXME: highlight does not get stuck, e.g. update on focus

      if (activeNode !== null)
        activeNode.classList.remove(CONST.ACTIVE);

      activeNode = nodeList[index];

      activeNode.classList.add(CONST.ACTIVE);
      
    },
    select: function (nextIndex) {

      if (nextIndex < 0)
        return;

      if (nextIndex >= nodeList.length)
        return;
      
      var inputNode = nodeList[nextIndex].firstElementChild;

      inputNode.setSelectionRange(0, 0);
      inputNode.focus();

      handleLineChange({newIndex: nextIndex, oldIndex: null});

    },
    focus: function () {
      if (nodeList.length > 0) {

        var inputNode;

        if (activeNode === null)
          activeNode = nodeList[0];

        inputNode = activeNode.firstElementChild;

        // inputNode.focus();

        // inputNode.setSelectionRange(0, 0);

      }
    },
    insertText: function (string) {

      if (activeNode === null)
        throw new Error("NotImplementedError");

      var inputNode = activeNode.firstElementChild;

      var text = inputNode.value;

      var startIndex = inputNode.selectionStart;
      var stopIndex = inputNode.selectionEnd;

      if (stopIndex < startIndex) {
        var tempIndex = startIndex;
        startIndex = stopIndex;
        stopIndex = tempIndex;
      }
        
      var caretIndex = startIndex + string.length;

      inputNode.value = [
        text.slice(0, startIndex),
        string,
        text.slice(stopIndex)
      ].join('');

      // NOTE: update string in textLineList
      textLineList[nodeList.indexOf(activeNode)] = inputNode.value;

      inputNode.setSelectionRange(startIndex + string.length, startIndex + string.length);

      inputNode.focus();

    },
    render: function () {
      return new Promise(function (resolve) {

        if (nodeList.length > 0) {
          for (var index = 0; index < nodeList.length; index++)
            listNode.removeChild(nodeList[index]);
          nodeList.length = 0;
        }

        for (var index = 0; index < textLineList.length; index++) {

          var node = itemTmpl.cloneNode(true);
          var inputNode = node.firstElementChild;

          inputNode.value = textLineList[index];

          inputNode.addEventListener('focus', handleFocus, false);

          nodeList.push(listNode.appendChild(node));
        }

        resolve();

      });
    },
    setWritingDirection: function (direction) {
      if (direction === 'right-to-left') {
        viewNode.setAttribute('dir', 'rtl');
        isRTL = true;
      }
      else if (direction === 'left-to-right') {
        viewNode.setAttribute('dir', 'ltr');        
        isRTL = false;
      }
      else {
        console.error(Error("Invalid value for direction: " + direction));
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

        // FIXME: enable key navigation for RTL scripts
        if (isRTL)
          return;

        if (inputNode.selectionStart > 0)
          return;

        // allow to delete selected text at beginning of line
        if (Math.abs(inputNode.selectionStart - inputNode.selectionEnd) > 0)
          return;

        deltaY = -1;
        offsetX = Infinity;

        break;

      case 'ArrowUp':
      case 'Up':

        deltaY = -1;
        if (inputNode.selectionStart < textLineList[index].length)
          offsetX = inputNode.selectionStart;
        else
          offsetX = Infinity;
        break;

      case 'ArrowDown':
      case 'Down':
        deltaY = 1;
        if (inputNode.selectionStart < textLineList[index].length)
          offsetX = inputNode.selectionStart;
        else
          offsetX = Infinity;
        break;

      case 'ArrowLeft':
      case 'Left':

        if (isRTL)
          return;

        if (inputNode.selectionStart > 0)
          return;

        deltaY = -1;
        offsetX = Infinity;

        break;

      case 'ArrowRight':
      case 'Right':

        if (isRTL)
          return;

        if (inputNode.selectionEnd < textLineList[index].length)
          return;

        deltaY = 1;
        offsetX = 0;

        break;
    }

    evt.preventDefault();

    // update data

    var nextIndex = sanitize(index + deltaY);

    if (nextIndex !== index)
      handleLineChange({newIndex: nextIndex, oldIndex: index});

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

  function handleFocus (evt) {
    var index = nodeList.indexOf(evt.target.parentNode);

    if (activeNode !== null && activeNode.classList.contains(CONST.ACTIVE))
      activeNode.classList.remove(CONST.ACTIVE)

    activeNode = evt.target.parentNode;

    activeNode.classList.add(CONST.ACTIVE);

    handleLineChange({newIndex: index});
  }

  function handleLineChange (detail) {

    if (typeof onLineChange !== 'function')
      return;

    onLineChange({type: 'linechange', detail: detail});

  }

}

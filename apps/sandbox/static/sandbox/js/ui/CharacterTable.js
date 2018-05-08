function CharacterTable () {

  // TODO: rename to CharacterDialog?

  // TODO: keep most recent items

  // TODO: show on hashchange
  // e.g. var HASH = '#character-table';

  var URL = '/data/unicode-blocks.json';


  var DEFAULT_BLOCK = 145;

  var viewNode = document.querySelector('.js-character-table');

  var selectNode = viewNode.querySelector('.js-select');
  var tableNode = viewNode.querySelector('.js-table');
  var cancelNode = viewNode.querySelector('.js-cancel');

  var ranges;
  var labels;

  var promise = null;

  var resolve = null;
  var reject = null;

  // var p = getJSON(PREFIX + '/data/unicode-blocks.json');
  // p.then(initialize);

  return {
    isVisible: function () {
      return !viewNode.classList.contains('hidden');
    },
    select: function () {
      return new Promise(function (resolve_, reject_) {

        if (promise === null)
          promise = getJSON(PREFIX + URL).then(initialize);
        else
          promise = resetView();

        promise.then(showView);

        resolve = resolve_;
        reject = reject_;

      });
    }
  };

  function initialize (data) {

    ranges = data.ranges || [];
    labels = data.labels || [];

    renderSelect();
    update(DEFAULT_BLOCK);

    addEventListeners();

  }

  function resetView () {

    tableNode.scrollTop = 0;
    tableNode.scrollLeft = 0;

    return Promise.resolve();

  }

  function addEventListeners () {
    selectNode.addEventListener('change', handleChange, false);
    tableNode.addEventListener('click', handleClick, false);
    tableNode.addEventListener('keypress', handleKeypress, false);
    cancelNode.addEventListener('click', handleCancel, false);
  }

  function renderSelect () {

    var selectedNode;

    for (var index = 0; index < labels.length; index++) {

      var optionNode = document.createElement('option');
      optionNode.setAttribute('name', 'block');
      optionNode.setAttribute('value', 'block-' + index);
      optionNode.textContent = labels[index];
      selectNode.appendChild(optionNode);

      if (index === DEFAULT_BLOCK)
        selectedNode = optionNode;

    }

    selectedNode.setAttribute('selected', '');

  }

  function renderTable (startCode, endCode) {

    var itemNode;
    var itemTmpl = document.createElement('button');
    itemTmpl.classList.add('item');
    itemTmpl.setAttribute('tabindex', 0);

    startCode = Math.max(0x21, startCode); // hide invisible chars

    for (var code = startCode; code <= endCode; code++) {
      itemNode = itemTmpl.cloneNode(true);
      // FIXME: handle invisible characters gracefully
      itemNode.setAttribute('data-char-code', code);
      itemNode.textContent = String.fromCharCode(code);
      tableNode.appendChild(itemNode);
    }
  }

  function resetTable () {
    while (tableNode.firstChild !== null)
      tableNode.removeChild(tableNode.firstChild);
  }

  function select (node) {

    console.assert(node instanceof HTMLElement);

    var charCode = parseInt(node.getAttribute('data-char-code'));

    return hideView().then(function () {
      console.assert(typeof resolve === 'function');
      resolve(String.fromCharCode(charCode));
    });
  }

  function handleChange (evt) {

    if (evt.cancelable)
      evt.preventDefault();

    update(selectNode.selectedIndex);

  }

  function handleClick (evt) {

    if (!evt.target.classList.contains('item'))
      return;

    if (evt.cancelable)
      evt.preventDefault();

    select(evt.target);

  }

  function handleKeypress (evt) {

    if (evt.currentTarget === window && evt.key === 'Escape') {
      handleEscapeKeypress(evt);
    }
    else if (evt.target.classList.contains('item')) {

      if (evt.key === 'Enter')
        handleEnterKeypress(evt);
      else
        handleArrowKeypress(evt);
    }
  }

  function handleEnterKeypress (evt) {

    evt.preventDefault();

    if (evt.cancelable)
      evt.stopPropagation();

    select(evt.target);

  }

  function handleArrowKeypress (evt) {
    
    var node = evt.target;
    var nextNode = null;

    // FIXME: handle up and down arrows

    switch (evt.key) {
      case 'ArrowRight':
        nextNode = node.nextElementSibling;
        if (nextNode === null)
          nextNode = tableNode.firstElementChild;
        break;
      case 'ArrowLeft':
        nextNode = node.previousElementSibling;
        if (nextNode === null)
          nextNode = tableNode.lastElementChild;
        break;
    }

    if (nextNode !== null)
      nextNode.focus();

  }

  function handleEscapeKeypress () {
    console.assert(typeof reject === 'function');
    hideView().then(reject);
  }

  function handleCancel (evt) {

    if (evt.cancelable)
      evt.preventDefault();

    hideView().then(reject);

  }

  function update (index) {
    var range = ranges[index];

    resetTable();
    resetView();

    renderTable(range[0], range[1]);
  }

  function hideView () {
    return new Promise(function (resolve) {

      window.removeEventListener('keypress', handleKeypress);

      if (!viewNode.classList.contains('hidden'))
        viewNode.classList.add('hidden');
      resolve();
    });
  }

  function showView () {
    return new Promise(function (resolve) {

      window.addEventListener('keypress', handleKeypress, false);

      if (viewNode.classList.contains('hidden'))
        viewNode.classList.remove('hidden');
      
      viewNode.focus();

    });
  }

}

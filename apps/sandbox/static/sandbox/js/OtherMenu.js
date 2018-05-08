function OtherMenu (viewer, pageDoc, postDoc, handleError) {

  console.assert(pageDoc instanceof Document);

  /* FIXTHIS: this is not really a menu, rather controller + model */
  var lineList = [];

  var saveNode = document.querySelector('.js-save');
  saveNode.setAttribute('disabled', '');
  saveNode.addEventListener('click', handleSave, false);

  var countNode = document.querySelector('.js-count');
  var textNode = document.querySelector('.js-text');

  function handleSelect (lineId, isDisabled) {

    if (isDisabled && lineList.indexOf(lineId) <= 0)
      lineList.push(lineId);
    else
      lineList.splice(lineList.indexOf(lineId), 1);

    if (lineList.length > 0)
      saveNode.removeAttribute('disabled');
    else
      saveNode.setAttribute('disabled', '');

    countNode.textContent = [
      lineList.length,
      'LINE' + (lineList.length != 1 ? 'S' : ''),
      'CHANGED'
    ].join(' ');

  }

  function handleSave (evt) {

    evt.preventDefault();

    saveNode.setAttribute('disabled', '');

    for (var index = 0; index < lineList.length; index++) {
      removeTextLine(pageDoc, lineList[index]);
    }

    postDoc().then(function () {

      lineList.length = 0;
      countNode.textContent = '';
      textNode.textContent = '';
      saveNode.setAttribute('disabled', '');

      viewer.render(pageDoc);

    }, function (error) {
      handleError(error);
    })

  }

  function removeTextLine (pageDoc, lineId) {
    var node = pageDoc.querySelector('TextLine[id="' + lineId  +'"]');
    if (node === null) {
      console.error("Could not locate TextLine '", lineId, "'");
      return;
    }

    var serializer = new XMLSerializer();
    var string = serializer.serializeToString(node);
    var comment = pageDoc.createComment(string);
    node.parentNode.replaceChild(comment, node);

  }

  return {
    select: handleSelect,
    print: function (lineId) {
      var node = pageDoc.querySelector('TextLine[id="' + lineId + '"] > TextEquiv > Unicode');

      if (node === null) {
        console.error("Could not locate TextLine '", lineId, "'");
        return
      }

      textNode.textContent = node.textContent;

    }
  };

}

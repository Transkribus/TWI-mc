function XMLEditor (onLineChange) {

  // NOTE: changing # of lines breaks everything

  // TODO: find right place for the following operations
  // TODO: replace < > with entities
  // TODO: use entitites for special characters, otherwise there will be unicode issues with composed characters
  // TODO: insert word break, e.g. special hyphen U+2010, xml tag, e.g.

  // TODO: create renderer method variant that handles text lines

  /* TODO: disable insertion of new lines using ENTER !important

     editor.textInput.getElement() ... handle, stopPropagation

     maybe also this: 

     editor.commands.addCommand({
       name: "NOP",
       exec: function() {},
       bindKey: {mac: "enter", win: "enter"}
     })
  */

  // TODO: review use of request animation frame, does it make sense?

  // TODO: review render, update init method

  // TODO: maybe, let XML Editor load its own dependencies

  // TODO: highlight the editor container when it is active using css

  // TODO: use nicer theme, e.g. better line highlight color

  // TODO: find nicer monospace font


  var editorNode = document.querySelector('.js-xml-editor');

  var editor;
  var session;
  var selection;

  var lastLineIndex = null;
  var textLineList = [];

  var isInit = false;

  var initPromise = new Promise(function (resolve) {
    requestAnimationFrame(initialize);
    requestAnimationFrame(function () {
      isInit = true;
      resolve();
    });
  });

  function initialize () {

    // ace.require('ace/ext/language_tools');

    editor = ace.edit(editorNode);

    editor.setOptions({
      // highlightActiveLine: false,
      // enableBasicAutocompletion: true
      selectionStyle: 'text',
      highlightSelectedWord: false,
      // wrapBehaviorsEnabled: true
    });

    editor.setTheme('ace/theme/textmate'); // text is black, xml hardly visible

    selection = editor.selection;

    session = editor.getSession();
    session.setMode('ace/mode/xml');

    editor.container.style.lineHeight = 1.5;
    editor.renderer.setOptions({
      showPrintMargin: false,
      showFoldWidgets: false,
      displayIndentGuides: false,
      fontSize: 14,
      fontFamily: 'monospace', // monspaced font is required
    });

    // editor.renderer.updateFontSize()

    editor.session.setOptions({
      // useWorker: false, // disables syntax validation
      wrap: true
    });

    // FIXME: this does not work for backspace

    // copy / cut / paste

    // var inputNode = editor.textInput.getElement();
    // inputNode.addEventListener('keydown', handleKeydown, false);

    // NOTE: override keys that might destroy integrity of line sequence

    // editor.commands.addCommand({
    //   name: "modify-backspace",
    //   exec: handleBackspace,
    //   bindKey: {mac: "backspace", win: "backspace"}
    // })

    // editor.commands.addCommand({
    //   name: "modify-delete",
    //   exec: handleBackspace,
    //   bindKey: {mac: "delete", win: "delete"}
    // })

    // editor.commands.addCommand({
    //   name: "modify-enter",
    //   exec: handleEnter,
    //   bindKey: {mac: "enter", win: "enter"}
    // })

    selection.on('changeCursor', handleChangeCursor);

  }

  return {
    update: function (newTextLineList) {

      console.assert(newTextLineList instanceof Array);

      lastLineIndex = null;
      textLineList.length = 0;
      textLineList.push.apply(textLineList, newTextLineList);

    },
    render: function () {
      if (isInit === true)
        return render();
      else
        return initPromise.then(render, function (error) { console.error(error); });
    },
    resize: function () {
      editor.resize();
    },
    moveTo: function (index) {
      selection.moveCursorToPosition({row: index, column: 0});
    },
    scrollTo: function (index) {
      editor.scrollToLine(index, false, true, null);
    },
    highlight: function (index) {
      throw new Error("Not implemented");
      // session.setMarker(new Range(0, 0, 0 10));
    },
    wrapWith: function (startTag, endTag) {
      // FIXME: is this behavior appropriate?
      var text = editor.getSelectedText();
      editor.insert(startTag + text + endTag);
    },
    focus: function () { editor.focus(); },
    hasChanges: function () { return !session.getUndoManager().isClean(); }
  };

  var isReady = true;

  function render () {

    return new Promise(function (resolve) {
      requestAnimationFrame(function () {

        // NOTE: emits change to last line, then to line 0 event
        isReady = false;
        session.setValue(textLineList.join('\n'));
        isReady = true;

        onLineChange(0);

        requestAnimationFrame(resolve);
      });
    });
  }

  function handleChangeCursor (evt) {

    if (!isReady)
      return;

    if (typeof onLineChange !== 'function') 
      return;

    var s = selection.getSelectionLead();

    var lineIndex = Math.max(0, Math.min(s.row, textLineList.length - 1));

    if (lineIndex === lastLineIndex)
      return;

    // notify image viewer to scroll part of image into view
    onLineChange(lineIndex);

    lastLineIndex = lineIndex;

  }

  // function handleEnter (command) {
  //   // go to next line if there is one
  // }

  // function handleBackspace (command) {
  //   // move to next line if line is empty
  // }

  // function handleDelete (command) {
  //   // do nothing if line is empty
  // }

  // function handleKeydown (evt) {

  //   if (evt.key === 'Enter') {
  //     evt.preventDefault();
  //     if (evt.cancelable)
  //       evt.stopPropagation();
  //   }
  //   else if (evt.key === 'Backspace') {
  //     evt.preventDefault();
  //     evt.stopPropagation();      
  //   }
  // }

}

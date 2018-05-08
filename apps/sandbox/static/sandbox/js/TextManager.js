var TEXT_LINE_LIST = [
  'The premise of subcultural dialectic theory holds that the significance of',
  'the observer is deconstruction, given that <person firstname="Jean Paul" lastname="Sartre">Sartre’s</person> analysis of neocapitalist',
  'capitalism in <place>Paris</place> is invalid. In a sense, Lyotard uses the term ‘<unclear>Baudrillardist</unclear>',
  'hyperreality’ to denote the role of the reader. <abbrev>i.e.</abbrev> artist.',
  'If subdialectic cultural theory holds, we have to choose between the',
  'pretextual paradigm of reality and <unclear>Lacanist</unclear> obscurity. However, the subject is',
  'contextualised into a feminism that includes sexuality as a whole.',
  '<person>Derrida</person> uses the term ‘neocapitalist capitalism’ to denote a mythopoetical',
  'totality. In a sense, the characteristic theme of the works of <person>Gibson</person> is the',
  'role of the writer as artist.'
];

function TextManager (doc) {

  // TODO: image, text editor, text viewer need to be coordinated, same line should be selected in all editors, see selectLine

  var CLASS_NAME = 'manager';

  var managerNode = document.querySelector('.js-manager');

  // var editNode = managerNode.querySelector('.js-edit');

  // editNode.addEventListener('click', handleClick, false);

  var actionNodes = Array.from(managerNode.querySelectorAll('.js-actions'));

  var editorNode = managerNode.querySelector('.js-editor');

  for (var index = 0; index < actionNodes.length; index++)
    actionNodes[index].addEventListener('click', handleClick, false);

  // var previewNode = managerNode.querySelector('.js-preview');
  // previewNode.addEventListener('click', handleClick, false);

  var defaultEditorName = 'xml-editor';
  var mostRecentEditorName = null;

  var editorNames = ['xml-editor', 'some-other-editor'];

  var currentLineId = null;

  // TODO: structure for all available editors ...


  // TODO: how to synch output of editors / preview viewer, e.g. onEditorChange (from, to) or something like that ..., save state of first one, update state of next ...


  // set up XMLEditor

  var tagSpec = new TagSpec();

  var renderer = new XMLStringRenderer(tagSpec);
  var xmlString = renderer.render(doc);

  var textLineList = xmlString.split('\n');

  // replace NOT with hyphen
  textLineList = textLineList.map(function (string) {

    var s = '';

    for (var index = 0; index < string.length; index++) {

      var code = string.charCodeAt(index)

      if (code >= 0x300 && code <= 0x36F)
        s += '&#' + code + ';'
      // else if (code === 60)
      //   s += '&lt;';
      // else if (code === 62)
      //   s += '&gt;';
      else
        s += string.charAt(index);
    }

    string = s;

    if (string.endsWith('\u00ac'))
      return string.replace('\u00ac', '\u2010');
    return string;
  });

  var xmlEditor = new XMLEditor(onLineChange);

  function onLineChange (lineIndex) {
    console.debug('switched to line', lineIndex);
  }

  // TODO: hide until it is done rendering ...
  xmlEditor.update(textLineList);
  xmlEditor.render();


  // set up HTMLTextViewer
  var textViewer = new HTMLTextViewer();

  textViewer.update(doc);
  textViewer.render();


  // set up preview viewer
  previewViewer = new PreviewViewer();

  return {
    // something like this?
    resize: function () {
      xmlEditor.resize();
    },
    selectLine: function (lineId) {
      currentLineId = lineId;
    },
    highlightLine: function () {
      //
    },
  };

  function handleClick (evt) {

    evt.preventDefault();

    var node = evt.target;

    if (node.nodeName !== 'BUTTON' || node.name !== 'action')
      return;

    handleAction(node.value);

  }

  function setClassName () {

    var classList = [CLASS_NAME];

    for (var index = 0; index < arguments.length; index++) {
      classList.push(arguments[index]);
    }

    managerNode.className = classList.join(' ');

  }

  function showEditor (name) {
    return new Promise(function (resolve) {

      if (name === null)
        name = defaultEditorName;

      if (editorNames.indexOf(name) < 0)
        throw new Error("Editor not found: " + name);

      // managerNode.classList.add('editing', name);
      setClassName('editing', name);

      mostRecentEditorName = name;

      resolve();

    });
  }

  function showPreview () {

    previewViewer.update();

    return previewViewer.render().then(function () {
      setClassName('editing', 'previewing');
    });

  }

  function showViewer () {
    return new Promise(function (resolve) {     

      setClassName('viewing');

      resolve();

    });
  }

  function handleAction (action) {

    var p = null;

    switch (action) {
      case 'edit':
        p = showEditor(mostRecentEditorName);
        break;
      case 'save':
        // save things and show viewer ... promise?
        p = showViewer();
        break;
      case 'cancel':
        p = showViewer();
        break;
      case 'xml-editor':
      case 'some-other-editor':
        p = showEditor(action);
        break;
      case 'preview':
        // do not save things, just show viewer in preview mode with temp document
        p = showPreview();
        break;
      default:
        console.error("Invalid action", action);
    }

    if (p !== null)
      p.then(function () {
        console.log("Done!");
      });
  }
}

function HTMLTextViewer () {

  var viewerNode = document.querySelector('.js-text-viewer');

  var handleMethods = {
    Page: handlePage,
    TableRegion: handleTableRegion,
    TextRegion: handleTextRegion,
    TextLine: handleTextLine,
    TableCell: handleTableCell,
    // Coords: handleCoords,
    // Baseline: handleBaseline,
    // Unicode: handleUnicode
  };
  
  // FIXME: use templates
  function handlePage (sourceNode, parentNode) {
    var node = document.createElement('main');
    node.classList.add(sourceNode.nodeName);
    return node;
  }

  function handleTableRegion  (sourceNode, parentNode) {
    throw new Error("Not Implemented");
  }

  function handleTableCell () {
    throw new Error("Not Implemented");
  }

  function handleTextRegion  (sourceNode) {
    var node = document.createElement('div');
    node.classList.add(sourceNode.nodeName);
    return node;
  }

  function handleTextLine (sourceNode) {

    var node = document.createElement('div');
    node.classList.add(sourceNode.nodeName);

    var unicodeNode = sourceNode.querySelector('Unicode'); 

    if (unicodeNode === null)
      return node;

    var string = unicodeNode.textContent;

    // NOTE: for some reason page xml uses non-breaking spaces only

    if (string === null)
      string = '';
    else
      string = string.trim();

    if (string !== '') {
      string = string.replace(/\u00a0/g, ' ');
      string = string.replace(/\u00ac$/, '\u2010');
    }

    var customAttribute = sourceNode.getAttribute('custom');
    if (customAttribute === null) {
      node.textContent = string;
      return node;
    }

    var attrList = parseCustomAttribute(customAttribute);

    var readingOrder = attrList.shift()
    console.assert(readingOrder.name === 'readingOrder');

    // var lineNum = readingOrder.attributes['index'] + 1;
    // var labelNode = document.createElement('span');
    // labelNode.textContent = lineNum;
    // node.appendChild(labelNode);

    // var tagSpec = new TagSpec();
    // console.log(string, toBracketedSegmentList(attrList, tagSpec.compare));

    // TODO: same thing but use DOM element api and teplates, like so:
    function DOMRenderer () {
      var root = document.createElement('div');

      var stack = [];


      return {};
    }

    function DOMTemplateRenderer () {
      var tmplNode = document.querySelector('.js-templates');

      return {
        handleStart: function () {},
      }
    }

    // TODO: merge segments, then add id of sorts, using hashid

    // TODO: thing that handles each tag

    // TODO: data structure that associates tags with info, e.g. their fields, for tooltips, etc.

    var tags = {
      abbrev: {
        start: function (attrList) {
          return 'abbr';
        },
        end: function () { return 'abbr' }
      }
    };

    function handleStartTag (name, attrList) {

      var e = tags[name];

      if (e && typeof e.start === 'function')
        return '<' + e.start(attrList) + '>';
      else
        return '<span class="tag ' + name + '">';
    }
    function handleEndTag (name) {

      var e = tags[name];

      if (e && typeof e.end === 'function')
        return '</' + e.end() + '>';
      else
        return '</span>';
    }

    function StringRenderer () {
      var results = [];
      return {
        render: function (doc) {
          throw new Error("Not Implemented");
        },
        handleStart: function (segment) {
          var name = segment.name;
          results.push(handleStartTag(segment.name, segment.attributes));
          return

          // TODO: thing that handles tags ...

          // if (segment.name === 'textStyle') {
          //   if (segment.attributes.superscript === 'true')
          //     segment.attributes.superscript = true;

          //   if (segment.attributes.superscript === true) {
          //     results.push('<sup>')
          //   }
          // }
          // else
          var name = segment.name;
          if (name in tags) {
            results.push('<' + tags[name](segment) + '>');
          }
          else
            results.push('<span class="tag ' + segment.name + '">');
        },
        handleEnd: function (segment) {
          results.push(handleEndTag(segment.name, segment.attributes));
          return;
          if (name in tags)
            results.push('</' + tags[name](segment) + '>');
          else
            results.push('</span>');
        },
        handleText: function (text) {
          results.push(text);
        },
        getResult: function () {
          return results.join('');
        }
      }
    }

    var h = new StringRenderer();

    var t = new TagSpec({});

    // FIXME: hierarchy not actually required ...
    renderBracketedSegmentListWithHierarchy(
      string, toBracketedSegmentList(attrList, t.compare),
      t.compare, t.compareHierarchy,
      h.handleStart, h.handleEnd, h.handleText
    );

    textWithTags = h.getResult();

    // console.log(htmlString);

    // node.appendChild(document.createTextNode(string));
    node.innerHTML = textWithTags

    return node;
  }

  function handleCoords (sourceNode, parentNode) {
    return null;
  }

  function handleBaseline (sourceNode, parentNode) {
    return null;
  }

  function handleUnicode (sourceNode, parentNode) {

    var string = sourceNode.textContent;

    // NOTE: for some reason page xml uses non-breaking spaces only

    string = string.trim();

    if (string !== '' && string !== null) {
      string = string.replace(/\u00a0/g, ' ');

      string = string.replace(/\u00ac$/, '\u2010');
    }

    return document.createTextNode(string);
  }

  function traverse (sourceNode, targetNode, isIncluded) {

    /* depth-first traversal */

    var handle;
    var index;
    var item;
    var nodeList;
    
    var stack = [[sourceNode, targetNode]];

    while (stack.length > 0) {

      item = stack.pop();

      sourceNode = item[0];
      targetNode = item[1];

      handle = handleMethods[sourceNode.nodeName];

      if (typeof isIncluded === 'function' && !isIncluded(sourceNode))
        continue;

      if (typeof handle === 'function') {
        targetNode = targetNode.appendChild(
          handle(sourceNode, targetNode));
      }

      // if (typeof handle === 'function') {
      //   node = handle(sourceNode, targetNode);
      //   if (!!node && node !== targetNode)
      //     targetNode = targetNode.appendChild(node);
      // }

      nodeList = Array.from(sourceNode.children);
      for (index = 0; index < nodeList.length; index++) {
        stack.push([nodeList[nodeList.length - index - 1], targetNode]);
      }

    }

  }

  function ignoreExtraTextRegion (node) {

    if (node.nodeName === 'Unicode') {

      if (node.parentNode.parentNode.nodeName === 'TextLine')
        return true;

      return false;
    }
    

    return true;
  }

  var doc = null;

  return {
    update: function (newDoc) {
      doc = newDoc;
    },
    render: function () {
      return new Promise(function (resolve) {
        requestAnimationFrame(function () {

          traverse(doc.documentElement, viewerNode, ignoreExtraTextRegion);

          resolve();

        });
      });
    }
  };

}

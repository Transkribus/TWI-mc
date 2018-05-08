function toBracketedSegmentList (segmentList, compare) {

  console.assert(typeof compare === 'function');

  var bracketedSegmentList = [];
  var segment;

  for (var index = 0; index < segmentList.length; index++) {

    var segment = segmentList[index];

    console.assert(segment.attributes instanceof Object);
    console.assert(typeof segment.attributes['offset'] === 'number');
    console.assert(typeof segment.attributes['length'] === 'number');

    var name = segment.name;
    var attrs = segment.attributes;
    var offset = attrs.offset;
    var length = attrs.length;

    bracketedSegmentList.push({
      name: name,
      offset: offset,
      length: length,
      isStart: true,
      attributes: attrs,
      id: index
    });

    bracketedSegmentList.push({
      name: name,
      offset: offset + length,
      length: 0,
      isStart: false,
      id: index,
    });
  }

  return bracketedSegmentList;

}

function XMLStringRenderer (tagMgr) {

  var compare = tagMgr.compare;
  var compareHierarchy = tagMgr.compareHierarchy

  function Handler () {
    var results = [];

    function startTextLine () { }

    function endTextLine () {
      results.push('\n');
    }

    function toAttrString (attrs) {
      return Object.keys(attrs).filter(function (key) {
        return key !== 'offset' && key !== 'length' && key !== 'continued';
      }).sort().map(function (key) {
        return key + '="' + attrs[key] + '"';
      }).join(' ');
    }

    function startTag (name, attributes) {

      var attrString = attributes !== undefined ? toAttrString(attributes) : '';

      var string = [
        '<', name, (attrString ? ' ' + attrString : '') + '>'
      ].join('');

      results.push(string);
    }

    function endTag (name) {
      results.push('</' + name + '>');
    }

    return {
      handleStart: function (segment) {
        if (segment.name === 'TextLine') {
          startTextLine(segment.name, segment.attributes);
        }
        else {
          startTag(segment.name, segment.attributes);
        }
      },
      handleEnd: function (segment) {
        if (segment.name === 'TextLine')
          endTextLine(segment.name);
        else {
          endTag(segment.name, segment.attributes);
        }
      },
      handleText: function (text) {
        results.push(text);
      },
      getResult: function () {        
        return results.join('').trim();
      }
    };
  };

  var handler = new Handler();

  return {
    render: function (pageDoc) {
      var lineList = toLineList(pageDoc, processTextLineNode);
      var merged = toSegmentList(lineList, compare);
      var bracketedSegmentList = toBracketedSegmentList(merged.segments, compare);
      return toXMLString(merged.text, bracketedSegmentList);
    }
  };

  function toLineList (doc, process) {

    console.assert(typeof process === 'function');

    var lineList = [];

    var it = new OrderedTextLineIterator(doc);       

    for (var i = it.next(); !i.done; i = it.next()) {
      lineList.push(process(i.item));
    }
  
    return lineList;
  }

  function processTextLineNode (textLineNode) {

    var attrList = parseCustomAttribute(
      textLineNode.getAttribute('custom'));

    console.assert(attrList.shift().name === 'readingOrder');

    return {
      segments: attrList,
      text: textLineNode.querySelector('Unicode').textContent
    };
  }

  function toSegmentList (lineList, compare) {

    console.assert(typeof compare === 'function');

    var mergedLineList = {
      text: '', 
      offset: 0,
      segments: []
    };  

    // lineList.reduce(mergeContinuedSegments, mergedLineList);
    lineList.reduce(function (result, line) {

      // FIXME: hack for dealing with line breaks correctly

      var r = mergeContinuedSegments(result, line);

      result.text += '\n';
      result.offset += 1;

      return r;
    }, mergedLineList);

    return {
      text: mergedLineList.text,
      segments: mergedLineList.segments.sort(compare)
    };

  }

  function toXMLString (text, bracketedSegmentList) {
    //renderBracketedSegmentList(
    renderBracketedSegmentListWithHierarchy(
      text,
      bracketedSegmentList,
      compare,
      compareHierarchy,
      handler.handleStart,
      handler.handleEnd,
      handler.handleText
    );

    return handler.getResult();

  }

}

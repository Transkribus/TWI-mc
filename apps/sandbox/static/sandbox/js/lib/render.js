function toBracketedSegmentList (items) {

  var results = [];

  for (var index = 0; index < items.length; index++) {

    var item = items[index];

    console.assert(item.attributes instanceof Object);
    console.assert(typeof item.attributes['offset'] === 'number');
    console.assert(typeof item.attributes['length'] === 'number');

    var name = item.name;
    var attrs = item.attributes;
    var offset = attrs.offset;
    var length = attrs.length;

    results.push({
      name: name,
      offset: offset,
      length: length,
      isStart: true,
      attributes: attrs,
      id: index
    });

    results.push({
      name: name,
      offset: offset + length,
      length: 0,
      isStart: false,
      id: index,
      _s: results[results.length - 1]
    });
  }

  // return items.sort(compare);

  return results;

}

function renderBracketedSegmentList (bracketedSegmentList, handleStart, handleEnd, handleText) {

  // TODO: add text handling

  throw new Error("Not implemented");

  var bracketedSegmentList = data[1];
  bracketedSegmentList.sort(compare)

  var results = [];

  var stack = [];

  var tempStack = []

  for (var index = 0; index < bracketedSegmentList.length; index++) {

    var segment = bracketedSegmentList[index];

    if (segment.open) {
      stack.push(segment);
      handleStart(segment);
    }
    else {
      var tempSegment;
      for (var tempSegment = stack[stack.length - 1]; stack.length > 0 && tempSegment.name !== segment.name; tempSegment = stack.pop()) {
        tempSegment = stack.pop();

        handleEnd(segment);

        tempStack.push(tempSegment);
      }

      stack.pop();

      results.push(end(segment));

      while (tempStack.length > 0) {
        var otherSegment = tempStack.shift();

        handleStart(otherSegment);
      }

    }


  }

  function start (segment) {
    return '<' + segment.name + '>';
  }

  function end (segment) {
    return '</' + segment.name + '>'
  }

  console.log(data[0], results);
}

function renderBracketedSegmentListWithHierarchy (text, bracketedSegmentList, compare, compareHierarchy, handleStart, handleEnd, handleText) {

  /* TODO:
     
     - pass in functions for start, end, text handlers

     - refactor / avoid duplication:

     END  START
     ---- -----

     CS   CS ... close subordinates (output)
     EI   SI ... end / start segment (output)
     OS   OS ... open subordinates (output)

          RI ... push segment on stack (state)
     PS   PS ... push subordinates back on stack (state)

     GS+  GS ... get subordinates with extra case for identity check

     - more testing

     - handle case where hierarchy is equal

     - depth vs. hierarchy: can hierarchy be generalized to depth? so that toXML, toSegmentList work back and forth

  */

  bracketedSegmentList.sort(compare)

  var results = [];

  var stack = [];

  var offset = 0;

  for (var index = 0; index < bracketedSegmentList.length; index++) {

    var segment = bracketedSegmentList[index];

    if (segment.isStart) {

      // get all subordinate nodes (generic, share)

      var s = [];
      var i;

      while (stack.length > 0) {

        i = stack.pop();

        // lower in hierarchy
        var v = compareHierarchy(segment, i);

        if (v < 0) {
          s.push(i);
        }
        // higher in hierarchy
        else if (v > 0) {

          // put it back on stack
          stack.push(i);

          break;
        }
        else {
          // FIXME: what if hierarchy is equal?
          throw new Error("NotImplemented");
        }

      }

      // insert text
      if (offset < segment.offset)
        handleText(text.slice(offset, segment.offset));

      // close all subordinates
      for (var j = 0; j < s.length; j++) {
        handleEnd(s[j]);
      }

      // now start superordinate node
      handleStart(segment);

      // open all subordiantes again
      for (var j = s.length; j > 0; j--) {
        handleStart(s[j - 1]);
      }

      // put superordinate on stack
      stack.push(segment);

      // put subordinates back on stack
      while (s.length > 0)
        stack.push(s.pop());

      offset = segment.offset;

    }
    else {

      // get all subordinate nodes

      var s = [];
      var i;

      while (stack.length > 0) {

        i = stack.pop();

        // tag is closed
        if (i.id === segment.id) {
          // do not push it back on stack
          break;
        }
        else {

          var v = compareHierarchy(segment, i);

          if (v < 0) {
            s.push(i);
          }

          else if (v > 0) {

            // put it back on stack
            stack.push(i);

            break;
          }
          else {
            throw new Error("NotImplemented");
          }
        }

      }

      // add text
      if (offset < segment.offset)
        handleText(text.slice(offset, segment.offset));

      // close all subordinates
      for (var j = 0; j < s.length; j++) {
        handleEnd(s[j]);
      }

      // now end superordinate node
      handleEnd(segment);

      // open all subordinates again
      for (var j = s.length; j > 0; j--) {
        handleStart(s[j - 1]);
      }

      // put subordinates back on stack
      while (s.length > 0)
        stack.push(s.pop());

      offset = segment.offset;

    }

  }

  // add left over text after tag e.g. <node>xxxxxx</node>xxxxxxEOL
  if (offset < text.length)
    handleText(text.slice(offset, text.length));

}

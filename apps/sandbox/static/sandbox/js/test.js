// FIXME: figure out how to deal with items which are equal in hierarchy
// TODO: iterate all lines in document in reading order ...
// TODO: make this more re-useable / flexible, i.e. factory for creating custom ordering function e.g. as part of TagDef

function compare (a, b) {

  var diff = Math.sign(a.offset - b.offset);

  if (diff !== 0)
    return diff;

  /* Fallback: decide based on hierarchy */
  if (a.isStart === b.isStart) {

    diff = Math.sign(hierarchy[b.name] - hierarchy[a.name]);

    /* NOTE: assumes same type of segment is never nested within itself */
    if (diff === 0)
      /* NOTE: could decide this like so: segment with leftmost offset precedes other segment, i.e. contains other segment */
      throw new Error("Not Implemented" + ': ' + JSON.stringify([a, b]));

    if (a.isStart === true)
      return diff
    else
      return -diff;
  }

  /* Ensure close precedes open */
  if (a.isStart === false)
    return -1;
  else
    return 1;

}


var hierarchy = {
  textStyle: 0,
  sic: 5,
  comment: 6,
  unclear: 7,
  abbrev: 8,
  person: 9,
  place: 10
};

var compareHierarchy = (function (map) {
  return function compareHierarchy (a, b) {
    return Math.sign(map[b.name] - map[a.name]);
  }
}(hierarchy));


function renderBracketedSegmentList (text, bracketedSegmentList, handleStart, handleEnd, handleText) {

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

  // TODO: instead of using result, jstu do handleStartNode, handleText etc.

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

function renderBracketedSegmentList2 (text, items) {

  /* TODO:
     
     - pass in functions for start, end, text handlers

     - refactor / avoid duplication:

     END  START
     ---- -----

     CS   CS ... close subordinates (output)
     EI   SI ... end / start item (output)
     OS   OS ... open subordinates (output)

          RI ... push item on stack (state)
     PS   PS ... push subordinates back on stack (state)

     GS+  GS ... get subordinates with extra case for identity check

     - more testing

     - handle case where hierarchy is equal

     - depth vs. hierarchy: can hierarchy be generalized to depth? so that toXML, toSegmentList work back and forth

  */

  // TODO: instead of using result, jstu do handleStartNode, handleText etc.

  items.sort(compare)

  var results = [];

  var stack = [];

  var offset = 0;

  for (var index = 0; index < items.length; index++) {

    var item = items[index];

    if (item.isStart) {

      // get all subordinate nodes (generic, share)

      var s = [];
      var i;

      while (stack.length > 0) {

        i = stack.pop();

        // lower in hierarchy
        var v = compareHierarchy(item, i);

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
      if (offset < item.offset)
        results.push(text.slice(offset, item.offset));

      // close all subordinates
      for (var j = 0; j < s.length; j++) {
        results.push(end(s[j]));
      }

      // now start superordinate node
      results.push(start(item));

      // open all subordiantes again
      for (var j = s.length; j > 0; j--) {
        results.push(start(s[j - 1]));
      }

      // put superordinate on stack
      stack.push(item);

      // put subordinates back on stack
      while (s.length > 0)
        stack.push(s.pop());

      offset = item.offset;

    }
    else {

      // get all subordinate nodes

      var s = [];
      var i;

      while (stack.length > 0) {

        i = stack.pop();

        // tag is closed
        if (i.id === item.id) {
          // do not push it back on stack
          break;
        }
        else {

          var v = compareHierarchy(item, i);

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
      if (offset < item.offset)
        results.push(text.slice(offset, item.offset));

      // close all subordinates
      for (var j = 0; j < s.length; j++) {
        results.push(end(s[j]));
      }

      // now end superordinate node
      results.push(end(item));

      // open all subordinates again
      for (var j = s.length; j > 0; j--) {
        results.push(start(s[j - 1]));
      }

      // put subordinates back on stack
      while (s.length > 0)
        stack.push(s.pop());

      offset = item.offset;

    }

  }

  // add left over text after tag e.g. <node>xxxxxx</node>xxxxxxEOL
  if (offset < text.length)
    results.push(text.slice(offset, text.length));

  return results.join('');

  function start (item) {
    // return '<' + item.name + '>';
    return '<span class="tag ' + item.name + '">';
  }

  function end (item) {
    return '</span>';
  }


}

// TODO: handle readingOrder, i.e. list things according to it, e.g. by re-arranging the DOM in-place as the least intrusive option, store and then restore original order when saving

function toSegmentList2 (doc) {

  // this does all the things at once, i.e. keeping count

  function visitBefore (item) {

    item.index = index;
    
    if (node.nodeType !== node.TEXT_NODE)
      return;

    if (node.parentNode.nodeName !== 'Unicode')
      return;

    text += node.nodeValue;
    index += node.nodeValue.length;

  }

  function visitAfter (item) {
    // NOTE: text nodes are not interesting
    if (node.nodeType === node.TEXT_NODE)
      return;

    // this is where all the data has been collected ...
    console.log({ 
      name: node.nodeName,
      index: item.index,
      length: index - item.index,
      text: text.slice(item.index, index)
    });
  }

  var index = 0;
  var text = '';

  // traverse(doc.documentElement, visitBefore, visitAfter);

  var stack = [{
    node: doc.documentElement,
    isVisited: true,
    index: null
  }];

  while (stack.length > 0) {

    var item = stack.pop();
    var node = item.node;

    if (item.isVisited === false) {
      visitAfter(item);
      continue;
    }

    visitBefore(item);

    item.index = index;
    item.isVisited = false;
    stack.push(item);

    var nodeList = Array.from(node.childNodes);

    for (var i = nodeList.length - 1; i >= 0; i--) {
      stack.push({
        node: nodeList[i],
        isVisited: true,
        index: index
      });
    }
  }

}


function isTextNode (node) {
  if (node.nodeType !== node.TEXT_NODE)
    return false;

  if (node.parentNode.nodeName !== 'Unicode')
    return false;

  return true;
}

function toSegmentList (doc) {

  var offset = 0;
  var text = '';

  // traverse(doc.documentElement, visitBefore, visitAfter);

  var stack = [{
    node: doc.documentElement,
    isStart: true,
    offset: null,
    depth: 0 // hierarchy
  }];

  while (stack.length > 0) {

    var item = stack.pop();
    var node = item.node;

    if (item.isStart === false) {
      // NOTE: text nodes are not interesting
      if (node.nodeType !== node.TEXT_NODE)
        // this is where all the data has been collected ...
        console.log({ 
          name: node.nodeName,
          offset: item.offset,
          length: offset - item.offset,
          text: text.slice(item.offset, offset),
          depth: item.depth
        });
      continue;
    }

    item.offset = offset; // store current offset
    item.isStart = false;
    stack.push(item);

    // update values ...
    if (isTextNode(node)) {
      text += node.nodeValue;
      offset += node.nodeValue.length;
    }

    var nodeList = Array.from(node.childNodes);

    for (var i = nodeList.length - 1; i >= 0; i--) {
      // store current offset along with item
      stack.push({
        node: nodeList[i],
        isStart: true,
        offset: offset,
        depth: item.depth + 1
      });
    }
  }

}

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

function traverse (node, visitBefore, visitAfter) {

  visitBefore(node);

  var nodes = Array.from(node.childNodes);

  for (var index = 0; index < nodes.length; index++) {
    traverse(nodes[index], visitBefore, visitAfter);
  }

  visitAfter(node);

}

function otherTest (data) {

  // function compare_ (a, b) {
  // return -compare(a, b);
  // }

  var items = data[1];
  items.sort(compare)

  var results = [];

  var stack = [];

  var tempStack = []

  for (var index = 0; index < items.length; index++) {

    var item = items[index];

    if (item.open) {
      stack.push(item);
      results.push(start(item));
    }
    else {
      var tempItem;
      for (var tempItem = stack[stack.length - 1]; stack.length > 0 && tempItem.name !== item.name; tempItem = stack.pop()) {
        tempItem = stack.pop();

        results.push(start(item));

        tempStack.push(tempItem);
      }

      stack.pop();

      results.push(end(item));

      while (tempStack.length > 0) {
        var otherItem = tempStack.shift();

        results.push(start(otherItem));
      }

    }


  }

  function start (item) {
    return '<' + item.name + '>';
  }

  function end (item) {
    return '</' + item.name + '>'
  }

  console.log(data[0], results);
}

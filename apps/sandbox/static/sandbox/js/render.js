function Segment (name, offset, length, attributes) {

  this.name = name;
  this.offset = offset;
  this.length = length;

  this.attrs = attributes || {};

}

Segment.prototype.getAttribute = function (name) {
  console.assert(typeof name === 'string' && name !== '');

  if (!(name in this.attrs))
    return null;

  return this.attrs[name];
};

Segment.prototype.isSeniorTo = function (segment) {
  console.assert(segment instanceof Segment);
  return this.offset + this.length >= segment.offset + segment.length;
};

Segment.prototype.isEmpty = function () {
  return this.length === 0;
};

Segment.prototype.hasEndedAt = function (offset) {
  return this.offset + this.length <= offset;
};

Segment.prototype.toString = function () {
  return JSON.stringify({
    name: this.name,
    offset: this.offset,
    length: this.length
  });
};

function peek (stack) {
  return stack[stack.length - 1];
}

function compareStartOffset (s, t) {

  var v = s.offset - t.offset;

  if (v !== 0)
    return v;

  var w = t.length - s.length;

  if (w !== 0)
    return w;

  // FIXME: does this do the right thing?
  return s.name.localeCompare(t.name);
  
}

function compareStopOffset (s, t) {

  var v =  t.offset + t.length - (s.offset + s.length);

  if (v !== 0)
    return v;

  var w = t.length - s.length;

  if (w !== 0)
    return w;

  return s.name.localeCompare(t.name);

}

function render (string, segments, handleOpen, handleClose, handleText, handleOpenClose) {

  var offset = 0;

  var stack = segments.slice().reverse();
  var openStack = [];

  while (stack.length > 0) {

    // NOTE: assumes segments on stack are ordered by seniority with most senior segment on top of stack
    
    var n = peek(stack);

    // find all segments starting at this offset
    var newStack = [];
    while (stack.length > 0 && peek(stack).offset === n.offset) { 
      newStack.push(stack.pop());
    }

    // close all nodes that have already ended at this point
    // NOTE: open segment cannot end here AND be senior to new segment, unless the new segment is empty as well
    while (openStack.length > 0 && peek(openStack).hasEndedAt(n.offset)) {

      var t = openStack.pop();

      if (offset < s.offset + s.length)
        handleText(string.slice(offset, s.offset + s.length), offset, s.offset + s.length);
      offset = s.offset + s.length;

      handleClose(t);
    }

    // handle text before opening tag: ^01<a>...$
    if (offset < n.offset) {
      handleText(string.slice(offset, n.offset), 0, n.offset);
      offset = n.offset;
    }

    var needToOpen = [];
    var needToOpenAndClose = []; // special case for new  segments with length = 0, e.g. gap, newline

    while (newStack.length > 0) {

      var s = newStack.pop();

      // split open segments that are less senior than new segment
      while (openStack.length > 0 && !peek(openStack).isSeniorTo(s)) {
        // get next segment from stack of open segments

        var t = openStack.pop();

        // handle text up to closing tag: ^...45</b>67</a>89$
        // if (offset < t.offset)

        // if (offset < s.offset + s.length)
          // text(string.slice(offset, t.offset + t.length), offset, t.offset + t.length);
        //  text(string.slice(offset, s.offset + s.length), offset, s.offset + s.length);
        // offset = s.offset + s.length;

        handleClose(t);

        needToOpen.push(t);
      }

      // at this point, there are no more open segments to split
      // open new segment
      if (!s.isEmpty())
        needToOpen.push(s)
      else
        needToOpenAndClose.push(s);

    }

    // NOTE: handle segment with length = 0, i.e. self-closing tag, put them between the other segments
    while (needToOpenAndClose.length > 0) {
      var s = needToOpenAndClose.pop();
      handleOpenClose(s);
    }

    while (needToOpen.length > 0) {
      var s = needToOpen.pop()
      handleOpen(s);
      openStack.push(s);
    }

  }

  // close all remaining open segments
  while (openStack.length > 0) {

    var s = openStack.pop();

    // handle text up to closing tag: ^...</b>67</a>...$
    if (offset < s.offset + s.length)
      handleText(string.slice(offset, s.offset + s.length), offset, offset + s.length);

    offset = s.offset + s.length;
    
    handleClose(s);

  }

  // handle text after last closing tag: ^...67</a>89$
  if (offset < string.length)
    handleText(string.slice(offset, string.length), offset, string.length);

}

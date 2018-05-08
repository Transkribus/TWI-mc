// NOTE: segment representation {name: ..., attributes: ...} is really prone to errors

function isContinued (s) {
  var attrs = s.attributes;

  if (attrs === undefined)
    return false;
  // FIXTHIS: take into account offset ... end of line
  return attrs.continued === true;
}

function isContinuing (s, offset) {
  // NOTE: only makes sense for segments if offsets relative to line start
  var attrs = s.attributes;
  return isContinued(s) && attrs.offset === 0;
}

function isContinuedBy (segment, otherSegment) {

  if (segment.name !== otherSegment.name)
    return false;

  var attrs = segment.attributes;
  var otherAttrs = otherSegment.attributes;

  // both have no attributes
  if (attrs === undefined && otherAttrs === undefined)
    false;

  // one has no attributes
  if ([attrs, otherAttrs].indexOf(undefined) >= 0)
    return false;

  // not continued
  if ([false, undefined].indexOf(attrs.continued) >= 0 && [false, undefined].indexOf(otherAttrs.continued) >= 0)
    return false;

  // one is continued, the other not
  if ((attrs.continued === true || otherAttrs.continued === true) && attrs.continued !== otherAttrs.continued)
    return false;

  var ignore = ['readingOrder', 'index', 'offset', 'length'];

  // value for key in one not equal value in other
  for (var key in attrs) {
    if (ignore.indexOf(key) < 0)

      // if (!(key in otherAttrs))
      //   return false;

      if (otherAttrs[key] !== attrs[key])
        return false;

    ignore.push(key);

  }

  // other way around ...
  for (var otherKey in otherAttrs) {
    if (ignore.indexOf(otherKey) < 0)
      if (otherAttrs[otherKey] !== attrs[otherKey])
        return false;
  }

  return true;

}

function findContinuingSegment (segment, segmentList) {

  var results = [];

  var isAmbiguous = false; // if more than one tag of type

  for (var index = 0; index < segmentList.length; index++) {
    var otherSegment = segmentList[index];

    if (!isContinuing(otherSegment))
      continue;

    if (otherSegment.name === segment.name)
      results.push(otherSegment);
  }

  if (results.length <= 1) // is not ambiguous or no matches
    return results.pop() || null;

  console.assert(results.length === 0); // invalid data ...
  
  // check matches with disambiguation using attributes
  /* var count = 0;
   * while (results.length > count) {
   *   otherSegment = results.pop();
   *   if (false);
   * }
   */
  for (index = 0; index < results.length; index++) {
    var otherSegment = results[index];
    if (!isContinuedBy(segment, otherSegment))
      results[index] = null;
  }

  results = results.filter(function (segment) {
    return segment !== null;
  });

  if (results.length > 1)
    throw new Error("Ambiguous continuations!");

  return results[0] || null;

}

function merge(s, t) {
  s.attributes.length += t.attributes.length;
  t.attributes.length = 0;
  return s;
}

function remove (item, itemList) {
  return itemList.splice(itemList.indexOf(item), 1)[0];
}

function insert (segment, result) {
  console.assert(segment.attributes instanceof Object);
  console.assert(typeof result.offset === 'number');
  segment.attributes.offset += result.offset;
  result.segments.push(segment);
}

function end (segment) {
  console.assert(segment.attributes instanceof Object);
  segment.attributes.continued = false;
}

// FIXME: use offset as well ...?

var result = {
  offset: 0,
  items: [],
  test: ''
};

function mergeContinuedSegments (result, nextLine) {

  console.assert(result.segments instanceof Array);
  console.assert(nextLine.segments instanceof Array);

  var segmentList = result.segments;
  var offset = result.offset || 0;
  var text = result.text || '';

  var nextSegmentList = nextLine.segments;
  // var nextLine = nextLine.segments || [];
  var nextText = nextLine.text || '';

  for (var i = 0; i < segmentList.length; i++) {
    var s = segmentList[i];

    if (isContinued(s)) {

      var t = findContinuingSegment(s, nextSegmentList);

      if (t === null) {
        // this segment ends here
        end(s);
      }
      else {
        merge(s, t);
      }

      remove(t, nextSegmentList);

    }
  }

  // add remaining non-continued segments
  for (var j = 0; j < nextSegmentList.length; j++) {
    insert(nextSegmentList[j], result);
  }

  // insert({
  //   name: 'TextLine',
  //   attributes: {
  //     offset: 0,
  //     length: nextText.length
  //   }
  // }, result);

  // add new text
  result.text += nextText;
  result.offset += nextText.length;

  return result;

}


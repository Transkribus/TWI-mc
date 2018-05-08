function TagSpec () {

  // TODO: get this from trp api

  var hierarchy = {
    textStyle: 0,
    sic: 5,
    comment: 6,
    unclear: 7,
    abbrev: 8,
    person: 9,
    place: 10,
    date: 11,
    organization: 12,
    TextLine: 100,
  };

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

  var compareHierarchy = (function (map) {
    return function compareHierarchy (a, b) {
      return Math.sign(map[b.name] - map[a.name]);
    }
  }(hierarchy));

  return {
    compare: compare,
    compareHierarchy: compareHierarchy
  }

}

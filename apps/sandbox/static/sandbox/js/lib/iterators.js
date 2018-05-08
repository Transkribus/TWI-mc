function OrderedTextLineIterator (doc) {
  // NOTE: doc must have reading order

  console.warn("OrderedTextLineIterator has not been tested ...");

  var regionList = Array.from(doc.querySelectorAll('TextRegion'));

  var regionOrder = new ReadingOrderIndex(regionList);
  var regionNode;

  var lineList = [];
  var lineOrder;

  regionList.sort(regionOrder.compare);

  return {
    next: function () {

      // find next reagion with lines ...
      while (regionList.length > 0 && lineList.length === 0) {
        regionNode = regionList.shift();
        lineList = Array.from(regionNode.querySelectorAll('TextRegion > TextLine'));

        if (lineList.length > 0) {
          lineOrder = new ReadingOrderIndex(lineList);
          lineList.sort(lineOrder.compare);
        }
      }

      var isDone = regionList.length === 0 && lineList.length === 0;

      var item = lineList.shift();

      return {
        item: item,
        done: isDone
      }
    },
  };

}

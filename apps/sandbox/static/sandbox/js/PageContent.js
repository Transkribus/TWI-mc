function parseCustomAttribute (string) {

  var results = [];

  string.split('} ').forEach(function(a) {
    var result = {};
    var attributes = {};

    var name = a.split(' {')[0];
    var attrs = a.split(' {')[1];

    var result = {name: name.trim()};

    if (attrs.indexOf('}'))
      attrs = attrs.replace('}', '');

    attrs.split(';').forEach(function(attr) {

      attr = attr.trim();

      if ( attr !== undefined && attr ) {
        k = attr.split(':')[0].trim();
        v = decodeURIComponent(JSON.parse('"' + attr.split(':')[1].trim().replace('"', '\\"') + '"'));
        if (k === 'index' || k === 'offset' || k === 'length')
          attributes[k] = parseInt(v);
        else if (k === 'continued' || k === 'superscript' || k === 'bold' || k === 'italic' || k === 'subscript')
          attributes[k] = Boolean(v);
        else
          attributes[k] = v;
      }
    });
    // FIXME: change name to attrs because attributes prone to typos
    result.attrs = result.attributes = attributes;
    results.push(result);
  });
  return results;
}

function toUnicode(string) {
  var result = "";
  for ( var i = 0; i < string.length; i++ ) {
    // Assumption: all characters are < 0xffff
    if ( /^[a-zA-Z0-9]*$/.test(string[i]) )
      result += string[i];
    else
      result += "\\u" + ("000" + string[i].charCodeAt(0).toString(16)).substr(-4);
  }
  return result;
}

function toCustomAttributeString (data) {
  var string = "";
  data.forEach(function (e) {
    string += e.name + " {";
    for ( var k in e.attributes ) {
      if ( k === 'index' || k === 'offset' || k === 'length' )
        string += k + ":" + e.attributes[k] + "; ";
      else
        string += k + ":" + toUnicode(e.attributes[k]) + "; ";
    }
    string = string.trim() + "} ";
  });
  return string.trim();
}


function hasTextLines (doc) {
  return doc.querySelector('TextLine') !== null;
}

function hasTextRegions (doc) {
  return doc.querySelector('TextRegion') !== null;
}

function hasEmptyLines (doc) {
  return doc.querySelector('TextEquiv > Unicode:empty') !== null;
}

var SELECTOR = {
  TextLine: 'TextRegion > TextLine, TableRegion > TableCell > TextLine'
};

function hasReadingOrder (doc, selector) {

  selector = selector || SELECTOR.TextLine;

  var items = doc.querySelectorAll(selector);

  for (var index = 0; index < items.length; index++) {

    var first = parseCustomAttribute(items[index]).shift();
    if (first.name !== 'readingOrder')
      return false;
  }

  return true;

}

function hasTags (doc) {
  var items = doc.querySelectorAll('TextLine[custom]');
  for (var i = 0; i < items.length; i++) {
    var attrList = parseCustomAttribute(items[i].getAttribute('custom'));
    for (var j = 0; j < attrList.length; j++) {
      var attrs = attrList[j].attributes || {};
      if ('offset' in attrs && 'length' in attrs)
        return true;
    }
  }
  return false;
}

function hasTextLinesWithoutUnicode (doc) {
  var textLines = doc.querySelectorAll('TextLine > Unicode');
  var textLinesWithoutUnicode = doc.querySelectorAll('TextLine > TextEquiv > Unicode');
  return textLines.length === textLinesWithoutUnicode.length;
}

// NOTE: commented out because es6 syntax

// function textLineHasCoords (doc) {
//   return Array.prototype.map.call(doc.querySelectorAll('TextLine'), node => Array.prototype.map.call(node.childNodes, child => child.nodeName === 'Coords').reduce((acc, cur) => acc = acc || cur, false)).reduce(function (acc, cur) { return acc || cur; }, false);
// }

// function textLineHasCoordsWithPoints (doc) {
//   return Array.prototype.map.call(doc.querySelectorAll('TextLine'), node => Array.prototype.map.call(node.childNodes, child => child.nodeName === 'Coords' && child.getAttribute('points').length > 0).reduce((acc, cur) => acc = acc || cur, false)).reduce(function (acc, cur) { return acc || cur; }, false);
// }

// function textLineHasCoordsWithPointsAndFormat (doc) {
//   return Array.prototype.map.call(doc.querySelectorAll('TextLine'), node => Array.prototype.map.call(node.childNodes, child => child.nodeName === 'Coords' && /[(\d+,\d+\s\d+,\d+)\s]+/.test(child.getAttribute('points'))).reduce(function (acc, cur) { return acc || cur; }, false)).reduce(function (acc, cur) { return acc || cur; }, false);
// }

var SELECTOR = {
  TextLine: 'TextRegion > TextLine, TableCell > TextLine'
};

function fixTextLinesWithoutUnicode (doc, selector) {

  selector = selector || 'TextRegion > TextLine, TableRegion > TableCell > TextLine';

  var lines = doc.querySelectorAll(selector);
  var line;
  var equiv;
  var unicode;

  for (var index = 0; index < lines.length; index++) {

    line = lines[index];
    equiv = line.querySelector('TextEquiv');

    if (equiv === null)
      equiv = line.appendChild(doc.createElement('TextEquiv'));

    unicode = equiv.querySelector('Unicode');

    if (unicode === null)
      unicode = equiv.appendChild(doc.createElement('Unicode'));

    unicode.textContent = '';

  }

}

function toRect (points) {

  var leftMost = Infinity;
  var rightMost = -Infinity;
  var topMost = Infinity;
  var bottomMost = -Infinity;

  points.forEach(function (point) {

    var x = point.x;
    var y = point.y;
    if (x < leftMost)
      leftMost = x;
    if (x > rightMost)
      rightMost = x;
    if (y > bottomMost)
      bottomMost = y;
    if (y < topMost)
      topMost = y;
  });

  return {
    x: leftMost,
    y: topMost,
    width: rightMost - leftMost,
    height: bottomMost - topMost
  };

}

function calcAvg () {
  return values.reduce(function (a, b) { return a + b; }, 0) / values.length;
}

function calcAvgDist (X) {

  var A; // baseline A, B
  var B;

  var avg = 0;

  for (var k = 0; k < X.length - 1; k++) {

    A = X[k];
    B = X[k + 1];

    var a = A[0]; // points on baseline
    var b = B[0];

    var d; // distance between baselines

    var nIter = 10000;

    for (var i = 0, j = 0; i < A.length && j < B.length; ) {

      if (nIter-- <= 0)
	throw new Error("Exceedeed maximum number of iterations!")

      /* consume points  */

      for (a = A[i]; a && a[0] <= b[0]; i++, a = A[i]) {
        d = Math.abs(b[1] - a[1]);
        avg += (d - avg) / (k + 1);
      }

      if (!a)
        a = A[A.length - 1];

      /* swap A and B rather than repeat loop ... */

      var T = A;
      A = B;
      B = T;

      var t = a;
      a = b;
      b = t;

      var l = i;
      i = j;
      j = l;

    }

  }

  return avg;
}

function parsePointsAttribute (string) {
  return string.split(' ').map(function (string) {
    return string.split(',').map(Number);
  }).map(function (array) {
    return new Point(array[0], array[1]);
  });
}

var Point = (function () {

  Point.prototype.toArray = function toArray () {
    return [this.x, this.y];
  };

  Point.prototype.toString = function () {
    return this.x + ',' + this.y;
  };

  return Point;

  function Point (x, y) {
    this.x = x;
    this.y = y;
  }

}());

function pointToString (p) {
  return p.x + ',' + p.y
}

var Point = (function () {

  Point.prototype.toArray = function toArray () {
    return [this.x, this.y];
  };

  Point.prototype.toString = function () {
    return this.x + ',' + this.y;
  };

  return Point;

  function Point (x, y) {
    this.x = x;
    this.y = y;
  }

}());

function parsePointsAttribute (string) {
  return string.split(' ').map(function (string) {
    return string.split(',').map(Number);
  }).map(function (array) {
    return new Point(array[0], array[1]);
  });
}

function calcLineHeight (doc) {

  var nodeList = Array.from(doc.querySelectorAll('TextRegion > TextLine, TableRegion > TableCell > TextLine'));

  var X = nodeList.map(function (node) {
    return parsePointsAttribute(node.querySelector(':scope > Coords').getAttribute('points')).map(function (point) {
      return [point.x, point.y];
    });
  });

  return calcAvgDist(X);

}





function calcAvgLineHeight (points) {

  var avgHeight = 0;

  var height;

  var centerY = calcMean(points.map(function (p) { return p[1]; }));

  var upperY;
  var lowerY;

  /* remove leftmost and rightmost points ... */
  var minX = Math.min.apply(Math, points.map(function (p) { return p[0]; }));
  var maxX = Math.max.apply(Math, points.map(function (p) { return p[0]; }));
  var width = maxX - minX;
  var alpha = 0.05;
  var leftMostX = minX + width * alpha;
  var rightMostX = maxX - width * alpha;

  for (var index = 0, y; index < points.length; index++) {

    p = points[index]

    x = p[0];

    if (x < leftMostX)
      continue
    if (x > rightMostX)
      continue

    y = p[1];

    if (y > centerY) {

      upperY = y;

    }
    else {

      lowerY = y;

    }

    if (upperY !== undefined && lowerY !== undefined) {
      height = upperY - lowerY;
      avgHeight += (height - avgHeight) / (index + 1);
    }
  }

  return avgHeight;
}

function Path (points) {
  /* FIXTHIS: inconsistent class pattern here ... */
  points = points || [];

  this.getPoints = function getPoints () { return points; };

  /* FIXTIHS: for performance, use cache decorator here */
  this.getRect = function getRect () {

    var leftMost = Infinity;
    var rightMost = -Infinity;
    var topMost = Infinity;
    var bottomMost = -Infinity;

    points.forEach(function (point) {

      var x = point.x;
      var y = point.y;

      if (x < leftMost)
        leftMost = x;
      if (x > rightMost)
        rightMost = x;
      if (y > bottomMost)
        bottomMost = y;
      if (y < topMost)
        topMost = y;

    });

    return {
      x: leftMost,
      y: topMost,
      width: rightMost - leftMost,
      height: bottomMost - topMost
    };

  };

}

function findLeftMostPoint (points) {
  var p;
  var min = Infinity;
  var result;

  for (var index = 0, length = points.length; index < length; index++) {
    p = points[index];

    if (p.x < min) {
      result = p;
      min = p.x;
    }
  }
  return result;
}

function findConvexHull (S) {
  /* jarvis algorithm. not particularly efficient */

  var hullPoint = findLeftMostPoint(S);
  var candidatePoint;
  var point;

  var P = [];

  var slope;
  var intercept;

  var i = 0;

  function isLeft(a, b, c){
    // https://stackoverflow.com/a/3461533
    return ((b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)) > 0;
  }

  do {
    P[i] = hullPoint;
    candidatePoint = S[0];
    for (var j = 0, length = S.length; j < length; j++) {
      point = S[j];
      if (candidatePoint === hullPoint || isLeft(hullPoint, candidatePoint, point)) {
        candidatePoint = point;
      }
    }
    i++;
    hullPoint = candidatePoint;
  }
  while (P[0] !== candidatePoint)

  return P;
}

function buildPageContent (data) {

  var pathAttr = 'coords';
  var baselineAttr = 'baseline';

  /* FIXTHIS: add image retc somewhere ... */

  var state = new TaskState(children);
  data = data.lines || [];
  var path = new Path(findConvexHull(data.reduce(function (a, b) {
    return a.concat(b[pathAttr]);
  }, []).map(function (p) {
    return new Point(p[0], p[1]);
  })));

  var offset = path.getRect();

  offset.x *= -1
  offset.y *= -1

  var children = data.map(function (data) {

    function createPoints (points, offset) {
      offset = offset || {x: 0, y: 0};
      return points.map(function (p) {
        /* NOTE: get relative to container */
        return new Point((offset.x || 0) + p[0],  (offset.y || 0) + p[1]);
      });
    }

    var path = new Path(createPoints(data[pathAttr] || [], offset));
    var baseline = new Path(createPoints(data[baselineAttr] || [], {
      x: offset.x,
      /* NOTE set baseline offset */

      y: offset.y + 0.1 * path.getRect().height
    }));

    var state = new State(false);
    var line = new Line(path, baseline, state);

    return {
      getBaseline: function () { return line._baseline.getPoints(); },
      getRect: function () { return line._path.getRect(); },
      getPath: function () { return line._path.getPoints(); },
      // isDone: function () { return line.state.isDone(); }
    };
  });

  // var task = new Task(children, path, state);
  // task._path.getRect();

  return {
    getChildren: function () { return task._children; },
    isDone: function () { return task.state.isDone(); },
    getRect: function () { return task._path.getRect(); },
    getPath: function () { return task._path.getPoints(); },
    getLineHeight: function () {
      return calcAvgDist(this.getChildren().map(function (line) {
	return line.getBaseline().map(function (p) {
	  return [p.x, p.y];
	});
      }));
    },
    getFontSize: function () {

      var avg = 0;

      this.getChildren().forEach(function (line, index) {

	var pivot = calcAverage(line.getBaseline().map(function (p) { return p.y; }));
	var upperHull = line.getPath().filter(function (point) { return point.y <= pivot; });

	var m = calcAvgDist([
	  line.getBaseline().map(pointToArray),
	  upperHull.map(pointToArray)
	]);

        avg += (m - avg) / (index + 1);

      });

      return avg;
    }
  };

}

/* reading order */

function OrderedTextLineIterator (doc) {
  // NOTE: doc must have reading order

  var SELECTOR = {
    REGION: 'TextRegion, TableRegion',
    LINE: 'TextRegion > TextLine, TableRegion > TableCell > TextLine'
  };

  var regionList = Array.from(doc.querySelectorAll(SELECTOR.REGION));

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
        lineList = Array.from(regionNode.querySelectorAll(SELECTOR.LINE));

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

function getReadingOrder (node) {
  var string = node.getAttribute('custom');
  console.assert(string !== null);
  var attrList = parseCustomAttribute(string);
  var readingOrder = attrList.shift();

  if (readingOrder.name === 'readingOrder')
    return readingOrder;

  for (var index = 0; index < attrList.length; index++) {
    readingOrder = attrList[index];
    if (readingOrder.name === 'readingOrder')
      return readingOrder;
  }

  throw new Error("readingOrder not specified");

}

function ReadingOrderIndex (nodes) {

  var readingOrderIndex = [];
  var nodeList = [];

  for (var index = 0; index < nodes.length; index++) {
    var node = nodes[index]
    var readingOrder = getReadingOrder(node);

    console.assert(readingOrder.attributes instanceof Object);
    console.assert(typeof readingOrder.attributes.index === 'number');

    nodeList.push(node);
    readingOrderIndex.push(readingOrder.attributes.index);
  }

  function get (node) {
    return readingOrderIndex[nodeList.indexOf(node)];
  }

  return {
    get: function (node) {
      return get(node);
    },
    compare: function (node, otherNode) {
      return get(node) - get(otherNode);
    }
  };
}

function traverseReadingOrder (node, visit, readingOrderedNodes) {

  // FIXME: how to deal with nodes that don't have reading order?

  visit(node);

  var nodes = Array.from(node.childNodes);

  if (readingOrderedNodes instanceof Array && readingOrderedNodes.indexOf(node.nodeName) >= 0) {
    var readingOrderIndex = buildReadingOrderIndex(nodes);
    nodes.sort(readingOrderIndex.compare);
  }

  for (var index = 0; index < nodes.length; index++) {
    traverseReadingOrder(nodes[index], visit);
  }

}



// *lol* of course we won't do this, just use XMLDocument.cloneNode(true);

function Node () {}

Node.prototype.getAttribute = function (name) {
  console.assert(name !== undefined);
  return this._attributes[name];
}

Node.prototype.setAttribute = function (name, value) {
  console.assert(name !== undefined);
  console.assert(value !== undefined);
  return this._attributes[name] = value;
}

Node.prototype.getText = function () {
  return this._text;
}

Node.prototype.setText = function (text) {
  console.assert(typeof text === 'string');
  return this._text = text;
}

function Page () {}

Page.prototype = Object.create(Node);

function TextRegion () {
}

TextRegion.prototype = Object.create(Node);

function TextLine () {
}

TextLine.prototype.getText = function () {
  return this._text;
}

TextLine.prototype.getAttributes = function () {
  return this._attributes;
}

TextLine.prototype = Object.create(Node);

function Unicode () {}

Unicode.prototype = Object.create(Node);

var Unicode = (function () {

  Unicode.prototype.getText = function () {
    return this._node.textContent;
  };

  Unicode.prototype.setText = function (text) {
    // throw new Error("NotImplemented");
    console.assert(typeof text === 'string');
    return this._node.textContent = text;
  };

  return Unicode;

  function Unicode (unicodeNode) {
    this._node = unicodeNode;
  }

}());

var Baseline = (function () {

  Baseline.prototype.getPoints = function () {
    return parsePointsAttribute(this._node.getAttribute('points'));
  };

  return Baseline;

  function Baseline (baselineNode) {
    this._node = baselineNode;
  }

}());

var TextLine = (function () {

  TextLine.prototype.getBaseline = function () {
    return new Baseline(this._node.querySelector('Baseline'));
  };

  TextLine.prototype.getUnicode = function () {
    return new Unicode(this._node.querySelector('TextEquiv > Unicode'));
  };

  return TextLine;

  function TextLine (textLineNode) {
    this._node = textLineNode;
  }

}());

function PageContent (root) {

  return {
    getTextLines: function () {
      return Array.from(root.querySelectorAll('Page > TextRegion > TextLine')).map(function (node) {
        return new TextLine(node);
      });
    },
    getTextRegions: function () {
      return Array.from(root.querySelectorAll('Page > TextRegion'));
    }
  };
}

var Line = (function () {

  function Line (path, baseline, state) {
    this._path = path;
    this._baseline = baseline;
    this.state = state;
  }

  // Line.prototype.isDone = function isDone () {
  //   return false;
  // };

  // Line.prototype.

  return Line;

}());

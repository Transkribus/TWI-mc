function TaggingViewer (pageDoc, onSomeCallback, onSomeOtherCallback) {

  var scopeNode = document.querySelector('.js-tagging-viewer');
  var textNode = scopeNode.querySelector('.js-text');

  var tmplNode = scopeNode.querySelector('.js-templates');
  var helloTmpl = tmplNode.querySelector('.js-hello');

  var pageRoot = pageDoc.documentElement;

  console.assert(pageDoc instanceof Document);
  console.assert(pageRoot.nodeName === 'PcGts');

  var tagColors = {
    abbrev: 'FF0000',
    date: '0000FF',
    gap: '1CE6FF',
    person: '00FF00',
    place: '8A2BE2',
    unclear: 'FFCC66',
    organization: 'FF00FF'
  };

  initialize();

  function initialize () {
    if (typeof onSomeCallback === 'function')
      onSomeCallback();
  }

  function render () {

    var nodes = Array.from(pageRoot.querySelectorAll('TextLine[custom]')); 

    nodes.forEach(function (node) {

      var textNode = node.querySelector('Unicode');
      var customAttribute = node.getAttribute('custom');

      var r;

      try {
        r = getLineDivWithTags(textNode.textContent, customAttribute);

        console.log({
          text: textNode.textContent,
          customAttribute: customAttribute,
          html: r
        });

      }
      catch (e) {
        console.error(textNode.textContent, e);
      }

    });

  }

  function getSortedCustomTagArray(customData) { 
    var custom = customData.replace(/\s+/g, '').split('}');
    var customTagArray = [];
    if ("None" != custom) {
      custom.forEach(function(attribute) { // turn "tags" into something closer to actual tags (=spans)
	attribute = attribute.split('{');
	if ("" != attribute && "readingOrder" != attribute[0] && attribute[1].indexOf("offset:") != -1 && attribute[1].indexOf(";length:") != -1) { // we have no use for readingOrder for now...
	  var split = attribute[1].split("offset:")[1].split(";length:");
	  var start = parseInt(split[0]);
	  var length = parseInt(split[1]); // parseInt doesn't care about what comes after the first int
	  var end = start + length;
	  var tag = attribute[0];
	  if ( split[1].indexOf("bold:true") !== -1 )
	    tag = "bold";
	  else if ( split[1].indexOf("italic:true") !== -1 )
	    tag = "italic";
	  else if ( split[1].indexOf("strikethrough:true") !== -1 )
	    tag = "strikethrough";
	  else if ( split[1].indexOf("underlined:true") !== -1 )
	    tag = "underlined";
	  else if ( split[1].indexOf("subscript:true") !== -1 )
	    tag = "subscript";
	  else if ( split[1].indexOf("superscript:true") !== -1 )
	    tag = "superscript";
	  customTagArray.push({"offset": start, "tag": tag, "open": true, "length": length});
	  customTagArray.push({"offset": end, "tag": tag, "open": false, "length": 0});
	}
      });
    }
    customTagArray.sort(function (tagA, tagB) {
      return tagA.offset - tagB.offset;
    });
    return customTagArray;
  }
  
  function getLineDivWithTags(lineUnicode, customData) {
    // TODO Set these somewhere else
    var initialWidth = window.innerWidth;
    var contentLineFontSize = 12;
    // values for creating SVGs with the right height to be used as a background and a 1 px "long" line corresponding to each tag:
    var lineY = Math.round(1.5 * contentLineFontSize);
    var lineThickness = Math.round(lineY / 6);// TODO Test what looks good...
    var thicknessAndSpacing = lineThickness + Math.round(lineY / 8);// TODO Test what looks good...
    var svgRectsJSON = ''; // JSON-2-B with the rect for each line
    var backgroundHeight = lineY; // enough for the first tag graphic
    var tagGfxStack = [];
    // "tags"-2-tags:
    if ("" == lineUnicode)
      return '';
    var customTagArray = getSortedCustomTagArray(customData);

    if (customTagArray.length > 0) {
      customTagArray.forEach(function (tag) { // get a stack with all unique tags present
	var notYetIn = true; // set to false if the tag is already found in the stack
	for (var i = 0; notYetIn && i < tagGfxStack.length; i++) {
	  if (tagGfxStack[i] == tag.tag)
	    notYetIn = false;
	}
	if (notYetIn)
	  tagGfxStack.push(tag.tag);
      });
      // sort the stack and generate a graphical representation for each tag type (placement depends on order and total # of tags)
      tagGfxStack.sort();
      var gapTag = false;
      nonHeightTags = 0;
      tagGfxStack.forEach(function (gfxTag) { // we use initialWidth here and below since it's definitely long enough, except for the "gap" tag
	if ( gfxTag === "gap" ) {// we exclude this special case
	  gapTag = true;
	  nonHeightTags++;
	}
	else if ( gfxTag === "bold" || gfxTag === "italic" || gfxTag === "strikethrough" || gfxTag === "underlined" || gfxTag === "changeFromOriginal" || gfxTag === "subscript" || gfxTag === "superscript" )
	  nonHeightTags++;
	else {
	  svgRectsJSON += '"' + gfxTag + '":' + "\"<rect x=\\\\'0\\\\' y=\\\\'" + lineY + "\\\\' width=\\\\'" + initialWidth + "\\\\' height=\\\\'" + lineThickness + "\\\\' style=\\\\'fill: %23" + tagColors[gfxTag] + ";\\\\' />\""; // # must be %23 and yes \\\\ [sic!]
	  lineY +=thicknessAndSpacing;
	  svgRectsJSON += ',';
	}
      });
      if (gapTag) // insert the "gap" tag, if necessary. This also ensures that we don't have a comma in the end before conversion...
	svgRectsJSON += '"gap":' + "\"<line x1=\\\\'0\\\\' y1=\\\\'0\\\\' x2=\\\\'0\\\\' y2=\\\\'" + lineY + "\\\\' style=\\\\'stroke-width: " + lineThickness + "; stroke: %23" +  (tagColors["gap"]) + ";\\\\' />\""; // # must be %23 and yes \\\\ [sic!]
      else
	svgRectsJSON = svgRectsJSON.substring(0, svgRectsJSON.length - 1); // remove the comma in the end
      svgRectsJSON = JSON.parse("{" +svgRectsJSON + "}");
      // more graphics variables
      var bottomPadding = (1 + (tagGfxStack.length - nonHeightTags)) * thicknessAndSpacing; // nonHeightTags must be subtracted from the count since it shouldn't affect the height
      var backgroundHeight = lineY + bottomPadding;
      // generate lines with spans showing the tags...
      var tagStack = [];
      //  With line no: var tagString = '<li value="' + lineNo + '" spanOffset="0" class="tag-menu ' + (window.location.href.indexOf("view") >= 0 ? 'context-menu-disabled' : '') + '" id="' + prefix + '_' + tagLineId + '" spellcheck="false"' 
	+ '><div style="padding-bottom: ' + bottomPadding + 'px; ' + 'min-height: ' + backgroundHeight + 'px;">';
      var tagString = '<div spanOffset="0" class="tag-menu ' + (window.location.href.indexOf("view") >= 0 ? 'context-menu-disabled' : '') + '" spellcheck="false"' 
	  + '><div style="padding-bottom: ' + bottomPadding + 'px; ' + 'min-height: ' + backgroundHeight + 'px;">';
      var rangeBegin;
      var keepOpenStack = [];
      var previousTag;
      var firstTagOffset = customTagArray[0].offset;
      if (firstTagOffset > 0) {
	var tagContent = lineUnicode.substring(0, firstTagOffset);
	tagString += '<span spanOffset="0">' + tagContent + '</span>';
	rangeBegin = firstTagOffset;
      } else
	rangeBegin = 0;
      customTagArray.forEach(function (tag) {
	var currentTag = tag.tag;
	var offset = tag.offset;
	var length = tag.length; // set this when opening for the first time ONLY, not when reopening (this is from Transkribus custom and has nothing to do with the string lengths between spans...)
	if (offset != rangeBegin || currentTag != previousTag) { // has this tag already been temporarily closed when closing an outer tag? If so, we don't need to open it again, otherwise we must
	  var tagContent = lineUnicode.substring(rangeBegin, offset);
	  while (keepOpenStack.length > 0) {
	    var keepTag = keepOpenStack.pop();
	    var tagDecoration = "background-image: url('data:image/svg+xml; utf8, <svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'" + initialWidth + "\\' height=\\'" + backgroundHeight + "\\'>" + svgRectsJSON[keepTag] + "</svg>');";
	    if ( keepTag.tag === "bold" )
	      tagDecoration = "font-weight: bold;";
	    else if ( keepTag.tag === "italic" )
	      tagDecoration = "font-style: italic;";
	    else if ( keepTag.tag === "strikethrough" )
	      tagDecoration = "text-decoration: line-through;";
	    else if ( keepTag.tag === "underlined" )
	      tagDecoration = "text-decoration: underline;";
	    else if (keepTag.tag === "changeFromOriginal")
	      tagDecoration = "color: blue;";
	    tagString += "<span spanOffset=\"" + rangeBegin + "\" "
	      + "style=\"padding-bottom: " + bottomPadding + "px; " + tagDecoration + "\""
	      + ">";// we use initialWidth here and below because it's guaranteed to be enough
	    if ( keepTag.tag === "subscript" )
	      tagString += "<sub>";
	    else if ( keepTag.tag === "superscript" )
	      tagString += "<sup>";
	    tagStack.push(keepTag);
	  };
	  tagString += '<span spanOffset="' + rangeBegin + '">' + tagContent + '</span>';// we always need the tagLineId
	  if (tag.open) { // if the new tag opens, just insert it and push it onto the stack
	    var tagDecoration = "background-image: url('data:image/svg+xml; utf8, <svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'" + initialWidth + "\\' height=\\'" + backgroundHeight + "\\'>" + svgRectsJSON[currentTag] + "</svg>');";
	    if ( tag.tag === "bold" )
	      tagDecoration = "font-weight: bold;";
	    else if ( tag.tag === "italic" )
	      tagDecoration = "font-style: italic;";
	    else if ( tag.tag === "strikethrough" )
	      tagDecoration = "text-decoration: line-through;";
	    else if ( tag.tag === "underlined" )
	      tagDecoration = "text-decoration: underline;";
	    else if (tag.tag === "changeFromOriginal")
	      tagDecoration = "color: blue;";
	    tagString += "<span offset=\"" + offset + "\" spanOffset=\"" + offset + "\" tagLength=\"" + length +  "\" tag='" + currentTag + "' " //" // a "tag" = span with a tag attribute
	      + "style=\"padding-bottom: " + bottomPadding + "px; " + tagDecoration + "\""
	      + ">";
	    if ( tag.tag === "subscript" )
	      tagString += "<sub>";
	    else if ( tag.tag === "superscript" )
	      tagString += "<sup>";
	    tagStack.push(currentTag);
	  } else { // if the tag closes, we have to close all open tags until we reach the "original" opening tag
	    var precedingTag = tagStack.pop();
	    while (precedingTag && currentTag != precedingTag) {
	      keepOpenStack.push(precedingTag);
	      if ( precedingTag.tag === "subscript" )
		tagString += "</sub></span>";
	      else if ( precedingTag.tag === "superscript" )
		tagString += "</sup></span>";
	      else
		tagString += "</span>"; // easy to close since we don't need to care about what the opening tag type was...
	      precedingTag = tagStack.pop();
	    }
	    if ( tag.tag === "subscript" )
	      tagString += "</sub></span>";
	    else if ( tag.tag === "superscript" )
	      tagString += "</sup></span>";
	    else
	      tagString += "</span>";
	  }
	}
	previousTag = currentTag;
	rangeBegin = offset;
      });
      var remainder = lineUnicode.substring(rangeBegin);
      tagString += '<span spanOffset="' + rangeBegin + '">' + remainder + '</span></div></div>';
      return tagString;
    } else
      return '<div class="tag-menu ' + (window.location.href.indexOf("view") >= 0 ? 'context-menu-disabled' : '') + '" spellcheck="false"><div style="min-height: ' + backgroundHeight + 'px;"><span spanOffset="0">' + lineUnicode + '</span></div></div>';
  }

  return {
    renderLine: function (text, customAttribute) {
        return getLineDivWithTags(text, customAttribute);
    },
    render: function () {

      render();

      if (typeof onSomeOtherCallback === 'function')
        onSomeOtherCallback();

    }
  };
}

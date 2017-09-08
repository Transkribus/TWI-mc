var surroundingCount = 1;
var currentLineId;
var zoomFactor = 0;
var accumExtraX = 0;
var accumExtraY = 0;
var initialWidth, initialHeight, initialScale, naturalWidth;
var previousInnerWidth = window.innerWidth;
var correctModal;
var view = "";
var changed = false;

// i18n vars needed: transUnsavedChanges, transSavingChanges

function calculateAreas() {
	var i = 1;
	$("#transcriptMap").children().each(function (value) {
		var coordString = "";
		for (var j = 0; j < 7; j++) {
			coordString += initialScale*contentArray[i][2][j] + ',';
		}
		coordString += initialScale*contentArray[i][2][7];
		this.coords = coordString;
		i++;
	});
}
function resizeContents() { // Call to perform necessary updates of contents and variables whenever the GUI size is changed
   	var widthFactor = window.innerWidth/previousInnerWidth;
	var oldWidth = initialWidth;
    previousInnerWidth = window.innerWidth;
	initialWidth = $('#transcriptImage').width();
	initialHeight = $('#transcriptImage').height();
	naturalWidth = $('#transcriptImage').get(0).naturalWidth;
	initialScale = initialWidth / naturalWidth;
	// We have to update these too in case the image has gotten resized by the browser along with the window:
	accumExtraX = initialWidth * accumExtraX / oldWidth;
	accumExtraY = initialWidth * accumExtraY / oldWidth;
	$(".transcript-map-div").css("transform",  "translate(" + -accumExtraX +"px, " + -accumExtraY+ "px) scale(" + (1 + zoomFactor) + ")");// Note, the CSS is set to "transform-origin: 0px 0px"
	calculateAreas();
	generateThumbGrid();
	updateCanvas();
	if ( correctModal !== undefined && correctModal.isOpen() ) {
		updateDialog();
		updateDocking();
	}
}
function getContent() { // "JSON.stringifies" (verbing a noun) contentArray and also strips out content which does not need to be submitted.
	var lengthMinusOne = contentArray.length - 1;
	var content = '{';
	for (var cI = 1; cI <= lengthMinusOne; cI++) {// cI = 1 because we skip the "line" which isn't real since it's the top of the page
		var unicode = contentArray[cI][1].replace('"', '\\"');
		content += '"' + contentArray[cI][0] + '": {"Unicode":"' + unicode + '","custom":"' + contentArray[cI][4] + '"}';
		if (cI < lengthMinusOne)
			content += ',';
	}
	content += '}';
	console.log("custom content: " + content);
	return content;
}
function saveChanges(e) {
	if (arguments.length == 1)
		e.preventDefault();
	setMessage('<div class="alert alert-warning">' + transSavingChanges + '</div>');
	$.post(window.location.href, {content: getContent(), csrfmiddlewaretoken: csrf_token}, function( data ) {
		setMessage(data);
		changed = false;
	});
	// TODO Handle failures here or are we happy with the current solution?
}

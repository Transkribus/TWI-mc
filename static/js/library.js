console.log("IN LIBRARY.JS");
console.log(window.location.pathname);
//We strip off the ids and should have a useful app base that will work for any server context
var appbase = window.location.pathname.replace(/\/\d+(|\/)/g, "");
//var serverbase = window.location.pathname.replace(/\/\w+\/\d+(|\/)/g, ""); //nb expects slash
//our urls will be like this:
// domain.com/serverbase/appname/id/id/id/id/action
// remove from the back nothing after word that *should* == appname and anything after it (to get server base)
var serverbase = window.location.pathname.replace(/\/\w+(|\/|\/\d.*)$/g, ""); 

console.log("APPBASE: ",appbase);
console.log("SERVERBASE: ",serverbase);

$(document).ready(function(){

	init_collections_table();
	init_documents_table();
	init_pages_thumbs();
});
function make_url(url){
//	appbase = appbase.replace(/\/$/,""); //remove trailing slash from appbase
//	return appbase+url;
	//we will switch to using serverbase as we may need to call ajax views across the constituent apps
	//NB this change means the app that the view is from must be specigied in the url
	serverbase = serverbase.replace(/\/$/,""); //remove trailing slash from appbase
	return serverbase+url;

}
function init_collections_table(){

	if(!$("#collections_table").length) return;

	var url = make_url("/utils/table_ajax/collections");
	var columns =  [
		    //This column will be for our image which we will not get from the table_ajax/collections view
		    //We may need to divise some darstedly view especially for getting a single image from a collection or document
		    //One thing is sure if we start make full doc calls in side collection loops we will be waiting a long time
		//,
	     // "render" : function(data, type, row){
		//		return '<a href="'+row.colId+'">'+data+'</a>';
		//	} --> was after colName
		    { "data": "colId",
		      "searchable": false, 
		      "orderable": false
 		    },
		    { "data" : "colName",  //insert colName as default for search and order #bigupSchorsch
		      "defaultContent": '<span class="glyphicon glyphicon-refresh glyphicon-spin"></span>', 
//		      "searchable": false, 
//		      "orderable": false
			},
		    { "data": "nrOfDocuments" },
       /* nrOfDOcument has disappeared from the data for some reason... until it found render this field as empty to stop warnings
                    { "data": "nrOfDocuments", "data": null, "defaultContent": '<span></span>'},*/
		    { "data": "role" },
        	];
	var datatable = init_datatable($("#collections_table"),url,columns);
	
	$("#collections_table").on( 'draw.dt', function () {
	    var api = new $.fn.DataTable.Api( "#collections_table" );
		row_data = [];
		//rowIdx is the index of this row before the sort/search, rowLoop contains the (current) idx of the row after the sort
		api.rows({page:'current'}).every( function ( rowIdx, tableLoop, rowLoop ) {

			var d = this.data();
		    this.invalidate('dom');
		    var currRow = this;

			$("#collections_table tbody tr").each(function(rowInd){
		    	if (rowLoop == rowInd){

		    		// alert(Object.keys(currRow.data()));

					row_data[rowInd] = {} ;
					row_data[rowInd].collId = currRow.data().colId;
					row_data[rowInd].url = make_url("/utils/thumb/"+row_data[rowInd].collId);
					row_data[rowInd].collStat = make_url("/library/coll_statistics/"+row_data[rowInd].collId);
					row_data[rowInd].img_cell = this;
					$.getJSON(row_data[rowInd].url, function(thumb_data){
						if (thumb_data.url){
							thumb = loadThumbs(thumb_data.url);
							$("td:eq(0)", row_data[rowInd].img_cell).empty();
							$("td:eq(0)", row_data[rowInd].img_cell).append(thumb);
							$("td:eq(0)", row_data[rowInd].img_cell).addClass('text-center');
						}else{
							$("td:eq(0)", row_data[rowInd].img_cell).html('No image available');
						}
					}).done(function(a,b) {
//					    console.log( "Done: ",a, " ",b );
					}).fail(function( a, b){
					    console.log( "Fail: ",a, " ",b );
					});


					row_data[rowInd].collStat = make_url("/library/coll_statistics/"+row_data[rowInd].collId);
					$.getJSON(row_data[rowInd].collStat, function(stat_data){
						$("td:eq(1)", row_data[rowInd].img_cell).html(stat_data.titleDesc);
						shorten_text("long_text_" + row_data[rowInd].collId);
						
						//Append a jump to link last accessed data from utils/collection_recent
						//We do this in the success func so we make sure the title and description goes first	
						row_data[rowInd].recent = make_url("/utils/collection_recent/"+row_data[rowInd].collId);
						$.getJSON(row_data[rowInd].recent, function(recent_data){
							render_jumpto(recent_data, rowInd, 1);
						}).done(function(a,b) {
//						    console.log( "Done: ",a, " ",b );
						}).fail(function( a, b){
						    console.log( "Fail: ",a, " ",b );
						});

					}).done(function(a,b) {
//					    console.log( "Done: ",a, " ",b );
					}).fail(function( a, b){
					    console.log( "Fail: ",a, " ",b );
					});

		    	}
			});
		});
	});

}

function init_documents_table(){

	if(!$("#documents_table").length) return;

//	var url = "./table_ajax/documents/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1');
	var url = make_url("/utils/table_ajax/documents/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1'));

	var ids = parse_path();	

	var columns =  [
		    //This column will be for our image which we will not get from the table_ajax/document view
		    //The columns with null data are loaded by ajax on draw.dt (see below) Becuase of this they cannot be searched or ordered
		    { "data": "docId",
		      "defaultContent": '<span class="glyphicon glyphicon-refresh glyphicon-spin"></span>',
		      "searchable": false, 
		      "orderable": false },
		    { "data" : null, 
		      "searchable": false, 
		      "orderable": false},
		    { "data": "title",    //load with title for sorting and ordering (though this gets replaced with secondary ajax (see below)
		      "defaultContent": '<span class="glyphicon glyphicon-refresh glyphicon-spin"></span>',
//		      "searchable": false, 
//		      "orderable": false
			},
		    { "data": null,
		      "searchable": false ,
		      "orderable": false},
		    { "data" : "nrOfPages"}
        	];

	var datatable = init_datatable($("#documents_table"),url,columns);
			
	//redraw handled here: may an easier solution to get current docID after a sort/search exist but this one works fine for the moment
	$("#documents_table ").on( 'draw.dt', function () {
		
	    var api = new $.fn.DataTable.Api( "#documents_table" );
		row_data = [];
		//rowIdx is the index of this row before the sort/search, rowLoop contains the (current) idx of the row after the sort
		api.rows({page:'current'}).every( function ( rowIdx, tableLoop, rowLoop ) {

		    var d = this.data();
		    this.invalidate('dom');
		    var currRow = this;
		    
/*		    console.log( "rowIdx: ", rowIdx);
		    console.log( "rowLoop: ", rowLoop);
		    console.log( "currRow: ", currRow.data().docId);*/
		    
		    //this way we can only go throug the indizes of the first page before the change during sort/search
		    $("#documents_table tbody tr").each(function(rowInd){
		    	
		    	//console.log( "rowInd: ", rowInd);
		    	if (rowLoop == rowInd){
		    				 
					row_data[rowInd] = {} ;
					row_data[rowInd].docId = currRow.data().docId;
					row_data[rowInd].url = make_url("/utils/thumb/"+ids['collId']+'/'+row_data[rowInd].docId);
					row_data[rowInd].img_cell = this;
					$.getJSON(row_data[rowInd].url, function(thumb_data){
						thumb = loadThumbs(thumb_data.url);
						$("td:eq(0)", row_data[rowInd].img_cell).empty();
						$("td:eq(0)", row_data[rowInd].img_cell).append(thumb);
						$("td:eq(0)", row_data[rowInd].img_cell).addClass('text-center');
					}).done(function(a,b) {
					    console.log( "Done: ",a, " ",b );
					}).fail(function( a, b){
					    console.log( "Fail: ",a, " ",b );
					});

					row_data[rowInd].stats = make_url("/library/statistics/"+ids['collId']+'/'+row_data[rowInd].docId);
					$.getJSON(row_data[rowInd].stats, function(stat_data){
						$("td:eq(2)", row_data[rowInd].img_cell).html(stat_data.titleDesc);
						$("td:eq(3)", row_data[rowInd].img_cell).html(stat_data.statString);
						$("td:eq(1)", row_data[rowInd].img_cell).html(stat_data.viewLinks);

						shorten_text("long_text_" + row_data[rowInd].docId);
						//Append a jump to link last accessed data from utils/collection_recent
						//We do this in the success func so we make sure the title and description goes first	
						row_data[rowInd].recent = make_url("/utils/document_recent/"+row_data[rowInd].docId);
						$.getJSON(row_data[rowInd].recent, function(recent_data){
							render_jumpto(recent_data, rowInd, 2);
						}).done(function(a,b) {
//						    console.log( "Done: ",a, " ",b );
						}).fail(function( a, b){
						    console.log( "Fail: ",a, " ",b );
						});

					}).done(function(a,b) {
					    console.log( "Done: ",a, " ",b );
					}).fail(function( a, b){
					    console.log( "Fail: ",a, " ",b );
					});
			    }
		    });
		});
	});
}

function init_pages_table(){

//	var url = "./table_ajax/pages"+window.location.pathname.replace(/^.*\/(\d+\/\d+)$/, '$1');
	var url = make_url("/utils/table_ajax/pages"+window.location.pathname.replace(/^.*\/(\d+\/\d+)$/, '$1'));



	var ids = parse_path();	

	var columns =  [
		    { "data": "pageId" },
		    { "data": "pageNr" },
		    { "data": "thumbUrl" },
		    { "data": "status" },
		    { "data": "nrOfTranscripts" },
        	];
	init_datatable($("#pages_table"),url,columns);

}

function init_pages_thumbs(){
	// NB This paging is managed on django until we can do so on transkribus rest
	// would be great to manage page size and pages with datatable... but this is not a datatable....
	if(!$("#pages_thumbnail_grid").length) return;

	var start = 0;
	var length = 12;
	get_thumbs(start,length);
	
	$("body").on("change","select[name='pages_thumb_length']",function(){
		var start = parseInt($("#thumb_pagination .paginate_button.current").attr("href"));
		var length = parseInt($(this).val());
		if(length >= parseInt($("#pages_thumb_info").data("thumb-total"))) start = 0;
		get_thumbs(start,length);
	});
	$("body").on("click",".paginate_button",function(){
		if($(this).hasClass("disabled")) return false;
		
		var start = parseInt($(this).attr("href"));
		var length = parseInt($("select[name='pages_thumb_length']").val())
		if($(this).attr("href") === "previous"){ 
			start = parseInt($("#thumb_pagination .paginate_button.current").attr("href"))-length; 
		}
		if($(this).attr("href") === "next"){ 
			start = parseInt($("#thumb_pagination .paginate_button.current").attr("href"))+length; 
		}

		get_thumbs(start,length);
		return false;
	});

}

function shorten_text(element_id) {
	$('#'+element_id).each(function(event){ /* select all divs with the item class */
		var max_length = 150; /* set the max content length before a read more link will be added */
		
		if($(this).html().length > max_length){ /* check for content length */
			var short_content 	= $(this).html().substr(0,max_length); /* split the content in two parts */
			var long_content	= $(this).html().substr(max_length);
			
			$(this).html(short_content+
						 '<a href="#" class="read_more"><br/>More...</a>'+
						 '<span class="more_text" style="display:none;">'+long_content+'</span>'); /* Alter the html to allow the read more functionality */
						 
			$(this).find('a.read_more').click(function(event){ /* find the a.read_more element within the new html and bind the following code to it */
				event.stopPropagation(); /* prevent the a from changing the url */
				$(this).hide(); /* hide the read more button */
				$(this).parents('#'+element_id).find('.more_text').show(); /* show the .more_text span */
			});
		}
	});
};
function render_jumpto(recent_data,rowInd,colInd){

	if (recent_data[0]){
		pageNr = recent_data[0].pageNr;
		docId = recent_data[0].docId;
		docName = recent_data[0].docName;
                view_url = make_url('/view/'+row_data[rowInd].collId+'/'+docId+'/'+pageNr);
                $("td:eq("+colInd+")", row_data[rowInd].img_cell).append('<p>Jump to <a href="'+view_url+'">page '+pageNr+' of '+docName+'</a></p>');
	}
}
// $('.automatic_resize').one('load', function() {
// 	// alert('o_O'):
//   // console.log($(this).width);
// }).each(function() {
//   if(this.complete) $(this).load();
// });
function loadThumbs(url) { // Loads all thumbs and shows the ones which are visible as soon as they've been loaded
	tempImg = new Image();
	tempImg.src = url;
	tempImg.onload = function() {
		// alert(tempImg);
		// alert(tempImg.clientWidth);
		if(this.clientWidth > this.clientHeight)
		{
			this.width  = 120;
			this.height = 90;
		}else{
			this.width  = 90;
			this.height = 120;
		}
	};
	return tempImg;
}


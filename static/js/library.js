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
		    { "data" : null,
		      "defaultContent": '<span class="glyphicon glyphicon-refresh glyphicon-spin"></span>'}, 
		      "searchable": false, 
		      "orderable": false
		    { "data": "colId" },
		    { "data": "colName"},
		    { "data": "description" },
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
					 
					row_data[rowInd] = {} ;
					row_data[rowInd].collId = currRow.data().colId;
					console.log( "TestAusgabe docId: ", row_data[rowInd].collId);
			
					//console.log(datatable.cell(rowInd,0).data().colId);
					//row_data[rowInd].collId = datatable.cell(rowInd,0).data().colId;
					row_data[rowInd].url = make_url("/utils/thumb/"+row_data[rowInd].collId);
					row_data[rowInd].img_cell = this;
					$.getJSON(row_data[rowInd].url, function(thumb_data){
						$("td:eq(0)", row_data[rowInd].img_cell).html('<img src="'+thumb_data.url+'"/>');
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

function init_documents_table(){

	if(!$("#documents_table").length) return;

//	var url = "./table_ajax/documents/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1');
	var url = make_url("/utils/table_ajax/documents/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1'));

	var ids = parse_path();	

	var columns =  [
		    //This column will be for our image which we will not get from the table_ajax/document view
		    { "data" : null, 
		      "defaultContent": '<span class="glyphicon glyphicon-refresh glyphicon-spin"></span>'}, 
		    { "data": "docId" },
		    { "data": "title" },
		    { "data": "desc" },
		    { "data": "author" },
		    { "data": "nrOfPages" },
		    { "data": "language" },
		    { "data" : null, 
		      "defaultContent": '<span class="glyphicon glyphicon-refresh glyphicon-spin"></span>'},
		    //{ "data": "new_key" },//if we want to add a new column in this table
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
					console.log( "TestAusgabe docId: ", row_data[rowInd].docId);
					
					row_data[rowInd].url = make_url("/utils/thumb/"+ids['collId']+'/'+row_data[rowInd].docId);
					row_data[rowInd].stats = make_url("/library/statistics/"+ids['collId']+'/'+row_data[rowInd].docId);
					row_data[rowInd].img_cell = this;
					$.getJSON(row_data[rowInd].url, function(thumb_data){
						$("td:eq(0)", row_data[rowInd].img_cell).html('<img src="'+thumb_data.url+'"/>');
					}).done(function(a,b) {
					    console.log( "Done: ",a, " ",b );
					}).fail(function( a, b){
					    console.log( "Fail: ",a, " ",b );
					});
					$.getJSON(row_data[rowInd].stats, function(stat_data){
						$("td:eq(7)", row_data[rowInd].img_cell).html('<p>"'+stat_data.docStatString+'"</p><p>"'+stat_data.tagsString+'"</p>');
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



/* globals... */
var data_cache = {};
var charts = {};
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
	$('#errorModal').modal({ show: false})

});
function make_url(url){
//	appbase = appbase.replace(/\/$/,""); //remove trailing slash from appbase
//	return appbase+url;
	//we will switch to using serverbase as we may need to call ajax views across the constituent apps
	//NB this change means the app that the view is from must be specigied in the url
	serverbase = serverbase.replace(/\/$/,""); //remove trailing slash from appbase
	return serverbase+url;

}

function init_datatable(table,url, columns){
	var datatable = table.DataTable({
		"ordering": true,
		"processing": true,
        "serverSide": false,
        "filter": true,
        "searching": true,
        "search": {},
		"ajax": {
			"url": url,
			"data": function ( d ) {
				if($("#slider-range").data("uiSlider")){
					return $.extend( {}, d, { 
						"start_date": ($("#slider-range").slider("option", "values")[0]*1000),
						"end_date":($("#slider-range").slider("option", "values")[1]*1000) ,
					});
				}
			},
			"error": function (xhr, error, thrown) {
				$(table.selector+'_processing').hide();
				if(xhr.status == 401){ //unauthorised response from transkribus... we should forward to logout
					//but with a message on the login page... somehow
					window.location.href = make_url("/logout/?next="+window.location.pathname)
				}else{
					//otherwise notify user of the error 
					$.notify({
						// options
						message: "There was a problem communicating with Transkribus.<br/>Error code: "+xhr.status+ " : "+thrown,
						},{
						// settings
						type: 'danger'
		 			});
				}
			},
		},		
//		"sDom": "rltip",
		"oLanguage": {
			"sProcessing": 'Retrieving data from transkribus <span class="glyphicon glyphicon-refresh glyphicon-spin"></span>',
		},
		"dom": '<"top"f>rt<"bottom"lip><"clear">',
		"length" : 5,
		"lengthMenu": [ 5, 10, 20, 50, 100 ],
		//ordering should be handled server side
		//"ordering": false,  //still not sure about this
		"columns": columns,
		"createdRow": function ( row, data, index ) {
                	$(row).addClass("clickable");
			//make rows click through to wheresoever they have an id for (col,doc,page)
                	$(row).on("click", function(){ 
				//TODO TODO make these linked rows work for user table
				//TODO this works but feels messy (need to shift that n/a crap from the data for one)
				var ids = parse_path();	
				var colId = null;
				var url = null;
				if(data.colId != undefined && data.colId !== "n/a")
					colId = data.colId;
				if(ids.collId != undefined && ids.collId)
					colId = ids.collId;

				if(colId) url = colId;
				if(data.docId != undefined && data.docId !== "n/a"){
					url += '/'+data.docId;
					if (appbase.includes("library")){
						appbase = appbase.replace("library", "edit/correct")
						url += '/'+1;
					}
				}
				if(data.pageNr != undefined && data.pageNr !== "n/a"){ //NB will break until we use base url
					url = serverbase+'/edit/correct/'+data.colId+'/'+data.docId+'/'+data.pageNr;	
					if(serverbase !== "") url = '/'+url;
				 	window.location.href=url;
					return false;
					
				}
				//TODO add case for userlist links 
				if(table.selector.match(/users/)){
					url += '/u/'+data.userName;
				}

				if(url){
					if(appbase.match(/\/$/)) loc = appbase+url; else loc = appbase+'/'+url;
					window.location.href=loc;
				}
			});
        	},

	});
	$(".table_filter").on("click", function(){
		console.log("filter value: ",this.value);
//		This search does not work now that all data is loaded to client
//		Also changing the number of columns would need to be handled which it is not at present
//		 datatable.columns( 5 ).search( this.value ).draw();
//		This search will, but is not limited to column so there is a risk it will show rows where "title =~ /Save/" etc
		 datatable.search( this.value ).draw();
		return false;
	});
	$(table).on( 'draw.dt', function () {
		$("#"+$(table).attr("id")+"_count").html(datatable.page.info().recordsTotal);
	} );
	return datatable;
}

function init_list(list_id,url){
	if(data_cache[url]){ // here we check cache
		make_list(list_id,data_cache[url]);
	}

	$.ajax({
	    'type': 'GET',
    	    'url': url,
	    'data': {length: -1}, //insist on all values...?
            'dataType': 'json',
            'success': function (data) {
		data_cache[url] = data; //cache the cahrt data as it is generally much bigger
		make_list(list_id,data);
 	     },
	     "error": function (xhr, error, thrown) {
			$('#errorModal').modal('show').on('shown.bs.modal', function () {
				$('.modal-body', this).html("Sorry, it looks like there was a problem communicating with Transkribus.<br/>Error code: "+xhr.status+ " : "+thrown);
			});
		},

	});
}	
function make_list(list_id,data){

	$("#"+list_id).html(""); //clearout
	
	if(data.data!==undefined && data.data.length == 0){
		$("#"+list_id).append('<li><a href="#" onclick="return false;">User data unavailable</a></li>');
	}

	for(i in data.data){
		$("#"+list_id).append('<li data-userid="'+data.data[i].userId+'"><a href="#'+list_id+'_panel" data-toggle="tab">'+data.data[i].userName+'</a></li>');
	}

	$("#"+list_id+" > li").on("click", function(){
		console.log("load user data for...?", this, $("a", this).attr("href"), $(this).data("userid") );
		init_user_actions_chart( $(this).data("userid"),"user_actions_line_x");
	});
}
function init_chart(canvas_id,url,chart_type){
//	console.log("url: ",url);
//	console.log("ccanvas: ",canvas_id);

	//Collect date parameters from slider
	var params = {"start_date": ($("#slider-range").slider("option", "values")[0]*1000),
		"end_date":($("#slider-range").slider("option", "values")[1]*1000)};

	$.ajax({
	    'type': 'GET',
    	    'url': url,
	    'data': params,
            'dataType': 'json',
	    "error": function (xhr, error, thrown) {
			$(table.selector+'_processing').hide();
			if(xhr.status == 401){ //unauthorised response from transkribus... we should forward to logout
				//but with a message on the login page... somehow
				window.location.href = make_url("/logout/?next="+window.location.pathname)
			}else{
				//otherwise notify user of the error 
				$.notify({message: "There was a problem communicating with Transkribus.<br/>Error code: "+xhr.status+ " : "+thrown,},
					{type: 'danger'});
			}
		},
            'success': function (data) {
		data_cache[url] = data; //cache the cahrt data as it is generally much bigger

		if(data.labels.length == 0 && data.datasets.length ==0){
			//console.log(data.labels,data.datasets)
			//TODO tigger panel so we can see a message
			$.notify({message: "This chart appears to have no data."},
					{type: 'warning'});
			$("#"+canvas_id).html("No data available");
		}
		if(chart_type == 'bar')
			Chart.defaults.global.legend.display = false;
		else
			Chart.defaults.global.legend.display = true;
		charts[canvas_id] = new Chart(document.getElementById(canvas_id).getContext('2d'), {
		    type: chart_type,
		    data: data,
/* options: {
        legend: {
            onClick : function(event, legendItem)  { console.log("legend clicked\n")}
        }
    }
*/
 		});


		$("#"+canvas_id).on("click",
		    function(e){
			//where appropriate we can navigate by clicking on chart bar/lines/segmments
			//only tested for collection bars presently
			var chart =  charts[canvas_id];
	        
			activeElement = chart.getElementAtEvent(e);
			if(activeElement[0] == undefined) return; //not clicked on a dataset
			var clicked_value = data.datasets[activeElement[0]._datasetIndex].data[activeElement[0]._index];
			var clicked_label = data.labels[activeElement[0]._index];
			if(data.label_ids == undefined) return; //no label ids avialable for forwarding
			var clicked_id = data.label_ids[activeElement[0]._index];

			var ids = parse_path();
			var url = "/dashboard";
			var context = '';
			for(x in ids){
				context += '/'+ids[x];
			};
			if(canvas_id == 'top_users'){	
				url += context+'/u/'+clicked_label;
			}else{
				url += context+'/'+clicked_id;
			}

//			console.log("CLICK: ",clicked_id);
//			console.log("URL: ",url);
		 	window.location.href=make_url(url);
		    }
		);  

	    }
	});

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
function get_thumbs(start,length){
	var ids = parse_path();	
	var url = make_url("/utils/table_ajax/pages/"+ids['collId']+'/'+ids['docId']);

//	console.log("get_thumbs, URL: ",url);

	$.ajax({
	    type: 'GET',
    	    url: url,
	    data: {length: length, start: start},
            dataType: 'json',
            success: function (data) {
		//console.log(data);	
		length_menu = [ 12, 24, 48, 96 ];
		var menu = $('<div><label>Show <select name="pages_thumb_length"></select></label></div>');

		for(i in length_menu){
			var option=$('<option value="'+length_menu[i]+'">'+length_menu[i]+'</option>');
			if(length == length_menu[i]) $(option).attr("selected","selected");
			$("select[name='pages_thumb_length']", menu).append(option);
		}
		var row_html = '<div class="row"></div>';
		var row = $(row_html);
		for(x in data.data){
			var status_label = data.data[x].status.ucfirst().replace(/_/," ");
			var thumb = $('<div class="col-md-2"><a href="'+serverbase+'/edit/correct/'+ids['collId']+'/'+ids['docId']+'/'+data.data[x].pageNr+'" class="thumbnail '+data.data[x].status+'"><img src="'+data.data[x].thumbUrl+'"><div class="thumb_label">'+status_label+'</div></a></div>');
			$(row).append(thumb);
		}
		$("#pages_thumbnail_grid").html(menu);
		$("#pages_thumbnail_grid").append(row);
		var end = start+length;
		if(end > data.recordsTotal) end = data.recordsTotal;
		$("#pages_thumbnail_grid").append('<div class="dataTables_info" id="pages_thumb_info" data-thumb-total="'+data.recordsTotal+'">Showing '+start+' to '+end+' of '+data.recordsTotal+'</div>');

		if(length<data.recordsTotal){
			paginate("pages_thumbnail_grid",start,length,data.recordsTotal);
		}
           }
	});

}
//emulates the dataTables pagination for things that aren't tables, but need paginated (ie thumbgrids)
function paginate(id,start,length,total){
	var paginate_html = '<div class="dataTables_wrapper"><div class="dataTables_paginate paging_simple_numbers" id="thumb_pagination">'+
	'<a href="previous" id="pages_thumb_previous" class="paginate_button previous">Previous</a>'+
	'<span></span>'+
	'<a href="next" id="pages_thumb_next" class="paginate_button next">Next</a></div></div>';
	var paginate = $(paginate_html);
	var pages = Math.round(total/length)+1;
	var show_page_limit = 5;
	var curr_page = current_page(start,length);
	for(page=1; page<pages; page++){
	//	var curr_page = page*length;
		if(pages > show_page_limit){
			var onwards = true;
			if((page+1) == curr_page) onwards = false;
			if((page-1) == curr_page) onwards = false;
			if(page == curr_page) onwards = false;
			if(curr_page < show_page_limit && page <= show_page_limit) onwards = false;
			if(curr_page > (pages-show_page_limit) && page >= (pages-show_page_limit)) onwards = false;
			if(page == (pages-1)) onwards = false;
			if(page == 1) onwards = false;
			if(onwards) continue;
		}
		var p = $('<a href="'+((page-1)*length)+'" class="paginate_button">'+page+'</a>');

		if(page== (pages-1) && curr_page <= (pages-show_page_limit))
			$("span[class!='elipses']", paginate).append('<span class="elipses">...</span>');
		$("span[class!='elipses']", paginate).append(p);
		if(page== 1 && curr_page >= show_page_limit)
			$("span[class!='elipses']", paginate).append('<span class="elipses">...</span>');

		if(page == curr_page)
			$(p).addClass("current").siblings("a").removeClass("current");

	};
	if(start == 0 ) { $("#pages_thumb_previous",paginate).addClass("disabled"); }
	if(start+length >= total ) { $("#pages_thumb_next",paginate).addClass("disabled"); }

	$("#"+id).append(paginate);

}
function current_page(start,length){
	return Math.floor(start/length)+1;
}

String.prototype.ucfirst = function() {
    return this.charAt(0).toUpperCase() + this.slice(1).toLowerCase();
}

function parse_path(){
	
	var pattern = /\/\w+(|\/(\d+)(|\/(\d+)(|\/(\d+))))(|\/u\/.+)$/;
	var result = pattern.exec(window.location.pathname);
//	console.log("pattern result " + result)
	ids = {};
	if(result != null && result[2]) ids['collId'] = result[2];
	if(result != null && result[4]) ids['docId'] = result[4];
	if(result != null && result[6]) ids['pageId'] = result[6];

	return ids;
}
/* Collections */

glyph_opts = {
    map: {
      doc: "glyphicon glyphicon-file",
      docOpen: "glyphicon glyphicon-file",
      checkbox: "glyphicon glyphicon-unchecked",
      checkboxSelected: "glyphicon glyphicon-check",
      checkboxUnknown: "glyphicon glyphicon-share",
      dragHelper: "glyphicon glyphicon-play",
      dropMarker: "glyphicon glyphicon-arrow-right",
      error: "glyphicon glyphicon-warning-sign",
      expanderClosed: "glyphicon glyphicon-plus-sign",
      expanderLazy: "glyphicon glyphicon-plus-sign",  // glyphicon-expand
      expanderOpen: "glyphicon glyphicon-minus-sign",  // glyphicon-collapse-down
      folder: "glyphicon glyphicon-folder-close",
      folderOpen: "glyphicon glyphicon-folder-open",
      loading: "glyphicon glyphicon-refresh"
    }
  };

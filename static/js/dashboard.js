
console.log("IN DASHBOARD.JS");
console.log("APPBASE: ",appbase);
console.log("SERVERBASE: ",serverbase);

$(document).ready(function(){
	$("#id_language").on("change keyup", function () {
		$(this).closest("form").submit();
	});
	actions_table = init_actions_table();
	init_date_inputs(actions_table);
	init_actions_chart();
	init_user_actions_chart();
	init_top_users_chart();
	init_top_collections_chart()

	init_user_list();

	init_collections_table();
	init_users_table();
	init_documents_table();
//	init_pages_table();
	init_pages_thumbs();

	init_chart_filters();
});
function init_date_inputs(actions_table){

    var min = new Date('2016.01.01').getTime() / 1000;
    var max = new Date().getTime() / 1000;

    var slider = $( "#slider-range" ).slider({
      range: true,
      min: min, //seconds
      max: max,
      step: 86400,
      values: [ min, max ],
      slide: function( event, ui ) {
        $( "#start_date" ).val( (new Date(ui.values[ 0 ] *1000).toDateString() ) );
        $( "#end_date" ).val( (new Date(ui.values[ 1 ] *1000)).toDateString() );
      },
      change: function(event, ui){
	//if the slider values change we reload the data table...
	actions_table.ajax.reload();
      }
    });
    $( "#start_date" ).datepicker({"dateFormat":"D M dd yy", "onSelect": function(date){
		console.log("start date picker onSelect");
		slide_end = slider.slider("option", "values")[1];
		slider.slider( "option", "values", [($(this).datepicker("getDate")/1000),slide_end] );
	}}).val(new Date(min*1000).toDateString());
    $( "#end_date" ).datepicker({"dateFormat":"D M dd yy","onSelect": function(date){
		console.log("end date picker onSelect");
		slide_start = slider.slider("option", "values")[0];
		slider.slider( "option", "values", [slide_start,($(this).datepicker("getDate")/1000)] );
	}}).val(new Date(max*1000).toDateString());

}
function init_actions_table(){

	if(!$("#actions_table").length) return;

	var ids = parse_path();
	var url = make_url("/utils/table_ajax/actions");
	console.log("Using appbase: ",url);

//	var url = "./table_ajax/actions";
	var context = '';
	for(x in ids){
		console.log(x," => ",ids[x])
		context += '/'+ids[x];
	};
	url += context;
	console.log("URL: ",url);
	var columns =  [
		    { "data": "time",
		      "render" : function(data, type, row){
				if(data === "n/a") return data;
				var date = new Date(data);
				return date.toDateString();
			},
		    },
		    { "data": "colId", "visible": false },
		    { "data": "colName" },
		    { "data": "docId", "visible": false  },
		    { "data": "docName" },
		    { "data": "pageId", "visible": false  },
		    { "data": "pageNr" },
		    { "data": "userName" },
		    { "data": "type" }
        	];
	return init_datatable($("#actions_table"),url,columns);
}

function init_users_table(){

	if(!$("#users_table").length) return;

	var ids = parse_path();
	var url = make_url("/utils/table_ajax/users");

	var context = '';
	for(x in ids){
		context += '/'+ids[x];
	};
	url += context;
	var columns =  [
		    { "data": "userId", "visible": false  },
		    { "data": "userName"},
		    { "data": "firstname" },
		    { "data": "lastname" },
		    { "data": "email" },
		    { "data": "affiliation" },
		    { "data": "created",
		      "render" : function(data, type, row){
				if(data === "n/a") return data;
				var date = new Date(data);
				return date.toDateString();
			},
		    },
		    { "data": "role" },
        	];
	return init_datatable($("#users_table"),url,columns);
}
function init_collections_table(){

	if(!$("#collections_table").length) return;

	var url = make_url("/utils/table_ajax/collections");

	var columns =  [
		    { "data": "colId" },
		    { "data": "colName",
		      "render" : function(data, type, row){
				return '<a href="'+row.colId+'">'+data+'</a>';
			} 
		    },
		    { "data": "description" },
		    { "data": "role" },
        	];
	init_datatable($("#collections_table"),url,columns);
}

function init_documents_table(){

	if(!$("#documents_table").length) return;

//	var url = "./table_ajax/documents/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1');
	var url = make_url("/utils/table_ajax/documents/"+window.location.pathname.replace(/^.*\/(\d+)$/, '$1'));

	var ids = parse_path();	

	var columns =  [
		    { "data": "docId" },
		    { "data": "title" },
		    { "data": "author" },
		    { "data": "uploadTimestamp",
		      "render" : function(data, type, row){
				var date = new Date(data)	
				return date.toDateString();
			} 
		    },
		    { "data": "uploader" },
		    { "data": "nrOfPages" },
		    { "data": "language" },
		    { "data": "status" },
        	];
	init_datatable($("#documents_table"),url,columns);
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

function init_actions_chart(){

	if(!$("#actions_line").length) return;
	ids=parse_path();
//	var url = static_url+"/dashboard/chart_ajax/actions/line";
	var url = make_url("/dashboard/chart_ajax/actions/line");

	for(id in ids){
		url += '/'+ids[id];
	}
	init_chart("actions_line",url,"line");

}

//TODO propogate / better integrate this
function init_user_actions_chart(userid,canvas_id){

	if(canvas_id == undefined) canvas_id = "user_actions_line";
	if(!$("#"+canvas_id).length) return;
	ids=parse_path();
	//userid is set in header template and is the current_userid of currently logged in user
//	console.log("USERNAME: ",current_userid);
	if(userid == undefined) userid = current_userid;
//	var url = static_url+"/dashboard/chart_ajax/u/"+userid+"/actions/line";
	var url = make_url("/dashboard/chart_ajax/u/"+userid+"/actions/line");

	for(id in ids){
		url += '/'+ids[id];
	}
	init_chart(canvas_id,url,"line");
}

function init_top_users_chart(){

	if(!$("#top_users").length) return;
	ids=parse_path();
//	var url = static_url+"/dashboard/chart_ajax/actions/top_bar/userId/userName";
	var url = make_url("/dashboard/chart_ajax/actions/top_bar/userId/userName");

	for(id in ids){
		url += '/'+ids[id];
	}
	init_chart("top_users",url,"bar");
}

function init_top_collections_chart(){

	if(!$("#top_collections").length) return;
	ids=parse_path();
//	var url = static_url+"/dashboard/chart_ajax/actions/top_bar/colId/colName";
	var url = make_url("/dashboard/chart_ajax/actions/top_bar/colId/colName");

	init_chart("top_collections",url,"bar");
}

function init_doughnut(){

	if(!$("#status_doughnut").length) return;
	ids=parse_path();
//	var url = static_url+"/dashboard/chart_ajax/actions/top_bar/userId/userName";
	var url = make_url("/dashboard/chart_ajax/status/doughnut");

	for(id in ids){
		url += '/'+ids[id];
	}
	init_chart("top_users",url,"doughnut");
}



function init_user_list(){
	if(!$("#user_list").length) return;
	ids=parse_path();
//	var url = static_url+"/dashboard/table_ajax/users"; //use table data with -1... *nascent* javascript caching... will need to use url+paramss to stop pollution
	var url = make_url("/utils/table_ajax/users"); //use table data with -1... *nascent* javascript caching... will need to use url+paramss to stop pollution

	for(id in ids){
		url += '/'+ids[id];
	}
	init_list("user_list",url);
}

function init_chart_filters(){

	$(".table_filter").on("click", function(){
		active_canvas = $(".tab-pane.active > canvas").attr("id");
		console.log("table_filter CLICKED",active_canvas);

		if($("#"+active_canvas).length==0) return false;

		var chart =  charts[active_canvas];
		//TODO the hiding needs to be inversed to make click on the button positive (ie just show clicked, rather than hide clicked)
		for(x in chart.data.datasets){
			var a=chart.getDatasetMeta(x);
			a.hidden=null;
		}
		if($(this).attr("id") === "filter_clear"){ chart.update(); return;}

		var n=parseInt($(this).val())-1;
		for(x in chart.data.datasets){
			if(n!=x){
				var a=chart.getDatasetMeta(x);
				a.hidden=null===a.hidden ?! chart.data.datasets[x].hidden : null;
			}

		}
		chart.update();
		return false;

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

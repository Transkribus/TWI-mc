$(document).ready(function()
{

    $("#institution-select").selectBoxIt({
          theme: "bootstrap",
          showEffect: "slideDown",
          autoWidth: true,      
     });
     
     
     var id = $("#institution-select option:first-child").val();
     change_inst_select(id);
     
     var owl = $("#blog_carousel").owlCarousel();
     owl.on('changed.owl.carousel', function(event) 
     {
                blog_detail(blog[event.item.index]);
    });
});



function blog_detail(id)
{
    $.post("get_blog", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
    
        var subtitle = (data[0].fields.subtitle != null && data[0].fields.subtitle.length == 0) ? "" : "<h5>" + data[0].fields.subtitle + "</h5><br/>"; 
        var str = "<h4>" + data[0].fields.title  + " (" + data[0].fields.changed + ")</h4>";
        str += subtitle;
        str += data[0].fields.content;
        $('#blog_detail').html(str);
    });
}



function change_inst_select(id)
{
    ins = inst[id]
    map.setCenter({lat:ins.lat, lng:ins.lng});
    map.setZoom(8);
    $("#inst_desc").html(ins.desc);
    
    //and also get the projects
    $.post("get_inst_projects", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        var str = "";
        if (data.length > 0)
        {
            str = "<h3>" + projects_str + "</h3>";
            for (var i = 0; i < data.length;i++)
            {
                str += "<h4>" + data[i].fields.title + "</h4>";
                str += data[i].fields.desc;
            }
            
        }
        $("#inst_projects").html(str);
    });  
}

function more_service(btn, id, show_str, hide_str)
{ 
    if ($("#services_more_" + id).html().trim().length == 0)
    {
        $("#" + btn).html(hide_str);
        $("#services_more_" + id).html(services[id]);
    } else
    {
         $("#" + btn).html(show_str);
        $("#services_more_" + id).html('');
    }
}

function more_documents(btn, id, show_str, hide_str)
{
    if ($("#documents_more_" + id).html().trim().length == 0)
    {
        $("#" + btn).html(hide_str);
        $("#documents_more_" + id).html(docs[id]);
    } else
    {
         $("#" + btn).html(show_str);
        $("#documents_more_" + id).html('');
    }
}

function select_act_blog(pos, blog_id)
{
    $("#blog_carousel").trigger("to.owl.carousel", [pos, 1, true]);
    blog_detail(blog_id);
}

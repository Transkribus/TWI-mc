$(document).ready(function()
{

    $("#institution-select").selectBoxIt({
          theme: "bootstrap",
          showEffect: "slideDown",
          autoWidth: true,      
     });
     
     
     var id = $("#institution-select option:first-child").val()
     change_inst_select(id);
});



function change_inst_select(id)
{
    ins = inst[id]
    map.setCenter({lat:ins.lat, lng:ins.lng});
    $("#inst_desc").html(ins.desc);
    
    //and also get the projects
    $.post("get_inst_projects", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        console.log(data);
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
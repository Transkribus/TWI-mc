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
    
}
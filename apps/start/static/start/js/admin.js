/* this holds all quill editors of the page */
var quills = [];

/* general toolbar options for the quill.js editor */
var toolbarOptions = [
  ['bold', 'italic', 'underline', 'strike', 'link'],        // toggled buttons
  ['blockquote', 'code-block'],
  ['video', 'formula', 'image'],
  [{ 'header': 1 }, { 'header': 2 }],               // custom button values
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  [{ 'script': 'sub'}, { 'script': 'super' }],      // superscript/subscript
  [{ 'indent': '-1'}, { 'indent': '+1' }],          // outdent/indent
  [{ 'direction': 'rtl' }],                         // text direction

  [{ 'size': ['small', false, 'large', 'huge'] }],  // custom dropdown
  [{ 'header': [1, 2, 3, 4, 5, 6, false] }],

  [{ 'color': [] }, { 'background': [] }],          // dropdown with defaults from theme
  [{ 'font': [] }],
  [{ 'align': [] }],

  ['clean']                                         // remove formatting button
];

 Dropzone.options.MyDropzone = 
            {
                dictDefaultMessage: "{% trans 'put_your_file_here' %}",
                init: function()
                {
                    /* Called once the file has been processed. It could have failed or succeded */
                    this.on("complete", function(file){
                        //var img = file.xhr.responseText;
                        //img = img.replace(/"/g,"");
                        //img_form = img_templ.replace(/@link/g, img);
                        //$("#img_container").append(img_form);
                        //id++;
                        
                        //hide the upload container, not needed anymore
                        //$("#MyDropzone").hide();
                        //$("#desc_1").hide();
                        
                        //show the new data entry fields
                        //$("#step_3").show();
                        //$("#desc_2").show();
                    });
                    
                    /* Called after the file is uploaded and sucessful */
                    this.on("sucess", function(file){
                      //  console.log(file);
                    });
                    
                    /* Called before the file is being sent */
                    this.on("sending", function(file){
                      //  console.log("sending");
                    });
                    
                    /* Called before the file is being sent */
                    this.on("addedfile", function(file){
                      //  console.log("addedfile");
                    });
                }
            };  
    

/* ------------------------------------ */
/* Common functions */
/* ------------------------------------ */    
function getBlogEntryByLang(arr, lang)
{
    for (var i = 1; i < arr.length;i++)
    {
        if (arr[i].fields.lang == lang)
        {
            return arr[i];
        }
    }
    return null;
}

function openTabs(lang,type, evt) 
{
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent-" + type);
    for (i = 0; i < tabcontent.length; i++) 
    {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks-" + type);
    for (i = 0; i < tablinks.length; i++) 
    {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(lang).style.display = "block";
    if (evt)
    {
        evt.currentTarget.className += " active";
    } else
    {
        tablinks[0].className += " active";
    }
}

/*  type (blog, inst,...) serves as a prefix for the key of the array which stores the quill objects 
    objects are generated for each language and type
*/
function generateQuillObjects(type)
{
    for (var i = 0; i < langs.length;i++)
    {
        var l = langs[i];
        quills[type + "-" + l] = new Quill('#editor-container-' + type + '-' + l, {
            modules: {
              toolbar: toolbarOptions,
            },
            placeholder: 'Compose an epic...',
            formula:true,
            theme: 'snow'  // or 'bubble'
            });  
    }
}

/* ------------------------------------ */
/* Blog functions */
/* ------------------------------------ */    

/* remove all entries from the blog editor section */
function clear_blog()
{
    $("#editor-container-blog-de").children().first().html(''); 
    $("#editor-container-blog-en").children().first().html('');
    $("#editor-title-blog-de").val(''); 
    $("#editor-title-blog-en").val(''); 
    $("#editor-subtitle-blog-de").val(''); 
    $("#editor-subtitle-blog-en").val('');  
}

function delete_blog()
{
    var id = $("#blog-options").val();
   
    $.post("delete_admin_blog", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#blog-options option[value='" + id + "']").remove();
    });
    clear_blog();
}

        
function store_blog()
{
    var html_de = $("#editor-container-blog-de").children().first().html(); 
    var html_en = $("#editor-container-blog-en").children().first().html();
    var title_de = $("#editor-title-blog-de").val(); 
    var title_en = $("#editor-title-blog-en").val(); 
    var subtitle_de = $("#editor-subtitle-blog-de").val(); 
    var subtitle_en = $("#editor-subtitle-blog-en").val();  

    $.post("store_admin_blog", 
        {id : 0, 
        title_de: title_de, 
        subtitle_de: subtitle_de,
        title_en: title_en, 
        subtitle_en: subtitle_en,
        content_de: html_de, 
        content_en: html_en,  
        'csrfmiddlewaretoken':  csrf_token }).done(function(data)
            {
                console.log(data);
                $("#blog-options").append('<option value="' + data.id +'" selected="selected">' + data.title + ' - ' + data.changed + '</option>');
            });
}    


function change_blog(v)
{
    if (v !== 0)
    {
        $.post("change_admin_blog", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
            var img = data[0].fields.image;
            
            $("#editor-blog-img").removeClass("invisible");
            $("#editor-blog-btn-delete").removeClass("invisible");
            $("#editor-blog-img").attr("src", "../static/start/img/upload/" + img ); //TODO: change path
            $("#editor-blog-img").attr("width","80px");
            var de = getBlogEntryByLang(data, "de");
            
            //$("#editor-container-blog-de").html(de.fields.content);
            quills['blog-de'].clipboard.dangerouslyPasteHTML(de.fields.content);
            $("#editor-title-blog-de").val(de.fields.title);
            $("#editor-subtitle-blog-de").val(de.fields.subtitle);
            
            var en = getBlogEntryByLang(data, "en");
            quills['blog-en'].clipboard.dangerouslyPasteHTML(en.fields.content);
            $("#editor-title-blog-en").val(en.fields.title);
            $("#editor-subtitle-blog-en").val(en.fields.subtitle);   
        });
    } else
    {
        $("#editor-blog-btn-delete").addClass("invisible");
        $("#editor-blog-img").addClass("invisible");
    }
}

/* ------------------------------------ */
/* Institution functions */
/* ------------------------------------ */    

function store_inst()
{
    var html_de = $("#editor-container-inst-de").children().first().html(); 
    var html_en = $("#editor-container-inst-en").children().first().html();
    var name = $("#inst-name").val();
    var loc_name = $("#loc-name").val();
    var lng = $("#loc-coord-long").val();
    var lat = $("#loc-coord-lat").val();
    var url = $("#inst-url").val();
    
    $.post("store_admin_inst",
        {id: 0,
        name: name,
        loc_name : loc_name,
        lng : lng,
        lat : lat,
        url : url,
        content_de: html_de, 
        content_en: html_en, 
        'csrfmiddlewaretoken':  csrf_token
        }).done(function(data)
            {
                $("#inst-options").append('<option value="' + data.id +'" selected="selected">' + data.name + '</option>');
    
            });
}

/* remove all entries from the inst editor section (also from inst-projects if linked) */
function clear_inst()
{
    $("#editor-container-inst-de").children().first().html(''); 
    $("#editor-container-inst-en").children().first().html('');
    $("#inst-name").val(''); 
    $("#loc-name").val(''); 
    $("#loc-coord-long").val(''); 
    $("#loc-coord-lat").val('');  
    //TODO: inst-projects
}

function delete_inst()
{
    var id = $("#inst-options").val();
    
    $.post("delete_admin_inst", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#inst-options option[value='" + id + "']").remove();
    });
    clear_inst();
}


function change_inst(v)
{
    if (v !== 0)
    {
        $.post("change_admin_inst", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
            var img = data[0].fields.image;
            
            $("#editor-blog-img").removeClass("invisible");
            $("#editor-blog-btn-delete").removeClass("invisible");
            $("#editor-blog-img").attr("src", "../static/start/img/upload/" + img ); //TODO: change path
            $("#editor-blog-img").attr("width","80px");
            var de = getBlogEntryByLang(data, "de");
            
            //$("#editor-container-blog-de").html(de.fields.content);
            quills['blog-de'].clipboard.dangerouslyPasteHTML(de.fields.content);
            $("#editor-title-blog-de").val(de.fields.title);
            $("#editor-subtitle-blog-de").val(de.fields.subtitle);
            
            var en = getBlogEntryByLang(data, "en");
            quills['blog-en'].clipboard.dangerouslyPasteHTML(en.fields.content);
            $("#editor-title-blog-en").val(en.fields.title);
            $("#editor-subtitle-blog-en").val(en.fields.subtitle);   
        });
    } else
    {
        $("#editor-blog-btn-delete").addClass("invisible");
        $("#editor-blog-img").addClass("invisible");
    }
}

function store_inst_proj()
{
    var html_de = $("#editor-container-inst-proj-de").children().first().html(); 
    var html_en = $("#editor-container-inst-proj-en").children().first().html();
    var title_de = $("#editor-title-inst-proj-de").val();
    var title_en = $("#editor-title-inst-proj-en").val();
    var inst_id = $("#inst-proj-options").val();
    
    console.log("inst_id" + inst_id);
    
    $.post("store_admin_proj",
        {id: 0,
        inst_id : inst_id,
        title_de: title_de,
        title_en: title_en,
        content_de: html_de, 
        content_en: html_en, 
        'csrfmiddlewaretoken':  csrf_token
        }).done(function(data)
            {
                $("#inst-proj-proj-options").append('<option value="' + data.id +'" selected="selected">' + data.title + '</option>');
            });
}


/* switch the selection of the actual institution: the listing of the actual projects are changed */
function change_inst_proj(v)
{
    $.post("change_admin_proj", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#inst-proj-proj-options").empty();
        for (var i = 0; i < data.length;i++)
        {
            $("#inst-proj-proj-options").append('<option value="' + data[i].fields.pk +'" selected="selected">' + data[i].fields.title + '</option>');            
        }
        if (data.length > 0)
        {
            change_inst_proj_proj(data[0].fields.project);
        }
    });
}


function getentrybylang(arr, lang)
{
    for (var i = 0; i < arr.length;i++)
    {
        if (arr[i].fields.lang == lang)
        {
            return arr[i];
        }
    }
    return null;
}

function change_inst_proj_proj(v)
{
    $.post("change_admin_pr_inst_selection", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        var en = getentrybylang(data,"en");
        quills['inst-proj-en'].clipboard.dangerouslyPasteHTML(en.fields.desc);
        $("#editor-title-inst-proj-en").val(en.fields.title);
        var de = getentrybylang(data,"de");
        quills['inst-proj-de'].clipboard.dangerouslyPasteHTML(de.fields.desc);
        $("#editor-title-inst-proj-de").val(de.fields.title);
    });
}

/* ------------------------------------ */
/* Main entry Point                     */
/* ------------------------------------ */    

$(document).ready(function()
    {
        openTabs('editor-blog-tab-de','blog');
        openTabs('editor-inst-tab-de','inst');
        openTabs('editor-inst-proj-tab-de','inst-proj');
        
        generateQuillObjects('blog');
        generateQuillObjects('inst');
        generateQuillObjects('inst-proj');
            
    });        
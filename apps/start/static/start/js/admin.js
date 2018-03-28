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
            console.log(data);
            $("#inst-options").append('<option value="' + data.id +'" selected="selected">' + data.name + '</option>');

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
            
        $( "#blog-options" ).change(function() {
            if ($(this).val() !== 0)
            {
                $.post("change_admin_blog", {'id': $(this).val(), 'csrfmiddlewaretoken': csrf_token }).done( function(data)
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
        });
    });        
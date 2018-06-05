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

/* get the array item which contains a field with a certain lang */ 
function getEntryByLang(arr, lang)
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
            placeholder: quills_placeholder,
            formula:true,
            theme: 'snow'  // or 'bubble'
            });  
    }
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


/*
set the image img for the image with id 
*/
function setImg(id, img)
{
    console.log("IMG:" + img)
    if (img && img != "")
    {
        console.log($(id))
        $(id).removeClass("invisible");
        $(id).attr("src", "../static/start/img/upload/" + img ); //TODO: change path
        $(id).attr("width","80px");
    }
}

/* by default, select the first option*/
function selectOption(id, opt_id = 0)
{
    console.log(id);
    $(id).removeAttr("selected");
    $(id + "option[value='" + opt_id + "']").attr("selected", "selected");
}

/* removes the image from the dropzone with id */
function clearDropzone(id)
{
    console.log($(id + " .dz-image").html())
    $(id + " .dz-image").remove();
    $(id + " .dz-default dz-message").html(quills_placeholder);
}

/* ------------------------------------ */
/* Home Article functions */
/* ------------------------------------ */   

function store_article()
{
    var html_de = $("#editor-container-article-de").children().first().html(); 
    var html_en = $("#editor-container-article-en").children().first().html();
    var html_de_short = $("#editor-container-article-short-de").children().first().html(); 
    var html_en_short = $("#editor-container-article-short-en").children().first().html();
    var title_de = $("#editor-title-article-de").val(); 
    var title_en = $("#editor-title-article-en").val();   
    var id = $("#article-options").val();
    
    $.post("store_admin_article", 
        {id : id, 
        title_de: title_de, 
        subtitle_de: html_de_short,
        title_en: title_en, 
        subtitle_en: html_en_short,
        content_de: html_de, 
        content_en: html_en,  
        'csrfmiddlewaretoken':  csrf_token }).done(function(data)
            {
                var val = data.title + ' ' + data.changed;
                if (id == 0)
                {
                    $("#article-options").append('<option value="' + data.id +'" selected="selected">' + val + '</option>');
                } else
                {
                    $("#article-options option[value='" + id + "']").text(val);  
                    setImg("#editor-article-img", data.image);  
                }
                setImg("#editor-article-img", data.image);  
            });
            
    clearDropzone("#article_dropzone");
    $("#editor-article-btn-delete").removeClass("invisible");
}

/* clear all entries from the home article section  */
function clear_article()
{
    $("#editor-container-article-de").children().first().html(''); 
    $("#editor-container-article-en").children().first().html(''); 
    $("#editor-container-article-short-de").children().first().html(''); 
    $("#editor-container-article-short-en").children().first().html(''); 
    $("#editor-title-article-de").val('');
    $("#editor-title-article-en").val('');
    $("#editor-article-img").attr("src", "");
    $("#editor-article-img").addClass("invisible");
    $("#editor-article-btn-delete").addClass("invisible");
}

function change_article(v)
{
    if (v === '0')
    {
        clear_article();
        $("#editor-article-img").addClass("invisible");
        $("#editor-article-btn-delete").addClass("invisible");
    } else
    {
        $.post("change_admin_article", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
            $("#editor-article-btn-delete").removeClass("invisible");
            setImg("#editor-article-img", data[0].fields.image);
            
            var de = getEntryByLang(data, "de");
            quills['article-de'].clipboard.dangerouslyPasteHTML(de.fields.content);
            $("#editor-title-article-de").val(de.fields.title);
            quills['article-short-de'].clipboard.dangerouslyPasteHTML(de.fields.shortdesc);
            
            var en = getEntryByLang(data, "en");            
            quills['article-en'].clipboard.dangerouslyPasteHTML(en.fields.content);
            $("#editor-title-article-en").val(en.fields.title);
            quills['article-short-en'].clipboard.dangerouslyPasteHTML(en.fields.shortdesc);
        });
    }

}

function delete_article()
{
    var id = $("#article-options").val();
    $.post("delete_admin_article", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#article-options option[value='" + id + "']").remove();
    });
    clear_article();
}

/* ------------------------------------ */
/* Service functions */
/* ------------------------------------ */   

function store_service()
{
    var html_de = $("#editor-container-service-de").children().first().html(); 
    var html_en = $("#editor-container-service-en").children().first().html();
    var html_de_short = $("#editor-container-service-short-de").children().first().html(); 
    var html_en_short = $("#editor-container-service-short-en").children().first().html();
    var title_de = $("#editor-title-service-de").val(); 
    var title_en = $("#editor-title-service-en").val();   
    var id = $("#service-options").val();
    var icon = $("#editor-icon-service").val();
 
    $.post("store_admin_service", 
        {id : id, 
        title_de: title_de, 
        subtitle_de: html_de_short,
        title_en: title_en, 
        subtitle_en: html_en_short,
        content_de: html_de, 
        content_en: html_en,  
        icon : icon,
      'csrfmiddlewaretoken':  csrf_token }).done(function(data)
        {
            var val = data.title + ' ' + data.changed;
            if (id == 0)
            {
                console.log(val);
                $("#service-options").append('<option value="' + data.id +'" selected="selected">' + val + '</option>');
            } else
            {
                $("#service-options option[value='" + id + "']").text(val);  
            }
        });
    $("#editor-service-btn-delete").removeClass("invisible");
}


function change_service(v)
{
    if (v !== '0')
    {
         $.post("change_admin_service_selection", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
            $("#editor-icon-service").data("selectBox-selectBoxIt").selectOption(data[0].fields.image_css);
            var en = getentrybylang(data,"en");
            quills['service-short-en'].clipboard.dangerouslyPasteHTML(en.fields.subtitle);
            quills['service-en'].clipboard.dangerouslyPasteHTML(en.fields.content);
            $("#editor-title-service-en").val(en.fields.title);
            
            var de = getentrybylang(data,"de");
            quills['service-short-de'].clipboard.dangerouslyPasteHTML(de.fields.subtitle);
            quills['service-de'].clipboard.dangerouslyPasteHTML(de.fields.content);
            $("#editor-title-service-de").val(de.fields.title);
            
            $("#editor-service-btn-delete").removeClass("invisible");
            
        });
    } else
    {
        $("#editor-service-btn-delete").addClass("invisible");
        clear_service();

    }
}

function delete_service()
{
    var id = $("#service-options").val();
   
    $.post("delete_admin_service", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#service-options option[value='" + id + "']").remove();
    });
    clear_service();
}

function clear_service()
{
    $("#editor-container-service-de").children().first().html(''); 
    $("#editor-container-service-en").children().first().html('');
    $("#editor-container-service-short-de").children().first().html(''); 
    $("#editor-container-service-short-en").children().first().html('');
    $("#editor-title-service-de").val(''); 
    $("#editor-title-service-en").val('');   
    $("#editor-service-btn-delete").addClass("invisible");
    $("#editor-icon-service").data("selectBox-selectBoxIt").selectOption("no_icon");
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
    $("#editor-blog-img").addClass("invisible");
    $("#editor-blog-btn-delete").addClass("invisible");
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
    var id =  $("#blog-options").val();
    var html_de = $("#editor-container-blog-de").children().first().html(); 
    var html_en = $("#editor-container-blog-en").children().first().html();
    var title_de = $("#editor-title-blog-de").val(); 
    var title_en = $("#editor-title-blog-en").val(); 
    var subtitle_de = $("#editor-subtitle-blog-de").val(); 
    var subtitle_en = $("#editor-subtitle-blog-en").val();  

    $.post("store_admin_blog", 
        {id : id, 
        title_de: title_de, 
        subtitle_de: subtitle_de,
        title_en: title_en, 
        subtitle_en: subtitle_en,
        content_de: html_de, 
        content_en: html_en,  
        'csrfmiddlewaretoken':  csrf_token }).done(function(data)
            {
                var val = data.title + ' ' + data.changed;
                if (id == 0)
                {
                    $("#blog-options").append('<option value="' + data.id +'" selected="selected">' + val + '</option>');
                } else
                {
                    $("#blog-options option[value='" + id + "']").text(val);     
                }
                setImg("#editor-blog-img", data.image);  
            });
    clearDropzone("#blog_dropzone");
    $("#editor-blog-btn-delete").removeClass("invisible");
}    

function change_blog(v)
{
    if (v !== '0')
    {
        $.post("change_admin_blog", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
            $("#editor-blog-btn-delete").removeClass("invisible");
            
            setImg("#editor-blog-img", data[0].fields.image);
                        
            var de = getEntryByLang(data, "de");
            
            //$("#editor-container-blog-de").html(de.fields.content);
            quills['blog-de'].clipboard.dangerouslyPasteHTML(de.fields.content);
            $("#editor-title-blog-de").val(de.fields.title);
            $("#editor-subtitle-blog-de").val(de.fields.subtitle);
            
            var en = getEntryByLang(data, "en");
            quills['blog-en'].clipboard.dangerouslyPasteHTML(en.fields.content);
            $("#editor-title-blog-en").val(en.fields.title);
            $("#editor-subtitle-blog-en").val(en.fields.subtitle);   
        });
    } else
    {
        $("#editor-blog-btn-delete").addClass("invisible");
        $("#editor-blog-img").addClass("invisible");
        clear_blog();
    }
}

/* ------------------------------------ */
/* Institution functions */
/* ------------------------------------ */    

function store_inst()
{
    var id =  $("#inst-options").val();
    var html_de = $("#editor-container-inst-de").children().first().html(); 
    var html_en = $("#editor-container-inst-en").children().first().html();
    var name_de = $("#inst-name-de").val();
    var loc_name_de = $("#loc-name-de").val();
    var name_en = $("#inst-name-en").val();
    var loc_name_en = $("#loc-name-en").val();

    var lng = $("#loc-coord-long").val();
    var lat = $("#loc-coord-lat").val();
    var url = $("#inst-url").val();
    
    $.post("store_admin_inst",
        {id: id,
        name_de: name_de,
        loc_name_de : loc_name_de,
        name_en: name_en,
        loc_name_en : loc_name_en,
        lng : lng,
        lat : lat,
        url : url,
        content_de: html_de, 
        content_en: html_en, 
        'csrfmiddlewaretoken':  csrf_token
        }).done(function(data)
            {
                var val = data.name + " - " + data.changed;
                if (id == 0)
                {
                    var newOpt = '<option value="' + data.id +'" selected="selected">' + val + '</option>';
                    $("#inst-options").append(newOpt);
                    $("#inst-proj-options").append(newOpt);
                } else
                {
                    $("#inst-options option[value='" + id + "']").text(val);
                    $("#inst-proj-options option[value='" + id + "']").text(val);    
                }
                setImg("#editor-inst-img", data.image);  
            });
            
    clearDropzone("#inst_dropzone");
    $("#editor-inst-btn-delete").removeClass("invisible");
}

/* remove all entries from the inst editor section (also from inst-projects if linked) */
function clear_inst()
{
    $("#editor-container-inst-de").children().first().html(''); 
    $("#editor-container-inst-en").children().first().html('');
    $("#inst-name-de").val(''); 
    $("#inst-name-en").val(''); 
    $("#inst-url").val(''); 
    $("#loc-name-de").val(''); 
    $("#loc-name-en").val(''); 
    $("#loc-coord-long").val(''); 
    $("#loc-coord-lat").val('');  
    $("#editor-inst-img").addClass("invisible");
    $("#editor-inst-btn-delete").addClass("invisible");
}

function delete_inst()
{
    var id = $("#inst-options").val();
    
    $.post("delete_admin_inst", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#inst-options option[value='" + id + "']").remove();
    });
    clear_inst(id);
    var x= $("#inst-proj-options option[value='" + id + "']").remove();
    if(x.length > 0) //also remove the projects
    {
        $("#inst-proj-proj-options[value='0']").attr("selected", true);
    }
}


function change_inst(v)
{
    if (v !== '0')
    {
        $.post("change_admin_inst", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
            $("#editor-inst-btn-delete").removeClass("invisible");
            
            setImg("#editor-inst-img", data[0].fields.image);
            
            var de = getEntryByLang(data, "de");
            quills['inst-de'].clipboard.dangerouslyPasteHTML(de.fields.desc);   
            $("#inst-name-de").val(de.fields.name);
            $("#loc-name-de").val(de.fields.loclabel);  
                     
            var en = getEntryByLang(data, "en");
            quills['inst-en'].clipboard.dangerouslyPasteHTML(en.fields.desc);
            $("#inst-name-en").val(en.fields.name);
            $("#loc-name-en").val(en.fields.loclabel);
            
            $("#loc-coord-long").val(data[0].fields.lng);
            $("#loc-coord-lat").val(data[0].fields.lat);
            $("#inst-url").val(data[0].fields.link);
        });
    } else
    {
        $("#editor-inst-btn-delete").addClass("invisible");
        $("#editor-inst-img").addClass("invisible");
        clear_inst();
    }
}

/* -----------------------------------------
project for institutions functions
--------------------------------------------*/
function store_inst_proj()
{
    var id = $("#inst-proj-proj-options").val();
    var html_de = $("#editor-container-inst-proj-de").children().first().html(); 
    var html_en = $("#editor-container-inst-proj-en").children().first().html();
    var title_de = $("#editor-title-inst-proj-de").val();
    var title_en = $("#editor-title-inst-proj-en").val();
    var inst_id = $("#inst-proj-options").val();
    console.log("ID::" + id);
    $.post("store_admin_proj",
        {id: id,
        inst_id : inst_id,
        title_de: title_de,
        title_en: title_en,
        content_de: html_de, 
        content_en: html_en, 
        'csrfmiddlewaretoken':  csrf_token
        }).done(function(data)
            {
                var val = data.title + " " + data.changed;
                if (id == 0)
                {
                    $("#inst-proj-proj-options").append('<option value="' + data.id +'" selected="selected">' + val + '</option>');
                } else
                {
                    $("#inst-proj-proj-options option[value='" + id + "']").text(val); 
                }
            });
}


/* switch the selection of the actual institution: the listing of the actual projects are changed */
function change_inst_proj(v)
{
    $.post("change_admin_proj", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#inst-proj-proj-options option[value!='0']").remove();
        for (var i = 0; i < data.length;i++)
        {
            $("#inst-proj-proj-options").append('<option value="' + data[i].pk +'" selected="selected">' + data[i].fields.title + '</option>');            
        }
        if (data.length > 0)
        {
            change_inst_proj_proj(data[0].fields.project);
        } else
        {
            clear_inst_proj();
        }
    });
}



function clear_inst_proj()
{
    quills['inst-proj-en'].clipboard.dangerouslyPasteHTML('');
    $("#editor-title-inst-proj-en").val('');
    quills['inst-proj-de'].clipboard.dangerouslyPasteHTML('');
    $("#editor-title-inst-proj-de").val('');
    $("#editor-inst-proj-btn-delete").addClass("invisible");
    
}

function change_inst_proj_proj(v)
{
    if (v !== '0')
    {
        $.post("change_admin_pr_inst_selection", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
            var en = getentrybylang(data,"en");
            quills['inst-proj-en'].clipboard.dangerouslyPasteHTML(en.fields.desc);
            $("#editor-title-inst-proj-en").val(en.fields.title);
            
            var de = getentrybylang(data,"de");
            quills['inst-proj-de'].clipboard.dangerouslyPasteHTML(de.fields.desc);
            $("#editor-title-inst-proj-de").val(de.fields.title);
            $("#editor-inst-proj-btn-delete").removeClass("invisible");
        });
    } else
    {
        $("#editor-inst-proj-btn-delete").addClass("invisible");
        clear_inst_proj();
    }
}

function delete_inst_proj()
{

    var id = $("#inst-proj-proj-options").val();
    
    $.post("delete_admin_projinst", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#inst-proj-proj-options option[value='" + id + "']").remove();
    });
    clear_inst_proj();

}

/* ------------------------------------ */
/* Quote - Functions                    */
/* ------------------------------------ */    

function clear_quote()
{
    $("#editor-name-quote").val('');
    quills['quote-en'].clipboard.dangerouslyPasteHTML('');
    $("#editor-role-quote-en").val('');
    quills['quote-de'].clipboard.dangerouslyPasteHTML('');
    $("#editor-role-quote-de").val('');
    $("#editor-quote-img").attr("src", "");
    $("#editor-quote-img").addClass("invisible");
}

function change_quote(v)
{
    if (v !== '0')
    {
        $.post("change_admin_quote_selection", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
            setImg("#editor-quote-img", data[0].fields.image);
               
            $("#editor-name-quote").val(data[0].fields.name);
            var en = getentrybylang(data,"en");
            quills['quote-en'].clipboard.dangerouslyPasteHTML(en.fields.content);
            $("#editor-role-quote-en").val(en.fields.role);
            var de = getentrybylang(data,"de");
            quills['quote-de'].clipboard.dangerouslyPasteHTML(de.fields.content);
            $("#editor-role-quote-de").val(de.fields.role);
            $("#editor-quote-btn-delete").removeClass("invisible");
        });
    } else
    {
        $("#editor-quote-btn-delete").addClass("invisible");
        clear_quote();
    }
}

function store_quote()
{
    var html_de = $("#editor-container-quote-de").children().first().html(); 
    var html_en = $("#editor-container-quote-en").children().first().html();
    var role_de = $("#editor-role-quote-de").val();
    var role_en = $("#editor-role-quote-en").val();
    var id = $("#quote-options").val();
    var name = $("#editor-name-quote").val();
    
    $.post("store_admin_quote",
        {id: id,
        role_de: role_de,
        role_en: role_en,
        content_de: html_de, 
        content_en: html_en, 
        name : name,
        'csrfmiddlewaretoken':  csrf_token
        }).done(function(data)
            {
                var val = data.name + " " + data.changed;
                if (id == 0)
                {
                    $("#quote-options").append('<option value="' + data.id +'" selected="selected">' + val + '</option>');
                } else
                {
                    $("#quote-options  option[value='" + id + "']").text(val); 
                }
                setImg("#editor-quote-img", data.image);  
            });
    
    clearDropzone("#quote_dropzone");
    $("#editor-quote-btn-delete").removeClass("invisible");
}

function delete_quote()
{

    var id = $("#quote-options").val();
    
    $.post("delete_admin_quote", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#quote-options option[value='" + id + "']").remove();
    });
    clear_quote();
}


/* ------------------------------------ */
/* Documents                            */
/* ------------------------------------ */    

function clear_doc()
{
    quills['doc-desc-en'].clipboard.dangerouslyPasteHTML('');
    quills['doc-content-en'].clipboard.dangerouslyPasteHTML('');
    $("#editor-title-doc-en").val('');
    
    quills['doc-desc-de'].clipboard.dangerouslyPasteHTML('');
    quills['doc-content-de'].clipboard.dangerouslyPasteHTML('');
    $("#editor-title-doc-de").val('');   
    //$("#editor-icon-doc").val(''); 
    
    $("#editor-icon-doc").data("selectBox-selectBoxIt").selectOption("no_icon");
}

function change_doc(v)
{
    if (v !== '0')
    {
         $.post("change_admin_doc_selection", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
            $("#editor-icon-doc").data("selectBox-selectBoxIt").selectOption(data[0].fields.icon);
            var en = getentrybylang(data,"en");
            quills['doc-desc-en'].clipboard.dangerouslyPasteHTML(en.fields.desc);
            quills['doc-content-en'].clipboard.dangerouslyPasteHTML(en.fields.content);
            $("#editor-title-doc-en").val(en.fields.title);
            
            var de = getentrybylang(data,"de");
            quills['doc-desc-de'].clipboard.dangerouslyPasteHTML(de.fields.desc);
            quills['doc-content-de'].clipboard.dangerouslyPasteHTML(de.fields.content);
            $("#editor-title-doc-de").val(de.fields.title);
            
            $("#editor-doc-btn-delete").removeClass("invisible");
            
        });
    } else
    {
        $("#editor-doc-btn-delete").addClass("invisible");
        clear_doc();

    }
}

function store_doc()
{
    var id = $("#doc-options").val();
    var title_de = $("#editor-title-doc-de").val();
    var title_en = $("#editor-title-doc-en").val();
    var html_desc_en = $("#editor-container-doc-desc-en").children().first().html();
    var html_desc_de = $("#editor-container-doc-desc-de").children().first().html(); 
    var html_content_en = $("#editor-container-doc-content-en").children().first().html();
    var html_content_de = $("#editor-container-doc-content-de").children().first().html();
    
    var icon = $("#editor-icon-doc").val();
    
    $.post("store_admin_doc",
    {id: id,
    title_de: title_de,
    title_en: title_en,
    content_de: html_content_de, 
    content_en: html_content_en, 
    desc_de: html_desc_de, 
    desc_en: html_desc_en,
    icon : icon,
    'csrfmiddlewaretoken':  csrf_token
    }).done(function(data)
        {
            var val = data.title + ' ' + data.changed;
            if (id == 0)
            {
                $("#doc-options").append('<option value="' + data.id +'" selected="selected">' + val + '</option>');
            } else
            {
                $("#doc-options option[value='" + id + "']").text(val);   
            }
        });
    
}

function delete_doc()
{
    var id = $("#doc-options").val();
    
    $.post("delete_admin_doc", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#doc-options option[value='" + id + "']").remove();
    });
    clear_doc();
}

/* ------------------------------------ */
/* Videos                               */
/* ------------------------------------ */    
function clear_video()
{
    $("#editor-id-video").val();
    
    quills['video-de'].clipboard.dangerouslyPasteHTML('');
    $("#editor-title-video-de").val('');
    
    quills['video-en'].clipboard.dangerouslyPasteHTML('');    
    $("#editor-title-video-en").val('');
    
    $("#editor-id-video").val('');
}

function change_video(v)
{
     if (v !== '0')
    {
         $.post("change_admin_video_selection", {'id': v, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
        {
                    
            $("#editor-id-video").val(data[0].fields.vid);
        
            var de = getentrybylang(data,"de");
            quills['video-de'].clipboard.dangerouslyPasteHTML(de.fields.desc);
            $("#editor-title-video-de").val(de.fields.title);
            
            var en = getentrybylang(data,"en");        
            quills['video-en'].clipboard.dangerouslyPasteHTML(en.fields.desc);    
            $("#editor-title-video-en").val(en.fields.title);
            
            $("#editor-video-btn-delete").removeClass("invisible");
        });
    } else
    {
        $("#editor-video-btn-delete").addClass("invisible");
        clear_video();
    }
}

function store_video()
{
    var html_de = $("#editor-container-video-de").children().first().html(); 
    var html_en = $("#editor-container-video-en").children().first().html();
    var title_de = $("#editor-title-video-de").val();
    var title_en = $("#editor-title-video-en").val();
    var vid = $("#editor-id-video").val();
    var id = $("#video-options").val();
    console.log(id);
    $.post("store_admin_video",
        {id: id,
        vid : vid,
        title_de: title_de,
        title_en: title_en,
        content_de: html_de, 
        content_en: html_en, 
        'csrfmiddlewaretoken':  csrf_token
        }).done(function(data)
            {
                var val = data.title + ' ' + data.changed;
                if (id == 0)
                {
                    $("#video-options").append('<option value="' + data.id +'" selected="selected">' + data.title + '</option>');
                } else
                {
                    $("#video-options option[value='" + id + "']").text(val); 
                }
            });
}

function delete_video()
{
    var id = $("#video-options").val();
    $.post("delete_admin_video", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#video-options option[value='" + id + "']").remove();
    });
    clear_video(); 
}

/* ------------------------------------ */
/* Main entry Point                     */
/* ------------------------------------ */    

$(document).ready(function()
{
    openTabs('editor-blog-tab-de','blog');
    openTabs('editor-inst-tab-de','inst');
    openTabs('editor-inst-proj-tab-de','inst-proj');
    openTabs('editor-article-tab-de','article');
    openTabs('editor-quote-tab-de','quote');
    openTabs('editor-video-tab-de','video');
    openTabs('editor-doc-tab-de','doc');
    openTabs('editor-service-tab-de','service');
    
    generateQuillObjects('blog');
    generateQuillObjects('inst');
    generateQuillObjects('inst-proj');
    generateQuillObjects('article');
    generateQuillObjects('article-short');
    generateQuillObjects('quote');        
    generateQuillObjects('video');            
    generateQuillObjects('doc-desc');  
    generateQuillObjects('doc-content'); 
    generateQuillObjects('service');
    generateQuillObjects('service-short');     
    
     $("#editor-icon-doc").selectBoxIt({
          theme: "jqueryui",
          showEffect: "slideDown",
          autoWidth: true 
     });
     
     
     $("#editor-icon-service").selectBoxIt({
          theme: "jqueryui",
          showEffect: "slideDown",
          autoWidth: true 
     });
     //$("select").selectBoxIt();
});        
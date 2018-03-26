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

function editorBlogDelete()
{
    var id = $("#blog_options").val();
   
    
    $.post("delete_admin_blog", {'id': id, 'csrfmiddlewaretoken': csrf_token }).done( function(data)
    {
        $("#blog_options option[value='" + id + "']").remove();
    });
}

 function openBlog(lang, evt) 
        {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) 
            {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
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
        
        function store_blog()
        {
            var html_de = document.getElementById("editor-container-blog-de").firstChild.innerHTML; /* TODO replace with JQuery */
            var html_en = document.getElementById("editor-container-blog-en").firstChild.innerHTML; /* TODO replace with JQuery */
            var title_de = document.getElementById("editor-title-blog-de").value;  /* TODO replace with JQuery */
            var title_en = document.getElementById("editor-title-blog-en").value;  /* TODO replace with JQuery */
            var subtitle_de = document.getElementById("editor-subtitle-blog-de").value;  /* TODO replace with JQuery */
            var subtitle_en = document.getElementById("editor-subtitle-blog-en").value;  /* TODO replace with JQuery */
            //var id =  document.getElementById("editor-id-blog")
            // console.log(html);
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
                    });
        }    
$(document).ready(function()
    {
        openBlog('editor-blog-tab-de');
        
        $( "#blog_options" ).change(function() {
            if ($(this).val() !== 0)
            {
                $.post("change_admin_blog", {'id': $(this).val(), 'csrfmiddlewaretoken': csrf_token }).done( function(data)
                {
                    var img = data[0].fields.image;
                    
                    $("#editor-blog-img").removeClass("invisible");
                    $("#editor-blog-btn-delete").removeClass("invisible");
                    $("#editor-blog-img").attr("src", "../static/start/img/upload/" + img );
                    $("#editor-blog-img").attr("width","80px");
                    var de = getBlogEntryByLang(data, "de");
                    
                    //$("#editor-container-blog-de").html(de.fields.content);
                    quills['de'].clipboard.dangerouslyPasteHTML(de.fields.content);
                    $("#editor-title-blog-de").val(de.fields.title);
                    $("#editor-subtitle-blog-de").val(de.fields.subtitle);
                    
                    var en = getBlogEntryByLang(data, "en");
                    quills['en'].clipboard.dangerouslyPasteHTML(en.fields.content);
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
// shamelessly copied from https://css-tricks.com/snippets/javascript/get-url-variables/ (presumed to be in the public domain)
// URLSearchParams would be the ideal solution but isn't supported by Internet Explorer
function getQueryVariable(variable) {
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
       }
       return(false);
}
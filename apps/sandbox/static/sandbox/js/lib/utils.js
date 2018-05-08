/* FIXTHIS: quite a lot of repetition in getXXX and postXXX methods, however avoid premature refactoring */
/* FIXTHIS: use addEventListener(...) in all functions rather than onload = ...*/

function getXML (url) {

  return new Promise(function (resolve, reject) {

    var xhr = new XMLHttpRequest();

    xhr.open('GET', url);

    xhr.responseType = 'document';

    if (typeof xhr.overrideMimeType === 'function')
      xhr.overrideMimeType('text/xml');

    xhr.addEventListener('load', function () {
      if (xhr.responseXML === null)
        reject(new Error("Failed to parse response (probably)"));
      else
        resolve(xhr.responseXML);
    });

    xhr.addEventListener('error', reject);

    xhr.send();
  });

}

function postXML (url, xml) {

  console.assert(typeof url === 'string');
  console.assert(xml instanceof Document);

  return new Promise(function (resolve, reject) {

    var xhr = new XMLHttpRequest();

    xhr.open('POST', url);

    xhr.withCredentials = true;
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('Content-Type', 'text/xml');

    /* NOTE: for some reason this results in response being undefined */
    // xhr.responseType = 'json';

    xhr.addEventListener('load', function (evt) {
      if (xhr.status !== 200)
	reject(new Error(xhr.status));
      else {
	try {
	  if (xhr.responseText !== '')
            resolve.call(this, JSON.parse(xhr.responseText));
	  else
	    resolve.call(this, xhr.responseText);
        }
	catch (error) {
	  /* FIXTHIS: make distinction between HTTP and parsing errors */
	  console.error(error);
	  reject(error);
	}
      }
    });

    xhr.addEventListener('error', reject);

    xhr.send(xml);

  });

}


function getJSON (url) {

  var xhr = new XMLHttpRequest();

  xhr.open('GET', url, true);

  xhr.withCredentials = true;
  xhr.setRequestHeader('Accept', 'application/json');
  // NOTE: trp server CORS does not allow this field
  // xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

  return new Promise(function (resolve, reject) {

    xhr.onload = function (evt) {
      if (xhr.status !== 200)
        reject.call(this, new Error(xhr.status));
      else {
	if (xhr.responseText !== '')
          resolve.call(this, JSON.parse(xhr.responseText));
	else
	  resolve.call(this, xhr.responseText);
      }
    };
    xhr.onerror = reject;

    xhr.send();

  });
}

function postJSON (url, data) {

  /* FIXTHIS: check if session id cookie needs to be set ... */

  data = data || {};

  // var formData = new FormData();
  
  var formData = '';
  var paramList = [];

  for (var key in data) {
    if (!(data[key] instanceof Array))
        paramList.push(encodeURIComponent(key) + '=' + encodeURIComponent(data[key]));
    else {
      var values = data[key];
      for (var index = 0; index < values.length; index++) {
        paramList.push(encodeURIComponent(key) + '=' + encodeURIComponent(data[key]));
        // formData.append(key, values[index]);
      }
    }
  }

  formData = paramList.join('&').replace(/%20/g, '+');

  var req = new XMLHttpRequest();

  req.open('POST', url, true);

  req.withCredentials = true;

  if (formData.length > 0)
    req.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

  req.setRequestHeader('Accept', 'application/json');
  // req.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

  return new Promise(function (resolve, reject) {

    /* FIXTHIS: DRY, see loadJSON */
    req.onload = function (evt) {
      if (req.status !== 200)
        reject.call(this, new Error(req.status + ' ' + req.responseText));
      else {
	if (req.responseText !== '')
          resolve.call(this, JSON.parse(req.responseText));
	else
	  resolve.call(this, req.responseText);
      }
    };
    req.onerror = reject;

    if (formData.length > 0)
      req.send(formData);
    else
      req.send();

  });
}

function getIMG (url) {

  return new Promise(function (resolve, reject) {

    var image = new Image();

    image.addEventListener('load', function (evt) {
      resolve(image);
    });

    image.addEventListener('error', resolve);

    image.src = url;

  });

}

function loadIMG (imageUrl, imageNode) {
  return new Promise(function (resolve, reject) {
    imageNode.addEventListener('load', function (evt) {
      resolve(imageNode);
    });

    imageNode.addEventListener('error', reject);

    imageNode.setAttribute('xlink:href', imageUrl);

  });
}

function loadJS (url) {
  return new Promise(function (resolve, reject) {

    var script = document.createElement('script');

    script.addEventListener('load', resolve.bind(null));
    script.addEventListener('error', reject.bind(null));

    // NOTE: must insert into DOM first to work
    document.head.appendChild(script);

    script.type = 'text/javascript';
    script.src = url;

  });
}

function loadCSS (url) {
  return new Promise(function (resolve, reject) {

    var css = document.createElement('link');

    css.addEventListener('load', function () {
      resolve(css);
    });

    css.addEventListener('error', reject.bind(css));

    document.head.appendChild(css);

    css.rel = 'stylesheet';
    css.type = 'text/css';
    css.href = url;

  });
}

function loadHTML (url) {
  throw new Error("NotImplemented");
}


function getQueryParam (name, parse) {
  var value = new URL(document.location.href).searchParams.get(name);
  if (value === null)
    return null;
  if (typeof parse !== 'function')
    return value;
  return parse(value);
}

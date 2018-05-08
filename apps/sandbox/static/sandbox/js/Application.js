function parsePath (string, pattern, nameList, parsing) {

  console.assert(pattern === undefined);
  console.assert(nameList === undefined);
  console.assert(parsing === undefined);

  nameList = nameList || ['viewer', 'colId', 'docId', 'pageNr'];
  pattern = pattern || '^\\/([a-z]+)\\/(\\d+)\\/(\\d+)\\/(\\d+)\\/?$';
  parsing = parsing || {
    viewer: function (s) { return s; },
    colId: parseInt,
    docId: parseInt,
    pageNr: parseInt
  };

  var r = {};

  var re = new RegExp(pattern, 'i');

  var matchList = re.exec(string);

  if (matchList === null)
    return null;

  for (var index = 0; index < nameList.length; index++)
    r[nameList[index]] = parsing[nameList[index]](matchList[index + 1]);

  return r;
}

function Application () {

  initialize();

  function initialize () {
    checkLogin().catch(waitForLogin).then(checkData).catch(handleError);
  }

  function checkLogin () {

    /* FIXTHIS: avoid having to load api.js by using simple helper for this */
    return API.getInstance().then(function (api) {
      return api.checkSession();
    });
  }

  /* FIXTHIS: move this inside login??, e.g. Application needs to do loginDialog.login() only */
  function waitForLogin (error) {

    /* no session cookie / invalid sessoin: show login  */

    return LoginDialog.getInstance().then(function (loginDialog) {

      var loginPromise = loginDialog.login();

      loginPromise.catch(function (error) {
        console.warn("Login failed!");
      });

      loginPromise.then(function (userData) {
        console.debug(userData)
      })// .then(renderViewer);

      return loginPromise;

    });

  }

  function checkData () {

    var url = new URL(document.location.href);
    var params = parsePath(url.pathname.replace('/sandbox', ''));

    /* FIXTHIS: handle error, e.g. user has no access to document */
    var t = CurrentTranscript(params.colId, params.docId, params.pageNr);

    t.load().catch(handleError).then(renderViewer);

    // t.acquireLock().catch(handleError);

  }

  function renderViewer (transcript) {
    /* FIXTHIS: hide viewer at first, show when ready */

    var url = new URL(document.location.href);
    var params = parsePath(url.pathname.replace('/sandbox', ''));

    var viewerClass = null;
    var viewer;

    var menuClass = null;
    var menu;

    if (params.viewer === 'l') {
      viewerClass = LayoutViewer;
      menuClass = Menu
      /* TODO: find better way of doing the init */
      try {
        viewer = new viewerClass(transcript.getImageUrl(), transcript.getPageXml());
        menu = new menuClass(viewer);
      }
      catch (error) {
        handleError(error);
      }
    }
    else if (params.viewer === 'r') {

      var viewerClass = ReviewViewer;

      function onSelect () {
        menu.select.apply(menu.select, arguments);
      }

      function onFocus (lineId) {
        if (menu)
          menu.print(lineId);
      }

      try {

        var save = function () {
          /* FIXTHIS: loader ... */
          return transcript.save({status: 'FINAL'});
        }

        var viewer = new ReviewViewer(transcript.getImageUrl(), transcript.getPageXml(), onSelect, onFocus);
        // Menu(viewer)
        var menu = new OtherMenu(viewer, transcript.getPageDoc(), save, handleError);
      }
      catch (error) {
        handleError(error);
      }
        
    }
    else {
      handleError(new Error("NotImplemented"));
    }

  }

  function handleError (error) {

    console.error(error);

    var debugNode = document.querySelector('.js-debug');
    var textNode = debugNode.querySelector('textarea');
    textNode.value = error.stack;
    debugNode.classList.add('error');
  }

}

/* TODO: handle page locking */

function CurrentTranscript (colId, docId, pageNr) {

  console.assert(typeof colId === 'number');
  console.assert(typeof docId === 'number');
  console.assert(typeof pageNr === 'number');

  var imageData = null;
  var pageData = null;
  var pageDoc = null;

  function load (colId, docId, pageNr) {

    console.assert(typeof colId === 'number');
    console.assert(typeof docId === 'number');
    console.assert(typeof pageNr === 'number');

    return API.getInstance().then(function (api) {
      return Promise.all([
        api.getPage(colId, docId, pageNr).then(function (data) {
          imageData = data;
          console.assert(imageData instanceof Object);
          console.assert(typeof imageData.url === 'string');
        }),
        api.getCurrentTranscriptMetaData(colId, docId, pageNr).then(function (data) {
          console.assert(data instanceof Object);
          console.assert(typeof data.url === 'string');
          pageData = data;
          return getXML(pageData.url).then(function (doc) {
            pageDoc = doc;
          });
        })
      ]);
    });

  }

  return {
    isLocked: function () {
      return API.getInstance().then(function (api) {
        return api.isPageLocked(colId, docId, pageNr);
      });
    },
    load: function () {
      var that = this;

      return load(colId, docId, pageNr).then(function () {
        return that;
      });
    },
    save: function (params) {
      if (!(pageDoc instanceof Document))
        throw new Error("Data not loaded: Have called .load()?");

      params = params || {};

      console.assert(params.status in CurrentTranscript.STATUS);

      var that = this;
      return API.getInstance().then(function (api) {

        var p = api.saveTranscript(colId, docId, pageNr, pageDoc, {
          status: params.status,
          note: params.note,
          parent: that.getId(),
          overwrite: params.overwrite,
          toolName: params.toolName
        });
        p.then(function (data) {
          /* NOTE: update trpTranscriptMetaData AKA pageData */
          console.assert(data !== undefined);
          pageData = data;
        });
        return p;
      });
    },
    getImageUrl: function () {
      if (imageData === null)
        throw new Error("Data not loaded: Have called .load()?");
      return imageData.url;
    },
    getPageXml: function () {
      if (!(pageDoc instanceof Document))
        throw new Error("Data not loaded: Have called .load()?");
      return pageDoc.documentElement;
    },
    getPageRoot: function () {
      if (!(pageDoc instanceof Document))
        throw new Error("Data not loaded: Have called .load()?");
      return pageDoc.documentElement;
    },
    getPageDoc: function () {
      if (!(pageDoc instanceof Document))
        throw new Error("Data not loaded: Have called .load()?");
      return pageDoc;
    },
    getId: function () {
      if (pageData === null)
        throw new Error("Data not loaded: Have called .load()?");
      console.assert(typeof pageData.tsId === 'number');
      return pageData.tsId;
    },
    setPageDoc: function (newPageDoc) {
      console.assert(newPageRoot instanceof Document);
      if (!(pageDoc instanceof Document))
        throw new Error("Data not loaded: Have called .load()?");
      pageDoc = newPageDoc;
    },
    setPageRoot: function (newPageRoot) {
      console.assert(newPageRoot instanceof Element);
      if (!(pageDoc instanceof Document))
        throw new Error("Data not loaded: Have called .load()?");
      pageDoc.replaceWith(newPageRoot, pageDoc.documentElement);
    }
  };

}

CurrentTranscript.load = function (colId, docId, pageNr) {
  var t = new CurrentTranscript(colId, docId, pageNr);
  return t.load();
}

CurrentTranscript.STATUS = {
  FINAL: 'FINAL',
  DONE: 'DONE',
  IN_PROGRESS: 'IN_PROGRESS'
};

function PageMetaData (id, imageData, pageData) {

  console.assert(id instanceof Object);
  console.assert(typeof id.colId === 'number');
  console.assert(typeof id.docId === 'number');
  console.assert(typeof id.pageNr === 'number');

  console.assert(imageData instanceof Object);
  console.assert(pageData instanceof Object);

  var imageUrl = imageData.url;
  var pageUrl = pageData.url;

  console.assert(typeof imageUrl === 'string');
  console.assert(typeof pageUrl === 'string');

  return {
    save: function () {
      throw new Error("NotImplemented");
      return Promise.resolve();
    },
    getImageUrl: function () { return imageUrl; },
    getPageUrl: function () { return pageUrl; },
    retrievePageXML: function () { return getXML(pageUrl); },
    retrieveImage: function () { return getIMG(imageUrl); }
  };
}

PageMetaData.retrieve = function (colId, docId, pageNr) {

  console.assert(typeof colId === 'number');
  console.assert(typeof docId === 'number');
  console.assert(typeof pageNr === 'number');

  var id = {
    colId: colId, docId: docId, pageNr: pageNr
  };

  return loadPageMetaData(colId, docId, pageNr).then(function (data) {
    return new PageMetaData(id, data.image, data.page);
  });
}

function loadPageMetaData (colId, docId, pageNr) {

  console.assert(typeof colId === 'number');
  console.assert(typeof docId === 'number');
  console.assert(typeof pageNr === 'number');

  return new Promise(function (resolve, reject) {

    API.getInstance().then(function (api) {
      var p = Promise.all([
        api.getCurrentTranscriptMetaData(colId, docId, pageNr),
        api.getPage(colId, docId, pageNr),
      ]);

      p.catch(reject);

      p.then(function (list) { resolve({page: list[0], image: list[1]}); });

    });
  });
}

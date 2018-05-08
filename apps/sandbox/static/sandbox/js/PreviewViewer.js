function PreviewViewer () {

  var viewerNode = document.querySelector('.js-preview-viewer');

  return {
    update: function () {
      // what format?
      viewerNode.textContent = 'The preview at ' + new Date().toString();
    },
    render: function () {
      return new Promise(function (resolve) {
        resolve();
      });
    }
  };

}

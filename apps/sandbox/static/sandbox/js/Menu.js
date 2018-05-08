function Menu (viewer) {

  console.assert(viewer !== null && viewer !== undefined);

  var rootNode = document.querySelector('.js-menu');
  var formNode = rootNode.querySelector('.js-form');

  formNode.addEventListener('submit', function (evt) {
    evt.preventDefault();
  }, false);

  Array.from(formNode.children).forEach(function (node) {
    node.addEventListener('click', handleClick, false);
  });

  function handleClick (evt) {

    /* menu */

    evt.preventDefault();

    if (evt.target.name === 'toggle') {
      switch (evt.target.value) {
        case 'image':
          viewer.toggle('image');
          break;
        case 'layout':
          viewer.toggle('layout');
          break;
        case 'TextRegion':
        case 'TableRegion':
        case 'TableCell':
        case 'TextLine':
        case 'Baseline':
          viewer.toggle(evt.target.value);
          break;
        default:
          console.warn("Invalid value:", evt.target.value);
          break;
      }
    }
    else if (evt.target.name === 'zoom') {
      switch (evt.target.value) {
        case 'in':
          viewer.zoom(Zoomable.IN);
          break;
        case 'out':
          viewer.zoom(Zoomable.OUT);
          break;
        case 'reset':
          viewer.zoom(Zoomable.RESET);
          break;
        default:
          console.warn("Invalid value:", evt.target.value);
          break;
      }
    }
    else {
      console.warn("Invalid name:", evt.target.name);
    }

    /* FIXTHIS: set focus on body so arrow keys can perform scroll */
    document.body.focus();

  }

}

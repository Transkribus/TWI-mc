function Toolbar (selector, actions) {

  actions = actions || {};

  var CLICK = ['BUTTON'];
  var CHANGE = ['SELECT', 'INPUT'];

  var formNode = document.querySelector(selector);
  console.assert(formNode !== null);

  formNode.addEventListener('change', function (evt) {

    if (CHANGE.indexOf(evt.target.nodeName) < 0)
      return;

    evt.preventDefault();

    if (evt.cancelable)
      evt.stopPropagation();

    dispatch(evt.target.name, evt.target.value, evt.target);

  }, false);

  var activeNode = null;
  formNode.addEventListener('mousedown', function (evt) {
    activeNode = document.activeElement;
  }, false);

  formNode.addEventListener('mouseup', function (evt) {
    if (activeNode !== null && CLICK.indexOf(evt.target.nodeName) >= 0)
      activeNode.focus();
  }, false);

  formNode.addEventListener('click', function (evt) {

    // NOTE: do not handle click event for nodes not in CLICK here
    if (CLICK.indexOf(evt.target.nodeName) < 0)
      return;

    evt.preventDefault();

    dispatch(evt.target.name, evt.target.value);

  }, false);

  function dispatch (name, value, node) {

    var action = null;
    var object = actions[name];

    if (typeof object === 'function')
      action = object;
    else if (object instanceof Object)
      action = object[value];

    if (typeof action === 'function')
      action(value, node);
    else
      console.warn("Invalid action", name, value);
  }

  return {
    toggle: function (name) {

      var node = formNode.getElementById(name);

      if (node === null) {
        console.warn("Action not found:", name);
        return;
      }

      if (node.getAttribute('disabled') !== null)
        node.setAttribute('disabled', '');
      else 
        node.removeAttribute('disabled');
    },
    isChecked: function (id) {

      var node = formNode.querySelector('#' + id);

      if (node === null) {
        console.error("Element does not exist: " + id);
        return;
      }
      
      return node.checked;
      
    },
    register: function (name, action) {
      actions[name] = action;
    }
  };
}

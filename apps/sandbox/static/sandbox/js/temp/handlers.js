function PlainTextRenderer () {

  var r = [];

  function open (s) {
  }

  function close (s) {
  }

  function openClose (s) {
    if (s.name === 'br')
      r.push('<br>');
    // else
    //  r.push('<span class="' + s.name + '"/>');
  }

  function text (string, from, to) {
    r.push(string);
  }

  return {
    close: close,
    open: open,
    openClose: openClose,
    handleText: text,
    getResult: function () {
      return r.join('');
    }
  };
}

function BackgroundRenderer () {

  var r = [];

  function open (s) {
    r.push('<span class="' + s.name + '">');
  }

  function close (s) {
    r.push('</span>');
  }

  function openClose (s) {
    if (s.name === 'br')
      r.push('<br>');
    else
      r.push('<span class="' + s.name + '"/>');
  }

  function text (string, from, to) {
    r.push(string);
  }

  return {
    close: close,
    open: open,
    openClose: openClose,
    handleText: text,
    getResult: function () {
      return r.join('');
    }
  };
}

function BorderRenderer () {

  var r = [];

  var segments = [];

  function open (s) {

    var index = segments.indexOf(s);

    if (index < 0) {

      segments.push(s);

      index += segments.length;

    }

    var name = s.name;

    r.push(`<span class="${name}" data-index="${index}">`);

  }

  function close (s) {
    r.push('</span>');
  }

  function openClose (s) {
    if (s.name === 'br')
      r.push('<br>');
    else
      r.push('<span class="' + s.name + '"/>');
  }

  function text (string, from, to) {
    r.push(string);
  }

  return {
    close: close,
    open: open,
    openClose: openClose,
    handleText: text,
    getResult: function () {
      return r.join('');
    }
  };
}

function BracketRenderer () {

  var r = [];

  var segments = [];

  var nodeName = 'span';

  function open (s) {

    var index = segments.indexOf(s);

    if (index < 0) {

      segments.push(s);

      index += segments.length;

    }

    var name = s.name;

    r.push(`<${nodeName} class="${name} start" data-index="${index}"></${nodeName}>`);

  }

  function close (s) {
    var name = s.name;
    r.push(`<${nodeName} class="${name} stop"></${nodeName}>`);
  }

  function openClose (s) {
    if (s.name === 'br')
      r.push('<br>');
    else {
      var name = s.name;
      r.push(`<${nodeName} class="start stop ${name}"></${nodeName}>`);
    }
  }

  function text (string, from, to) {
    r.push(string);
  }

  return {
    close: close,
    open: open,
    openClose: openClose,
    handleText: text,
    getResult: function () {
      console.log(r.join(''));
      return r.join('');
    }
  };
}

var RENDERERS = {
  text: PlainTextRenderer,
  background: BackgroundRenderer,
  border: BorderRenderer,
  bracket: BracketRenderer
}

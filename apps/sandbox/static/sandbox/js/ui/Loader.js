function Loader () {

  var view = document.querySelector('.js-loader');
  var meter = view.querySelector('.js-meter');

  var nTicks; // total ticks
  var iTicks = 0; // current ticks
  var sTicks = 0; // skipped ticks

  var isAnimating = false;

  meter.addEventListener('transitionend', handleTransition, false);

  function handleTransition (evt) {

    evt.preventDefault();

    if (evt.cancelable)
      evt.stopPropagation();

    if (sTicks <= 0)
      isAnimating = false;
    else {
      iTicks += sTicks;
      sTicks = 0;
      update();
    }
  }

  function updateMeter (percent) {
    isAnimating = true;
    meter.style.transform = 'translateX(' + (percent - 100) + '%)';
  }

  function update () {
    updateMeter(Math.round(100 * Math.min(iTicks / nTicks, 1)));
  }

  function reset () {
    iTicks = 0;
    nTicks = undefined;
    updateMeter(0);
  }
  var sTicks = 0;
  return {
    set: function (value) { nTicks = value; },
    notify: function () {
      if (!isAnimating) {
        iTicks++;
        update();
      }
      else
        sTicks++;
    },
    show: function show () {
      document.body.classList.add('loading');
    },
    hide: function hide () {
      document.body.classList.remove('loading');
      reset();
    }
  };
}

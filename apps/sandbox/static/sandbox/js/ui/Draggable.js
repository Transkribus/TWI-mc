function Draggable (dragNode) {

  // FIXME: do not change focus after dragging ...

  // var dragNode = scopeNode.querySelector('.js-scrollable');

  var scrollX = null;
  var scrollY = null;

  var startX = 0;
  var startY = 0;

  var deltaX = 0;
  var deltaY = 0;

  var isDragging = false;
  var isReady = true;

  dragNode.addEventListener('dragstart', function (evt) {
    evt.preventDefault();
  }, false);

  dragNode.addEventListener('mousedown', startDrag, false);
  document.addEventListener('mousemove', drag, true);
  document.addEventListener('mouseup', stopDrag, false);
  // document.addEventListener('mouseout', stopDrag, false);

  dragNode.addEventListener('touchstart', startDrag, false);
  document.addEventListener('touchmove', drag, false);
  document.addEventListener('touchend', stopDrag, false);
  // document.addEventListener('mouseout', stopDrag, false);  

  function update () {
    dragNode.scrollLeft = scrollX - deltaX;
    dragNode.scrollTop = scrollY - deltaY;
    isReady = true;
  }

  function startDrag (evt) {

    if (isDragging) return;

    // evt.preventDefault();
    // if (evt.cancelable)
    //   evt.stopPropagation();

    startX = evt.changedTouches ? evt.changedTouches[0].clientX : evt.clientX;
    startY = evt.changedTouches ? evt.changedTouches[0].clientY : evt.clientY;

    scrollX = dragNode.scrollLeft;
    scrollY = dragNode.scrollTop;

    isDragging = true;

  }

  function drag (evt) {

    if (!isDragging) return;
    if (!isReady) return;

    evt.preventDefault();

    if (evt.cancelable)
      evt.stopPropagation();

    // if (isAnimating) return;

    deltaX = (evt.changedTouches ? evt.changedTouches[0].clientX : evt.clientX) - startX;
    deltaY = (evt.changedTouches ? evt.changedTouches[0].clientY : evt.clientY) - startY;

    // deltaX = Math.min(Math.max(deltaX, minDeltaX), maxDeltaX);
    // deltaY = Math.min(Math.max(deltaY, minDeltaY), maxDeltaY);

    // isAnimating = true;
    if (isReady) {
      isReady = false;
      requestAnimationFrame(update);
    }

  }

  // var T = 250;

  function stopDrag (evt) {

    if (!isDragging) return;

    evt.preventDefault();

    if (evt.cancelable)
      evt.stopPropagation();

    isDragging = false;

    // var startT = performance.now()

    // var deltaT;

    // var width = deltaX;
    // var height = deltaY;

    // return;

    // isAnimating = true;
    // requestAnimationFrame(function animate (lastT) {

    //   deltaT = lastT - startT;

    //   deltaX = width * Math.pow(1 - deltaT / T, 2);
    //   deltaY = height * Math.pow(1 - deltaT / T, 2);

    //   update();

    //   if (deltaT < T)
    //     requestAnimationFrame(animate);
    //   else
    //     isAnimating = false;
    // });

  }

}

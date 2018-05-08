function Login () {
  /* FIXTHIS: this should be a modal ... load collection list for user when done ...*/
  /* FIXTHIS: submit only once ... */
  var view = document.querySelector('.js-login');
  var formNode = view.querySelector('form');
  var userNode = formNode.querySelector('.js-user');
  var passwordNode = formNode.querySelector('.js-password');
  var errorNode = formNode.querySelector('.js-error');

  var isReady = true;

  initialize();

  function initialize () {

    addEventListeners();

    Router.getInst().then(function (router) {
      router.add(Router.LOGIN, view);
    });

  }

  function addEventListeners () {
    userNode.addEventListener('input', hideError, false);
    passwordNode.addEventListener('input', hideError, false);
    formNode.addEventListener('submit', onFormSubmit, false);
  }

  function hideError () {
    if (!errorNode.classList.contains('hidden'))
      errorNode.classList.add('hidden');
  }

  function onFormSubmit (evt) {

    if (!isReady)
      return;

    isReady = false;

    evt.preventDefault();

    /* FIXTHIS: not clear when spinner gets hidden again .. */
    Spinner.getInst().then(function (spinner) {
      spinner.show();
    });

    submitLogin(userNode.value, passwordNode.value).finally(clearForm);

  }

  function clearForm () {
    passwordNode.value = '';
    // passwordNode.focus();
    isReady = true;
  }

  function submitLogin (username, password) {

    console.assert(typeof username === 'string' && username !== '');
    console.assert(typeof password === 'string' && password !== '');

    return new Promise(function (resolve, reject) {

      API.getInst().then(function (api) {

        var loginPromise = api.postLogin(username, password);

        Storage.getInst().then(function (storage) {

          loginPromise.then(function (userData) {
            userData.loggedIn = true;
            storage.put('userData', userData);
          });

          loginPromise.catch(function (userData) {
            userData.loggedIn = false;
            storage.put('userData', userData);
          });

        });

        loginPromise.then(function (userData) {

            Router.getInst().then(function (router) {
              router.show(Router.MAIN);
            });

        });

        loginPromise.catch(showFormError).then(reject);

      });

    });

  }

  function showFormError (error) {
    errorNode.classList.remove('hidden');
    return Spinner.getInst().then(function (spinner) {
      return spinner.hide();
    });
  }

}

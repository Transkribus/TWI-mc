function LoginDialog () {

  var rootNode;

  var formNode;
  var usernameNode;
  var passwordNode;

  var isInit = false;

  function initialize () {
    rootNode = document.querySelector('.js-login-dialog');
    formNode = rootNode.querySelector('.js-login');
    usernameNode = rootNode.querySelector('.js-username');
    passwordNode = rootNode.querySelector('.js-password');
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

      var loginPromise = login();

      loginPromise.catch(function (error) {
        console.warn("Login failed!");
      });

      loginPromise.then(function (userData) {
        console.debug(userData)
      });

      return loginPromise;

    });

  }

  function login () {
    return new Promise(function (resolve) {

      /* can load additional resources, e.g. html fragment, styles here */

      if (!isInit)
        initialize();

      formNode.addEventListener('submit', handleSubmit, false);

      resetForm();

      var timer = null;

      requestAnimationFrame(function () {

        timer = setTimeout(handleTransition, 1000);

        rootNode.addEventListener('transitionend', handleTransition, false);
        if (!rootNode.classList.contains('visible'))
          rootNode.classList.add('visible');
      });

      function handleTransition (evt) {

        if (evt !== undefined) {
          evt.preventDefault();

          if (evt.cancelable)
            evt.stopPropagation();
        }

        if (timer !== null)
          clearTimeout(timer)

        rootNode.removeEventListener('transitionend', handleTransition);

      }

      function handleSubmit (evt) {

        evt.preventDefault();

        API.getInstance().then(function (api) {
          var loginPromise = api.login(usernameNode.value, passwordNode.value);

          loginPromise.then(function (data) {

            if (rootNode.classList.contains('visible'))
              rootNode.classList.remove('visible');
          });

          loginPromise.then(resolve);

          loginPromise.catch(function (error) {
            /* FIXTHIS: show error state */
            if (!formNode.classList.contains('error'))
              formNode.classList.add('error');

            console.warn("login failed");

            resetForm();

          });

        });

      }

      function resetForm () {
        formNode.reset();
        usernameNode.focus();
      }

    });
  }

  return {
    login: function () {
      return checkLogin().catch(waitForLogin);
    },
    logout: function () {
      return API.getInstance().then(function (api) {
        return api.checkSession().then(function () {
          return api.logout();
        });
      })
    }
  };
}

LoginDialog.getInstance = (function () {
  var inst = null;
  return function () {
    return new Promise(function (resolve, reject) {
      if (inst === null)
        inst = new LoginDialog();
      resolve(inst);
    });
  };
}());

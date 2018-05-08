/* FIXTHIS: implement build search params from func args */
/* FIXTHIS: error handling, e.g. not logged in, reject promise ... probably best doing this for HTTP errors only? */
/* FIXTHIS: handle request timeouts */
/* FIXTHIS: add connection timeout error ... */

function cached (func) {
  /* FIXTHIS: make key method cacheable */
  /* FIXTHIS: implement this using session / localstorage ... */
  var results = {};
  return function () {
    var key = JSON.stringify(arguments);
    if (key in results)
      return results[key];
    return (results[key] = func.apply(this, arguments));
  }
}

function extend (src, dest) {
  for (var name in src) {
    if (src.hasOwnProperty(name)) {
      var prop = src[name];
      if (typeof prop === 'function')
        prop.bind(dest);
      dest[name] = prop;
    }
  }
}

function API () {

  var baseUrl = 'https://transkribus.eu/TrpServer/rest';

  function build (path, params) {
    console.assert(typeof path === 'string');

    var u = new URL(baseUrl);

    if (u.pathname[u.pathname.length - 1] !== '/' && path[0] !== '/')
      u.pathname += '/' + path;
    else
      u.pathname += path;

    params = params || {};

    for (var key in params) {
      if (params[key] instanceof Array) {
        var list = params[key] || [];
        for (var index = 0; index < list.length; index++) {
          if (list[index] !== undefined)
            u.searchParams.append(key, list[index]);
          else
            console.warn("Ignoring param." + key + ": undefined");
        }
      }
      else if (params[key] !== undefined)
        u.searchParams.append(key, params[key]);
      else
        console.warn("Ignoring param." + key + ": undefined");
    }

    return u.toString();
  }

  function join () {
    var s, segs = [];
    for (var index = 0; index < arguments.length; index++) {
      s = arguments[index];
      console.assert(s[0] !== '/' && s[s.length - 1] !== '/');
      // while (s[0] !== undefined && s[0] === '/')
      //   s = s.slice(1);
      segs.push(s);
    }
    return '/' + segs.join('/');
  }

  /* FIXTHIS: set session cookie here ... */

  function post (path, data, params) {
    return postJSON(build(path, params), data || params);
  }

  function get (path, params) {
    return getJSON(build(path, params));
  }

  function _postXML (path, doc, params) {
    console.assert(doc instanceof Document);
    return postXML(build(path, params), doc);
  }

  function _getXML (path, params) {
    return getXML(build(path, params));
  }

  return {
    login: function (username, password) {
      console.assert(username !== undefined && password !== undefined)
      // return post(build('/auth/login', {user: username, pw: password}));
      return post('/auth/login', {user: username, pw: password});
    },
    logout: function () {
      return post('/auth/logout');
    },
    checkSession: function () {
      return get('/auth/checkSession');
      // return _getXML('/auth/checkSession');
    },

    getColInfo: cached(function (colId) {
      console.assert(typeof colId === 'number');
      return get(join('collections', colId, 'metadata'));
    }),

    getDocInfo: cached(function (colId, docId) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      return get(join('collections', colId, docId, 'metadata'));
    }),

    getDocList: cached(function (colId, index, nValues, sortColumn, sortDirection) {
      console.assert(typeof colId === 'number');

      var params = {};
      params.index = index;
      params.nValues = nValues;
      params.sortColumn = sortColumn;
      params.sortDirection = sortDirection;

      return get(join('collections', colId, 'list'), params);
    }),
    getColList: cached(function (index, nValues, sortColumn, sortDirection) {

      var params = {};
      params.index = index;
      params.nValues = nValues;
      params.sortColumn = sortColumn;
      params.sortDirection = sortDirection;

      return get('/collections/list', params);
    }),

    getColCount: function () {
      throw new Error("Not Implemented");
    },

    getDocCount: function (colId) {
      throw new Error("Not Implemented");
      console.assert(typeof colId === 'number');
    },

    findDocuments: function (colId, title, index, nValues) {
      throw new Error("Not Implemented.");

      console.assert(typeof colId === 'number');
      console.assert(typeof title === 'string');

      return get(join('collections', 'findDocuments'), {
        title: title,
        exactMatch: false,
        caseSensitive: false,
        index: index,
        nValues: nValues
      });
    },

    getDocById: function (colId, docId, nrOfTranscripts, status) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      return get(join('collections', colId, docId, 'fulldoc'), {
        status: status,
        nrOfTranscripts: nrOfTranscripts
      });
    },

    getJobStatus: function (jobId) {
      console.assert(jobId !== undefined && jobId !== undefined);
      return get('/jobs/' + jobId).then(fixTrpJobStatus);
    },
    getJobData: function (jobId) {
      console.assert(jobId !== undefined);
      return get('/jobs/' + jobId).then(parseTrpKwsResult);
    },
    getJobList: function (params) {
      params = params || {};
      return get('/jobs/list', params).then(fixTrpJobList);
    },
    getJobCount: function (params) {
      params = params || {};
      return get('/jobs/count', params);
    },
    killJob: function (jobId) {
      console.assert(jobId !== undefined);
      return post(join('/jobs', jobId, 'kill'));
    },

    getCurrentTranscriptMetaData: function (colId, docId, pageNr) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      return get(join('collections', colId, docId, pageNr, 'curr'));
    },
    saveTranscript: function (colId, docId, pageNr, document, params) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      console.assert(document instanceof Document);
      return _postXML(
        join('collections', colId, docId, pageNr, 'text'), document, params);
    },
    updatePageStatus: function (colId, docId, pageNr, tsId, status, note) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      console.assert(typeof tsId === 'number');
      return post(join(
        'collections',
        colId, docId, pageNr, tsId,
        'status'
      ), {}, {status: status});
    },

    getPage: function (colId, docId, pageNr) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      return get(join('collections', colId, docId, pageNr));
    },
    isPageLocked: function (colId, docId, pageNr) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      return get(join('collections', colId, docId, pageNr, 'isLocked'));
    },
    listPageLocks: function (colId, docId, pageNr) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      return get(join('collections', colId, docId, pageNr, 'listLocks'));
    },
    lockPage: function (colId, docId, pageNr, isLocked) {
      /* NOTE: send no param or false -> locks, send true: unlocks */
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      console.assert(isLocked === true || isLocked === false);
      // return post(join('collections', colId, docId, pageNr, 'lock'), {}, {type: true});
      // return post(join('collections', colId, docId, pageNr, 'lock'));
      return post(join('collections', colId, docId, pageNr, 'lock'), {}, {type: !isLocked});
    },

    postKwsSearch: function (colId, docId, queryStringList) {
      console.assert(colId !== undefined && docId !== undefined);
      console.assert(queryStringList instanceof Array && queryStringList.length > 0);

      return post(join(
        'collections',
        colId, docId,
        'kwsSearch'
      ), {}, {query: queryStringList, caseSensitive: true});

    },

    getKwsHitList: function (queryId, index, nValues, sortColumnField, sortDirection, filterKeyword) {
      /* FIXTHIS: implement sorting, filtering, etc. */

      console.assert(typeof queryId === 'number');
      console.assert(typeof index === 'number');
      console.assert(typeof nValues === 'number');

      var params = {
        index: index,
        nValues: nValues
      };

      if (typeof filterKeyword === 'string' && filterKeyword !== '')
        params.keyword = filterKeyword;

      return get('/kws/queries/' + queryId + '/hits', params).then(fixTrpKwsHitList);
    },
    getKwsQueryList: function (index, nValues) {
      return get('/kws/queries', {
        index: index,
        nValues: nValues
      }).then(fixTrpKwsQueryList);
    }
  };

  // var api;

  // if (isMock() === true)
  //   api = new MockAPI();
  // else
  //   api = new TrpAPI();

  // console.assert(api !== undefined);

  // return extend(api, this);

  // function isMock () {
  //   return API.MOCK || hasMockFlag();
  // }

  // function hasMockFlag () {
  //   var url = new URL(document.location);
  //   return parseInt(url.searchParams.get('mock')) === 1;
  // }

}

function fixTrpJobList (trpJobList) {
  trpJobList.forEach(function (item) {
    item.jobId = parseInt(item.jobId);
  });
  return trpJobList;
}

function fixTrpJobStatus (trpJobStatus) {
  trpJobStatus.jobId = parseInt(trpJobStatus.jobId);
  return trpJobStatus;
}

function fixTrpKwsHitList (trpKwsHitList) {

  console.assert(trpKwsHitList.trpKwsHit instanceof Array);
  console.assert(trpKwsHitList instanceof Object);
  console.assert(typeof trpKwsHitList.total === 'number');
  
  trpKwsHitList.trpKwsHit.forEach(function (item) {
    item.imgRect = getImgRectWithPadding(getImgRect(item.imgUrl));
    // item.imgUrl = getImgUrlWithFileType(item.imgUrl);
    item.imgUrl = getImgUrlFromRect(item.imgUrl, item.imgRect);
    item.confidence = Math.round(item.confidence * 100) / 100;
  });

  return trpKwsHitList;
}

function fixTrpKwsQueryList (trpKwsQueryList) {
  console.assert(trpKwsQueryList.trpKwsQuery instanceof Array);

  trpKwsQueryList.trpKwsQuery.forEach(function (data) {

    console.assert(data.keyWordList !== undefined);
    console.assert(data.keyWordList.keyWords instanceof Array);

    data.state = data.status === 'Completed' ? 'FINISHED' : data.status.startsWith('Failed') ? 'FAILED' : 'RUNNING';
    data.scope = data.scope.indexOf('Document') >= 0 ? 'doc' : 'col';;
    data.keywordList = data.keyWordList.keyWords;
    // data.timeago = getTimeAgo(data.created);

    data.keyWordList.keyWords.forEach(function (data) {
      data.keyword = data.keyWord;
    });

    if (data.docList instanceof Array)
      ;
    else
      data.docList = data.docList.docIds;
    data.colList = data.collectionList.colIds;
  });
  return trpKwsQueryList;
}

function getImgUrlWithFileType (imgUrl) {
  var url = new URL(imgUrl);
  url.searchParams.set('fileType', 'view');
  return url.toString();
}

function getImgUrlFromRect (imgUrl, imgRect) {
  var url = new URL(imgUrl);
  var cropParam = [imgRect.x, imgRect.y, imgRect.width, imgRect.height].join('x');

  url.searchParams.set('crop', cropParam);

  return url.toString();
}

function getImgRect (imgUrl) {

  console.assert(imgUrl !== undefined);

  var url = new URL(imgUrl);      

  var cropRect = url.searchParams.get('crop').split('x');
  
  /* FIXTHIS: have this added to data from server api */
  return {
    x: parseInt(cropRect[0]),
    y: parseInt(cropRect[1]),
    width: parseInt(cropRect[2]),
    height: parseInt(cropRect[3])
  };

}

function getImgRectWithPadding (rect) {
  var paddingX = Math.round(rect.height * 0.25);
  return {
    x: Math.max(0, rect.x - paddingX),
    y: rect.y,
    width: rect.width + Math.round(2.5 * paddingX),
    height: rect.height
  };
}

API.getInstance = (function (undefined) {
  var api;
  return function () {
    if (api === undefined)
      api = new API();
    return Promise.resolve(api);
  };
}());

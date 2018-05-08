function MockAPI () {

  /* FIXTHIS: implement real postJSON */
  function createPromise () {
    var resolve, reject;
    var r = {};
    var p = new Promise(function (s, j) { r.resolve = s; r.reject = j; });
    p.deferred = r;
    return p;
  }

  var sessionId;

  function update (requestOrWhatever) {
    sessionId = 42;
  }

  function reset () {
    sessionId = undefined;
  }

  var nStatusPoll = 4;
  var isCheckSession = false;

  return {
    login: function (username, password) {
      console.assert(username !== undefined && password !== undefined)
      var p = new Promise(function (resolve, reject) {
	setTimeout(function () {
	  if (username === 'fail@fail') {
            reject(new Error("Login failed for some reason."));
	  }
	  else {
            resolve(LOGIN)
	  }
	}, 500 + 500 * Math.random());
      });

      p.then(update);
      p.catch(reset);

      return p;
    },
    logout: function () {
      return new Promise(function (resolve) {
	setTimeout(function () {
	  resolve();
	}, 250 + 500 * Math.random());
      });
    },
    checkSession: function () {

      return new Promise(function (resolve, reject) {

        setTimeout(function () {
          if (sessionId === undefined) {
            return reject(new Error("Not logged in ... "));
          }
          else
            return resolve();
        }, 250 + 250 * Math.random());
        
      });
    },
    getColList: cached(function () {
      console.assert(sessionId !== undefined, "Invalid sessionId, try logging in first.");
      return new Promise(function (resolve) {
	setTimeout(function () {
          resolve(COL_LIST);
	}, 500 + 500 * Math.random());
      });
    }),
    getDocList: cached(function (colId) {

      console.assert(sessionId !== undefined);
      console.assert(colId !== undefined);

      return new Promise(function (resolve) {

	if (colId === 2805)
	  setTimeout(function () {
            resolve(DOC_LIST_2805);
	  }, Math.random() * 1000);
	else if (colId === 4915)
	  setTimeout(function () {
            resolve(DOC_LIST_4915);
	  }, 1000 * Math.random());
	else {
	  setTimeout(function () {
            reject(Error("Invalid value for 'colId'"));
	  }, 1000 * Math.random());
	}
      });
    }),

    getCurrentTranscriptMetaData: function (colId, docId, pageNr) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      return new Promise(function (resolve) {
        setTimeout(function () {
          resolve(TRANSCRIPT_META_DATA);
        }, 500 * (1 +  Math.random()));
      });
    },
    getPage: function (colId, docId, pageNr) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      return new Promise(function (resolve) {
        setTimeout(function () {
          resolve(PAGE);
        }, 500 * (1 +  Math.random()));
      });
    },
    isPageLocked: function (colId, docId, pageNr) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      console.assert(typeof pageNr === 'number');
      return new Promise(function (resolve) {
        setTimeout(function () {
          resolve(true);
        }, 500 * (1 +  Math.random()));
      });
    },

    postSearchQuery: function (colId, docId, queryStringList, scoreLimit) {
      console.assert(sessionId !== undefined);
      console.assert(colId !== undefined && docId !== undefined);
      console.assert(queryStringList instanceof Array && queryStringList.length > 0);
      // console.assert(typeof queryString === 'string' && queryString !== '');

      if (scoreLimit === undefined)
        scoreLimit = 0.5;

      return new Promise(function (resolve) {
        setTimeout(function () {
          resolve(42);        
        }, 500 + 500 * Math.random());
      });

    },

    deleteSearchQuery: function (jobId) {
      // '/jobs/42/kill
      throw new Error("Not Implemented");
    },

    getSearchQueryStatus: function (jobId) {
      console.assert(sessionId !== undefined);
      console.assert(jobId !== undefined && jobId !== undefined);

      return new Promise(function (resolve, reject) {

	setTimeout(function () {

          if (nStatusPoll > 0)
            resolve({jobId: jobId, state: Math.random() > 0.5 ? 'RUNNING' : 'WAITING'});
          else if (jobId === 43)
            resolve({jobId: jobId, state: 'FAILED'});
          else
            resolve({jobId: jobId, state: 'FINISHED'});

          nStatusPoll--;

	}, 500 + 500 * Math.random());

      });

    },
    getSearchQueryResultList: function (jobId, forReal) {
      console.assert(jobId !== undefined);
      console.assert(sessionId !== undefined);

      var results;

      if (!forReal)
        results = createSearchQueryResultList(24);
      else
        results = parseTrpKwsResult(RESULT);
        // results = RESULT;

      return new Promise(function (resolve) {
	setTimeout(function () {
	  resolve(results);
	}, 1000);
      });
    },
    getKwsHitList: function (queryId, index, nValues, sortColumnField, sortDirection, filterKeyword) {

      /* FIXTHIS: add sortColumn, etc. */

      console.assert(typeof queryId === 'number');
      console.assert(sessionId !== undefined);

      console.assert(typeof index === 'number');
      console.assert(typeof nValues === 'number');
      // console.assert(typeof sortColumnField === 'string');
      // console.assert(sortDirection === 'asc' || sortDirection === 'desc');

      var f = sortDirection === 'asc' ? -1 : 1;

      return new Promise(function (resolve) {
        setTimeout(function () {
          if (!sortColumnField && !sortDirection)
            resolve(paginated(filtered(fixTrpKwsHitList(KWS_HIT_LIST))));
          else
            resolve(paginated(sorted(filtered(fixTrpKwsHitList(KWS_HIT_LIST)))));
        }, 250 + Math.random() * 500);
      });

      function filtered (trpKwsHitList) {
        if (filterKeyword !== null) {

          var hitList = clone(trpKwsHitList.trpKwsHit);

          hitList = hitList.filter(function (item) {
            return keyword === filterKeyword;
          });

          trpKwsHitList.total = hitList.length;
          trpKwsHitList.trpKwsHit = hitList;

          return trpKwsHitList;
        }
        else
          return trpKwsHitList;
      }

      function paginated (trpKwsHitList) {
        trpKwsHitList = clone(trpKwsHitList);
        var hitList = trpKwsHitList.trpKwsHit;
        trpKwsHitList.trpKwsHit = hitList.slice(index, index + nValues);
        return trpKwsHitList;
      }

      function sorted(trpKwsHitList) {
        var hitList = trpKwsHitList.trpKwsHit;        
        hitList.sort(function (itemA, itemB) {
          var a = itemA[sortColumnField];
          var b = itemB[sortColumnField];
          if (typeof a === 'number' && typeof b === 'number')
            return f * (b - a);
          else if (typeof a === 'string' && typeof b === 'string')
            return f * (a.localeCompare(b));
          else
            throw new Error("NotImplemented");
        });
        return trpKwsHitList;
      }
    },
    getKwsQueryList: function (index, nValues) {

      console.assert(typeof index === 'number');
      console.assert(typeof nValues === 'number');

      return new Promise(function (resolve) {

        setTimeout(function () {
	  resolve(paginated(fixTrpKwsQueryList(KWS_QUERY_LIST)));
        }, 250 * (1 + Math.random()));

      });

      function paginated (trpKwsQueryList) {
        trpKwsQueryList = clone(trpKwsQueryList);
        var queryList = trpKwsQueryList.trpKwsQuery;
        trpKwsQueryList.trpKwsQuery = queryList.slice(index, index + nValues);
        return trpKwsQueryList;
      }

    },
    getJobList: (function () {
      var isFirst = true;

      fixTrpJobList(JOB_LIST);

      return function (params) {

        params = params || {};

        var type = 'CITlab Keyword Spotting';
        var sortColumn = 'startTime';
        var sortDirection = 'desc';

        return new Promise(function (resolve, reject) {

          setTimeout(function () {
            if (params.status !== undefined) {
              resolve(JOB_LIST.filter(function (item) {
                return item.state === params.status;
              }));
            }
            else {
              if (isFirst)
                resolve(JOB_LIST);
              else 
                resolve(JOB_LIST);
              isFirst = false;
            }

          }, 250 + 250 * Math.random());
        });
      }
    }()),
    getJobCount: (function () {

      var testData = {
        'CREATED': 0,
        'RUNNING': 1,
        'WAITING': 0,
        'FINISHED': Math.ceil(Math.random() * 100),
        'CANCELED': Math.ceil(Math.random() * 10),
        'FAILED': Math.ceil(Math.random() * 10)
      };

      var defaultState = 'DEFAULT';
      Object.keys(testData).reduce(function (value, key) {
        return testData[defaultState] = testData[key] + value;
      }, 0);

      return function (params) {
        params = params || {};
        return new Promise(function (resolve) {
          setTimeout(function () {
            resolve(testData[params.status || defaultState]);
          }, 250 + 250 * Math.random());
        });
      };
    }()),
    killJob: function () {
      return Promise.resolve();
    },
    getColInfo: cached(function (colId) {
      console.assert(typeof colId === 'number');
      return new Promise(function (resolve) {
        setTimeout(function () {
	  resolve(COL_METADATA);
        }, 250 + 250 * Math.random());
      });
    }),
    getDocInfo: cached(function (colId, docId) {
      console.assert(typeof colId === 'number');
      console.assert(typeof docId === 'number');
      return new Promise(function (resolve) {
        setTimeout(function () {
	  resolve(DOC_METADATA);
        }, 250 + 250 * Math.random());
      });
    })
  };

  function clone (obj) {
    return JSON.parse(JSON.stringify(obj));
  }

}

function createSearchQueryResultList (N) {
  N = N || 10;
  var results = [];
  // var N = 10;

  function randint (min, max) {
    return Math.floor(min + Math.random() * (max - min));
  }

  /* FIXTHIS: include queryString in results ... */

  var rect;

  for (var index = 0; index < N; index++) {
    rect = {
      width: randint(50, 300),
      height: randint(60, 120)
    };
    results.push({
      confidence: Math.round(100 * Math.random()) / 100,
      imgUrl: 'https://placehold.it/' + [

        rect.width, rect.height
      ].join('x'),
      imgRect: rect,
      pageNr: randint(1, 100),
      docId: 42,
      colId: 42,
      transcription: 'This is the transcription.',
      keyword: 'keyword'
    });
  }

  results.sort(function (item, nextItem) {
    return item.confidence - nextItem.confidence;
  });
  results.reverse();

  return results;
}

function parseTrpKwsResult (trpData) {
  console.assert(trpData !== undefined);
  console.assert(trpData.trpKwsResult !== undefined);
  console.assert(trpData.trpKwsResult.keyWordList !== undefined);
  console.assert(trpData.trpKwsResult.keyWordList.keyWords !== undefined);
  console.assert(trpData.trpKwsResult.keyWordList.keyWords.hitList !== undefined);
  console.assert(trpData.trpKwsResult.keyWordList.keyWords.hitList.hits !== undefined);

  var hitList = trpData.trpKwsResult.keyWordList.keyWords.hitList.hits;

  function parseTrpHitList (data) {

    // if (Math.random() > 0.5)
    //   data.imgUrl += 'sjkdu8jskdu8u'

    return {
      confidence: Math.round(100 * data.confidence) / 100,
      imgUrl: data.imgUrl,
      imgRect: getTrpImgRect(data.imgUrl),
      pageNo: data.pageNr,
      transcription: data.transcription,
      docId: data.docId,
      colId: data.colId
    };
  }

  return hitList.map(parseTrpHitList);
}

(function (global) {
    var map = {
        'rxjs': '/static/lib/rxjs',
    };

    //packages tells the System loader how to load when no filename and/or no extension
    var packages = {
        'rxjs': {defaultExtension: 'js'},
        'angular2-in-memory-web-api': {defaultExtension: 'js'},
        '/static/dist': {defaultExtension: 'js'},
    };

    var PackageNames = [
        'common',
        'compiler',
        'core',
        'http',
        'platform-browser',
        'platform-browser-dynamic',
        'router-deprecated',
        'upgrade',
    ];

    // Add map entries for each angular package
    PackageNames.forEach(function (pkgName) {
        map['@angular/' + pkgName] = '/static/lib/@angular/' + pkgName;
    });

    // Add package entries for angular packages
    PackageNames.forEach(function (pkgName) {
        packages['@angular/' + pkgName] = {main: pkgName + '.umd.js', defaultExtension: 'js'};
    });

    var config = {
        map: map,
        packages: packages,
        paths: {
            'rxjs/*' : '/static/lib/rxjs/*.js',
        }
    };
    if (global.filterSystemConfig) {
      global.filterSystemConfig(config);
    }
    System.config(config);


})(this);
/*
 Copyright 2016 Google Inc. All Rights Reserved.
 Use of this source code is governed by an MIT-style license that
 can be found in the LICENSE file at http://angular.io/license
 */

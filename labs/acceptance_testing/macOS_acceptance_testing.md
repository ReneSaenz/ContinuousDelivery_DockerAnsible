# Acceptance Testing for MacOS

## Initial Setup

We need to install `node.js` for our tests. But first, we need to get out of our virtual environment and then install it.
```
$ deactivate
$ brew install nodejs
```

Create a new directory at the top of our source code.
```
$ mkdir code/todobackend-spec
$ ls -l

drwxr-xr-x   68B Jul 15 19:34 todobackend-specs
drwxr-xr-x  204B Jul 12 21:15 todobackend
```

Now we initialize a node project.
```
$ cd todobackend-specs
$ npm init
This utility will walk you through creating a package.json file.
It only covers the most common items, and tries to guess sensible defaults.

See `npm help json` for definitive documentation on these fields
and exactly what they do.

Use `npm install <pkg>` afterwards to install a package and
save it as a dependency in the package.json file.

Press ^C at any time to quit.
package name: (todobackend-specs) <enter>
version: (1.0.0) 0.1.0
description: Todobackend Acceptance Tests
entry point: (index.js) app.js
test command: mocha
git repository: <enter>
keywords: <enter>
author: Rene Saenz
license: (ISC) <enter>
About to write to code/todobackend-specs/package.json:

{
  "name": "todobackend-specs",
  "version": "0.1.0",
  "description": "Todobackend Acceptance Tests",
  "main": "app.js",
  "scripts": {
    "test": "mocha"
  },
  "author": "Rene Saenz",
  "license": "ISC"
}


Is this ok? (yes) yes
```
With the base project in place, we can now install the various node packages required for the acceptance tests.
```
$ npm install bluebird chai chai-as-promised mocha superagent superagent-promise mocha-jenkins-reporter --save
npm notice created a lockfile as package-lock.json. You should commit this file.
npm WARN todobackend-specs@0.1.0 No repository field.

+ chai-as-promised@7.1.1
+ chai@4.1.0
+ mocha@3.4.2
+ bluebird@3.5.0
+ mocha-jenkins-reporter@0.3.8
+ superagent-promise@1.1.0
+ superagent@3.5.2
added 69 packages in 3.346s
```
__NOTE:__ The `--save` flag which will add these packages as dependencies in the `package.json` file
```
$ cat package.json
{
  "name": "todobackend-specs",
  "version": "0.1.0",
  "description": "Todobackend Acceptance Tests",
  "main": "app.js",
  "scripts": {
    "test": "mocha"
  },
  "author": "Rene Saenz",
  "license": "ISC",
  "dependencies": {
    "bluebird": "^3.5.0",
    "chai": "^4.1.0",
    "chai-as-promised": "^7.1.1",
    "mocha": "^3.4.2",
    "mocha-jenkins-reporter": "^0.3.8",
    "superagent": "^3.5.2",
    "superagent-promise": "^1.1.0"
  }
}
```
The `chai` and `mocha` packages are used for creating tests. The `superagent` is used to create an easy to use HTTP client, that will be communicating with our todobackend web service we will be testing.
The `bluebird` package adds support for promises, which allow for easier handling to asynchronous calls. Works with `chai-as-promised` and `superagent-promise`.
The `mocha-jenkins-reporter` package allow us to output test reports in a JUnit XML format, compatible with jenkins CI system.


## Writing Acceptance tests



## Running Acceptance tests

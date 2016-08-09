var _ = require('underscore-1.8.3')
var exec = require("child_process").execSync
var Option = require("visicom-option").Option


var pathToCheck = 'D:\\source\\visicom\\vdata\\web\\_tmp\\coverage'
var pythonPath = 'D:\\source\\visicom\\vdata\\bin\\tools\\python27\\python'
var pythonScriptPath = 'D:\\source\\visicom\\vdata\\bin\\lib\\coverage.py'


var log, errorLog;
function main()
{

    var svnStatus = () => {
        var stdout = String(exec('svn status --username=dev-robot --password=qwerty -u ' + pathToCheck))       
        var need = stdout.split('\n').some( (str) => str.trim().startsWith("*") )
        if(need){
            log('In repositry new version')
            exec('svn --username=dev-robot --password=qwerty update ' + pathToCheck);    
            log('Woring copy was updated')
            exec("cmd /c " + pythonPath + " " + pythonScriptPath)
            log("Coverage 'vdata' was updated ")

        }
    }

    Option.of(svnStatus).error(errorLog)
}


var intervalId;
exports.start = function(logger){
    log = logger;
    errorLog = _.partial(log,"ERROR:")
    _.defer(main);
    intervalId = setInterval(main, 60*1000)
}

exports.stop = function(){
    clearInterval(intervalId);
}

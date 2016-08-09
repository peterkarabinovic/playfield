var fs = require('fs')
var path = require('path')
var _ = require('underscore-1.8.3')

var activeDirectory = path.join(__dirname,'../active-scritps/');
var scripts = [];
var scriptByFile = file => scripts.find(s => s.file === file)
var lastModifed = (file) => fs.statSync(activeDirectory + file).mtime
var asApp = process.argv[2];
function logger(name)
{
    var logfile = path.join(__dirname, 'logs', name+'.log');
    var toStr = (it) => typeof(it) !== 'string' ? JSON.stringify(it) : it 
    return function(){
        var now = new Date()
        var msg = now.toLocaleString() + ': '+ _.toArray(arguments).map(toStr).join(' ')
        asApp ? console.log(msg) : fs.appendFile(logfile, msg + '\n');
    }
}
var log = logger('logs')
var errors = logger('errors')

function monitor()
{
    var loadedScripts = scripts.map( s => s.file )
    var fsScripts = fs.readdirSync(activeDirectory).filter( file => file.substr(-3) === '.js');
    var forRemove = _.difference(loadedScripts, fsScripts).map( scriptByFile );
    var forAdd = _.difference(fsScripts, loadedScripts)
    var forUpdate = _.intersection(fsScripts, loadedScripts).map( scriptByFile )
                     .filter( s => s.lm < lastModifed(s.file) )
    // removing
    log('forRemove',forRemove)                  
    forRemove.concat(forUpdate).forEach( s => {
        var name = require.resolve(activeDirectory + path.basename(s.file));
        if(name) {
            s.module.stop && s.module.stop()
            delete require.cache[name];
        }
    });               
    scripts = _.without(scripts, forRemove)
    scripts = _.without(scripts, forUpdate)

    // updateing
    forUpdate = forUpdate.map( s => s.file )
    log('forUpdate',forUpdate)

    // adding
    log('forAdd',forAdd)                  
    forAdd.concat(forUpdate).forEach( file => {
        try {
            var name = path.basename(file);
            var module = require(activeDirectory + name)
            module.start && module.start(logger(name.slice(0,-3)));
            scripts.push( {file:file, module: module, lm: lastModifed(file) } )
        }
        catch(err){
            errors('Failed to load module',file,":\n\t",err.message)
        }
    })
}

fs.watch(activeDirectory, _.debounce(monitor,50,true))

monitor()



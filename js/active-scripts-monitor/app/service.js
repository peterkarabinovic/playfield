var path = require('path')
var os = require('os')
var exec = require("child_process").execSync;
var Option = require("visicom-option").Option

var serviceName = 'Active JavaScripts Monitor'
var description = "nodejs программа которая следит за папкой с js-скриптами и выполняет их по расписанию"

Option.of( () => exec('NET SESSION') )
      .error( () => { 
        console.log("No rights to manage services") 
        process.exit() 
      })

var installed = Option.of( () => exec('sc query "' + serviceName + '"') )
                      .map((it) => true)
                      .orElse(false)

var arch = Option.of( () => os.arch().match(/(32|64)/)[1] ).orElse('32')

var nssmLocation = path.join(__dirname, (arch === '64') ? 'nssm64.exe' : 'nssm.exe') 



var command = process.argv[2]

if(command === 'run') 
{
      if(installed)
        return console.log('Service "' + serviceName + '" already installed.' )
      exec(nssmLocation + ' install "' + serviceName + '" node.exe --harmony main.js')
      exec(nssmLocation + ' set "' + serviceName + '" AppDirectory ' + __dirname)
      exec(nssmLocation + ' set "' + serviceName + '" Description "' + description + '"')
      exec(nssmLocation + ' start  "' + serviceName + '"')
      console.log("Service '" + serviceName + "' install successfully!" )
}
else if(command === 'stop'){
     if(!installed)
      return console.log('Service "' + serviceName + '" doesn\'t  exists.' )
     exec(nssmLocation + ' stop  "' + serviceName + '"')
     exec(nssmLocation + ' remove "' + serviceName + '" confirm')
     console.log("Service '" + serviceName + "' removed successfully!" )
}


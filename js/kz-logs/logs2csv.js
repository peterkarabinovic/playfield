var fs = require("fs");

var content = "";
fs.list("./logs").forEach(function(it){
	content += fs.read("./logs/"+it);
});

fs.write("logs.csv",content);
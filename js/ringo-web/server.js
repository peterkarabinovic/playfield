// Запускает http сервер на 1234 порту
// запускает instance hazercast 
// списко пользователей
//    в памяти это hazercast list of user
//    на диске это файл user-1.json
//    в браузере это списко пользователей
var fs  = require("fs");

var users;
exports.app = function(req) {
   users = users || usersFile(req.port);
   var res = {
       body: [],
       headers: {'Content-Type': 'applicarion.json'},
       status: 200
   };
   
   print(req.pathInfo)
   switch(req.pathInfo){
       case '/': 
           res.body = [getResource('./index.html').content];
           break;
       case '/users':
           res.body = [users.load()];
           break;
           
       case '/users/add': 
           break;
           
       case '/users/delete': 
           break;
           
   }
   return res;     
};
if (require.main === module)
    require("ringo/httpserver").main(module.id);

// filestrore
function usersFile(port){
    var f = {};
    var fn = './users-'+port+'.json';
    f.load = function(){
        return  fs.exists(fn) ? fs.read(fn) : '[]';
    };
    f.save = function(list){
        fs.write(fn, JSON.stringify(list), {append:false});
    };
    return f;
}

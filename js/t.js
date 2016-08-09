
function str() {
    return "".concat.apply("",arguments);
}


var html = ' <!--0.38--> <div class="title"> г. Обухов </div> <div class="desc"> Украина  , Киевская область  , Обуховский район  </div> '

var text = '[\\s\\W]+'
var spase = '\\s*'
var quotes = '[\'""]+'
var title = str('<div\\s+class=[\'"].*title.*[\'"]\\s*>(',text,')</div>')
console.log(html.match(title))
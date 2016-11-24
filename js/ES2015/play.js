
console.log([1,2,3].map(n => n + 1));

function foo(text) {
    return {
        'type': 'foo',
        text
    }
}

console.log( foo('kino') );

var obj = require('./module.js');
console.log(obj);


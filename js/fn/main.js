fn = require('./fn')

console.log(fn.curry)

is = fn.curry(fn.is)
isString = is('string')
console.log(isString('kino'))
console.log(is('string','kino'))
console.log(isString(123))

console.log(fn.filter(isString,[1,2,3,4]))
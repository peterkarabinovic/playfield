
var data = [1,2,3,4,5,6,7,8,9,10]

var res = []
[3,2,5].reduce(function(m,cu){
    res.push(data.slice(m,m+cu))
    return m + cu
},0)

console.log(res)

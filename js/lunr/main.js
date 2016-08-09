var lunr = require('./lunr');

var idx = lunr(function () {
    this.field('title', { boost: 10 })
    this.field('body')
});

idx.add({
    "title": "ден",
    "body": "If music be the food of love, play on: Give me excess of ден it… ",
    "author": "William Shakespeare",
    "id": 1
});    

idx.add({
    "title": "Twelfth-Night",
    "body": "Кино и  немцы день чудесен",
    "author": "William Shakespeare",
    "id": 2
});    

print( JSON.stringify(idx.search("ден")) );



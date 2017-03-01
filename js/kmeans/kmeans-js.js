var kMeans = require('kmeans-js');

var data = 
[[1.0592013597488403],
 [1.0591607093811035],
 [1.0591444969177246],
 [1.0575016736984253],
 [1.0548044443130493],
 [0.9361920952796936],
 [0.7070274353027344]];

var km = new kMeans({
    K: 3
});

km.cluster(data);
while (km.step()) {
    km.findClosestCentroids();
    km.moveCentroids();

    console.log(km.centroids);

    if(km.hasConverged()) break;
}

// console.log('Finished in:', km.currentIteration, ' iterations');
console.log(km.centroids, km.clusters);
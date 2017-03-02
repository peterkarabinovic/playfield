
app.factory('server', function($http, actions){
    var s = {}

    s.dispatch = function(store, action){
        if(action.type == INIT_ACTION){
            $http.get('/tenants/').then(function(d){
                store.next( actions.tenatsLoaded(d));
            });
        }
        store.next(action);
    }
});
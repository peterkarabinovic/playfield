

app.factory('store', function(reducers, server){

    var s = _.extend({}, L.Mixin.Events);
    s.state = {
        "ui": {
            selected_tab: null,
            selected_tenat: null,
            selected_point: null,
            edited_tenat: null,
            edit_point: null
        },
        "tenants":[]        
    }

    s.dispatch = function(action){
        return server.dispatch(s, action);
    }

    s.next = function(action){
        var new_state = _.reduce(reducers, function(s, r){
            return r(s, action);
        }, s.state);

        var props = changes(new_state, s.state);
        for(var pr in props){
            s.fire(pr, {old_state: s.state[pr], new_state: new_state[pr]});
            var props2 = changes(new_state[pr], s.state[pr]);
            for(var pr2 in props2){
                s.fire(pr + '.' + pr2, {old_state: s.state[pr][pr2], new_state: new_state[pr][pr2]});
            }
        }

    }

    return s;
});


// find the properties that is not equals
function changes(obj1, obj2){
    return _.reduce(obj1, function(result, value, key) {
        return _.isEqual(value, obj2[key]) ? result : result.concat(key);
    }, [])
}
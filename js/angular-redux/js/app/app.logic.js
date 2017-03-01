// ACTIONS

var INIT_ACTION = 'init';

var TENAT_SELECT = 'tselect',
    TENAT_EDIT = 'tedit',
    TENAT_NEW_GEOMETRY = 't_newgeometry',
    TENAT_SAVE = 't_save',
    TENAT_LOADED = 't_loaded';

var MAP_DRAWING_POLYGON = "map_drawing"

app.factory('actions', function(){
    return {
        tenatsLoaded: function(d) { return {type: TENAT_LOADED, payload: d} },
    };
})

app.factory('reducers', function(){

    function create_tenat(state, action){
        return {};
    }

    function save_tenat(state, action){
        var tenat = action.payload;
        if(tenat.id) {
            state.tenats = _.map(state.tenats, function(t){
                return t.id === tenat.id ? tenat : t;  
            })
        }
    }
});

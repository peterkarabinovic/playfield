"""
    Bottle HTTP handlers for RESTfull entry points
"""
import json
import dateutil.parser

from bottle import route, request, response, HTTPError
import visicomutils as vu
import sql

@route('/graph')
def graph():
    try:
        with vu.openDb() as db:
            box = request.query['box']
            opt = sql.select_graph(db, box).raiseError().result
            return opt
    except Exception as ex:
        response.status = 400
        return ex.message

@route('/graph-route')
def route_():
    try:
        start = request.query['s'].split(',')
        start_edge = request.query['se']
        finish = request.query['f'].split(',')
        finish_edge = request.query['fe']
        box = ",".join(start + finish)

        with vu.openDb() as db:
            source_pos = sql.edge_pos(db, start_edge, start).raiseError().result
            target_pos = sql.edge_pos(db, finish_edge, finish).raiseError().result
            route = sql.route(db, source_id=start_edge,
                                      source_pos=source_pos,
                                      target_id=finish_edge,
                                      target_pos=target_pos,
                                        box=box).raiseError().result

            return json.dumps(dict(request.query, route=route))
    except Exception as ex:
        response.status = 400
        return ex.message




@route('/graph-restriction', method='POST')
def restriction_add():
    try:
        data = json.load(request.body)
        source_id = data['source']
        target_id = data['target']
        with vu.openDb() as db:
            sql.restriction_add(db, source_id=source_id, target_id=target_id).raiseError()
            return sql.edge_by_id(db, source_id).raiseError().result
    except Exception as ex:
        return json.dumps({"error":ex.message})


@route('/graph-restriction', method='DELETE')
def restriction_remove():
    try:
        data = json.load(request.body)
        source_id = data['source']
        target_id = data['target']
        with vu.openDb() as db:
            sql.restriction_remove(db, source_id=source_id, target_id=target_id).raiseError()
            return sql.edge_by_id(db, source_id).raiseError().result
    except Exception as ex:
        response.status = 400
        return ex.message



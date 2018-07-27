



def select_graph(db, box):
    """

    :param db:
    :param box: [x1,y1,x2,y2]
    :return: edges with restrictions with nodes
    """
    sql = """
        SELECT json_build_object(
            'edges', array_to_json(array_agg(distinct edges.*)),
            'nodes', array_to_json(array_agg(nodes.*))
        )
        FROM (
            SELECT e.id, 
                   e.source, 
                   e.target, 
                   e.cost,
                   e.reverse_cost,
                   array_remove(array_agg(r.*), null) as restrictions,
                   ST_AsGeoJSON(e.geom) as geometry 
            FROM graph.edges e
            LEFT JOIN (SELECT id, source_id, target_id, cost FROM graph.edges_restrictions) as r ON r.source_id = e.id
            WHERE e.geom && ST_MakeEnvelope({})
            GROUP BY e.id, e.source, e.target
        ) as edges
        LEFT JOIN (
            SELECT id,
                   ST_AsGeoJSON(the_geom) as geometry  
            FROM graph.edges_vertices_pgr
        ) as nodes ON nodes.id = edges.source OR nodes.id = edges.target
    """.format(box)
    return db.select_scalar(sql)


def edge_by_id(db, edge_id):
    sql = """
        SELECT row_to_json(edges)
        FROM (
            SELECT e.id, 
               e.source, 
               e.target, 
               e.cost,
               e.reverse_cost,
               array_remove(array_agg(r.*), null) as restrictions,
               ST_AsGeoJSON(e.geom) as geometry 
            FROM graph.edges e
            LEFT JOIN (SELECT id, source_id, target_id, cost FROM graph.edges_restrictions) as r ON r.source_id = e.id
            WHERE e.id = %s
            GROUP BY e.id, e.source, e.target 
        ) as edges    
    """
    return db.select_scalar(sql,edge_id)

def edge_pos(db, edge_id, point):
    sql = """
        SELECT ST_LineLocatePoint(geom, 'SRID=4326;POINT({lng} {lat})'::geometry) 
        FROM graph.edges 
        WHERE id = {edge_id}
    """.format(lng=point[0], lat=point[1], edge_id=edge_id)
    return db.select_scalar(sql)


def route(db, source_id, source_pos, target_id, target_pos, box):
    sql = """
        SELECT seq, id1, id2, ST_AsGeoJSON(geom) as geometry  
        FROM (
        SELECT * FROM pgr_trsp(
           'SELECT id::INTEGER, source::INTEGER, target::INTEGER, cost::float, reverse_cost::float
            FROM graph.edges 
            WHERE geom && ST_Expand(ST_MakeEnvelope({box}), 0.1)',
            {source_edge}, {source_pos}, {target_edge}, {target_pos}, true, true,
           'SELECT cost::float as to_cost, target_id::int4, source_id::text AS via_path
            FROM graph.edges_restrictions'
        )) AS res, lateral (SELECT geom FROM graph.edges WHERE res.id2 = id) as g
        ORDER BY seq
    """.format(source_edge=source_id,
               source_pos=source_pos,
               target_edge=target_id,
               target_pos=target_pos,
               box=box)
    return db.select_dict_list(sql)


def restriction_add(db, target_id, source_id):
    sql = '''
        INSERT INTO graph.edges_restrictions(cost, target_id, source_id)
        VALUES(1000,%s,%s)
    '''
    return db.run_sql(sql, target_id, source_id)

def restriction_remove(db, target_id, source_id):
    sql = '''
        DELETE FROM graph.edges_restrictions
        WHERE target_id = %s AND source_id = %s
    '''
    return db.run_sql(sql, target_id, source_id)

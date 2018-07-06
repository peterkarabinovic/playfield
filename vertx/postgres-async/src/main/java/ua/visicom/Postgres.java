package ua.visicom;

import io.vertx.core.Vertx;
import io.vertx.core.json.JsonObject;
import io.vertx.ext.asyncsql.PostgreSQLClient;
import io.vertx.ext.sql.ResultSet;
import io.vertx.ext.sql.SQLClient;
import io.vertx.ext.sql.SQLConnection;

import java.util.Scanner;

public class Postgres {

    static Vertx vertx = Vertx.vertx();
    public static void main(String[] args)
    {
        JsonObject conf = new JsonObject()
                .put("host", "localhost")
                .put("port", 5432)
                .put("username", "postgres")
                .put("maxPoolSize", 3)
                .put("password", "123")
                .put("database", "vdata")
                .put("queryTimeout", 60 * 1000);


        SQLClient pgClient = PostgreSQLClient.createShared(vertx, conf);

        for (int i = 0; i <= 100; i++)
        {
            pgClient.getConnection(res ->
            {
                if (res.succeeded()) {
                    SQLConnection conn = res.result();
                    System.out.println("start ...");
                    conn.query("select pg_sleep(1);", res2 -> {
                        conn.close();
                        System.out.println("done");
                    });
                }
            });
        }
    }
}

package ua.visicom;

import io.vertx.core.Vertx;
import io.vertx.core.file.FileSystem;

import java.util.List;

public class Files {

    static Vertx vertx = Vertx.vertx();

    public static void main(String[] args) {
        FileSystem fs = vertx.fileSystem();
        List list = fs.readDirBlocking("D://");
        System.out.println(list);
    }


}

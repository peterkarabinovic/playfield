package spark.test.pkg2;

import static spark.Spark.get;


/**
 *
 * @author PV-Kara
 */
public class SparkTest2 
{
    public static void main(String[] args) 
    {
         get("/hello", (req, res) -> "Hello World 1");
    }
    
}

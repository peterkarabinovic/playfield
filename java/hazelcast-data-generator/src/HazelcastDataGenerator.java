
import com.hazelcast.config.ClasspathXmlConfig;
import com.hazelcast.config.Config;
import com.hazelcast.core.Hazelcast;
import com.hazelcast.core.HazelcastInstance;
import java.util.List;
import java.util.Map;

public class HazelcastDataGenerator 
{
    public static void main(String[] args) throws InterruptedException 
    {
        Config cfg = new ClasspathXmlConfig("hazelcast.xml");
        HazelcastInstance instance = Hazelcast.newHazelcastInstance( cfg );
        Map points = instance.getMap("points");
        if(points.isEmpty()) 
        {
            System.out.println("points is empty");
            for(int i=0; i<1000; i++){
                points.put(i, Math.random() * 100 +  "," + Math.random() * 100 );
            }
        }
        else {
            for(int k=0; k < 10; k++) {
                Thread.sleep(5000);
                long i =  Math.round(Math.random() * points.size());
                System.out.println("update i="+i);
                points.put((int)i, "updated");
            }
        }
        
        java.util.Set set = instance.getSet("numbers");
        set.add("1");
        set.add("2");
        set.add("3");
        set.add("4");
        //Thread.sleep(10000);
        //instance.getLifecycleService().shutdown();
    }
}

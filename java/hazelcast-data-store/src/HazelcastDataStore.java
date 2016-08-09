
import com.hazelcast.config.ClasspathXmlConfig;
import com.hazelcast.config.Config;
import com.hazelcast.core.Hazelcast;
import com.hazelcast.core.HazelcastInstance;


/**
 *
 * @author PV-Kara
 */
public class HazelcastDataStore 
{
    public static void main(String[] args) throws InterruptedException 
    {
        Config cfg = new ClasspathXmlConfig("hazelcast.xml");
        HazelcastInstance instance = Hazelcast.newHazelcastInstance( cfg );
        //Thread.sleep(10000);
        //instance.getLifecycleService().shutdown();
    }
}

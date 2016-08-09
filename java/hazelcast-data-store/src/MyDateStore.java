
import com.hazelcast.core.MapStore;
import java.util.Collection;
import java.util.Map;
import java.util.Set;

public class MyDateStore implements MapStore
{
    public void store(Object k, Object v) 
    {
        System.out.println("store " + k + "=" + v);
    }

    @Override
    public void storeAll(Map map) {
        System.out.println("storeAll " + map);
    }

    @Override
    public void delete(Object k) {
        
    }

    @Override
    public void deleteAll(Collection clctn) {
        
    }

    @Override
    public Object load(Object k) {
        System.out.println("load " + k);
        return null;
    }

    @Override
    public Map loadAll(Collection clctn) {
        System.out.println("loadAll " + clctn);
        return null;
    }

    @Override
    public Set loadAllKeys() {
        System.out.println("loadAllKeys ");
        return null;
    }
    
}

package test.nashorn;

import java.util.Date;
import javax.script.Bindings;
import javax.script.Invocable;
import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;
import javax.script.SimpleBindings;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import ua.visicom.helpers.Files;

/**
 *
 * @author PV-Kara
 */
public class TestNashorn 
{

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception
    {
        ScriptEngine engine = new ScriptEngineManager().getEngineByName("nashorn");
        String script = Files.readFromClasspath("test/nashorn/script.js", TestNashorn.class);
        engine.eval(script);
        Invocable invocable = (Invocable) engine;
        System.out.println(invocable.invokeFunction("fun1", "Петр"));
        invocable.invokeFunction("fun2", new Date());
        
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        DocumentBuilder db = dbf.newDocumentBuilder();
        Document document = db.newDocument();
        script = Files.readFromClasspath("test/nashorn/script_2.js", TestNashorn.class);
        Bindings b = new SimpleBindings();
        Element el = document.createElement("div");
        b.put("document", document);
        b.put("window", new Object());
        engine.eval(script, b);

    }
    
}

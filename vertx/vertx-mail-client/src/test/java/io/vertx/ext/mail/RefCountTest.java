/*
 *  Copyright (c) 2011-2015 The original author or authors
 *
 *  All rights reserved. This program and the accompanying materials
 *  are made available under the terms of the Eclipse Public License v1.0
 *  and Apache License v2.0 which accompanies this distribution.
 *
 *       The Eclipse Public License is available at
 *       http://www.eclipse.org/legal/epl-v10.html
 *
 *       The Apache License v2.0 is available at
 *       http://www.opensource.org/licenses/apache2.0.php
 *
 *  You may elect to redistribute this code under either of these licenses.
 */

package io.vertx.ext.mail;

import io.vertx.core.shareddata.LocalMap;
import io.vertx.test.core.VertxTestBase;
import org.junit.Test;

/**
 * @author <a href="http://tfox.org">Tim Fox</a>
 */
public class RefCountTest extends VertxTestBase {

  private LocalMap<String, Object> getLocalMap() {
    return vertx.sharedData().getLocalMap("__vertx.MailClient.pools");
  }

  @Test
  public void testNonShared() {
    LocalMap<String, Object> map = getLocalMap();
    MailConfig config = new MailConfig();
    MailClient client1 = MailClient.createNonShared(vertx, config);
    assertEquals(1, map.size());
    MailClient client2 = MailClient.createNonShared(vertx, config);
    assertEquals(2, map.size());
    MailClient client3 = MailClient.createNonShared(vertx, config);
    assertEquals(3, map.size());
    client1.close();
    assertEquals(2, map.size());
    client2.close();
    assertEquals(1, map.size());
    client3.close();
    assertWaitUntil(() -> map.size() == 0);
    assertWaitUntil(() -> getLocalMap().size() == 0);
    assertWaitUntil(() -> map != getLocalMap()); // Map has been closed
  }

  @Test
  public void testSharedDefault() throws Exception {
    LocalMap<String, Object> map = getLocalMap();
    MailConfig config = new MailConfig();
    MailClient client1 = MailClient.createShared(vertx, config);
    assertEquals(1, map.size());
    MailClient client2 = MailClient.createShared(vertx, config);
    assertEquals(1, map.size());
    MailClient client3 = MailClient.createShared(vertx, config);
    assertEquals(1, map.size());
    client1.close();
    assertEquals(1, map.size());
    client2.close();
    assertEquals(1, map.size());
    client3.close();
    assertEquals(0, map.size());
    assertNotSame(map, getLocalMap());
  }

  @Test
  public void testSharedNamed() throws Exception {
    LocalMap<String, Object> map = getLocalMap();
    MailConfig config = new MailConfig();
    MailClient client1 = MailClient.createShared(vertx, config, "ds1");
    assertEquals(1, map.size());
    MailClient client2 = MailClient.createShared(vertx, config, "ds1");
    assertEquals(1, map.size());
    MailClient client3 = MailClient.createShared(vertx, config, "ds1");
    assertEquals(1, map.size());

    MailClient client4 = MailClient.createShared(vertx, config, "ds2");
    assertEquals(2, map.size());
    MailClient client5 = MailClient.createShared(vertx, config, "ds2");
    assertEquals(2, map.size());
    MailClient client6 = MailClient.createShared(vertx, config, "ds2");
    assertEquals(2, map.size());

    client1.close();
    assertEquals(2, map.size());
    client2.close();
    assertEquals(2, map.size());
    client3.close();
    assertEquals(1, map.size());

    client4.close();
    assertEquals(1, map.size());
    client5.close();
    assertEquals(1, map.size());
    client6.close();
    assertEquals(0, map.size());
    assertNotSame(map, getLocalMap());
  }
}

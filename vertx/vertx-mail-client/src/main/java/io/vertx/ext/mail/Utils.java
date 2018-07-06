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

/**
 * a few utility methods that are used in MailAttachment and MailMessage
 */
package io.vertx.ext.mail;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import io.vertx.core.MultiMap;
import io.vertx.core.http.CaseInsensitiveHeaders;
import io.vertx.core.json.JsonArray;
import io.vertx.core.json.JsonObject;

/**
 * @author <a href="http://oss.lehmann.cx/">Alexander Lehmann</a>
 *
 */
class Utils {

  private Utils() {
  }

  static JsonObject multiMapToJson(final MultiMap headers) {
    JsonObject json = new JsonObject();
    for (String key : headers.names()) {
      json.put(key, headers.getAll(key));
    }
    return json;
  }

  static void putIfNotNull(final JsonObject json, final String key, final Object value) {
    if (value != null) {
      json.put(key, value);
    }
  }

  static MultiMap jsonToMultiMap(final JsonObject jsonHeaders) {
    MultiMap headers = new CaseInsensitiveHeaders();
    for (String key : jsonHeaders.getMap().keySet()) {
      headers.add(key, getKeyAsStringOrList(jsonHeaders, key));
    }
    return headers;
  }

  @SuppressWarnings("unchecked")
  static List<String> getKeyAsStringOrList(JsonObject json, String key) {
    Object value = json.getValue(key);
    if (value == null) {
      return null;
    } else {
      if (value instanceof String) {
        return asList((String) value);
      } else if (value instanceof JsonArray) {
        return (List<String>) ((JsonArray) value).getList();
      } else {
        throw new IllegalArgumentException("invalid attachment type");
      }
    }
  }

  static <T> List<T> asList(T element) {
    return Collections.singletonList(element);
  }

}

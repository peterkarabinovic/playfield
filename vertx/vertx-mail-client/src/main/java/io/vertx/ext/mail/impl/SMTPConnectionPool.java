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

package io.vertx.ext.mail.impl;

import io.vertx.core.AsyncResult;
import io.vertx.core.Future;
import io.vertx.core.Handler;
import io.vertx.core.Vertx;
import io.vertx.core.logging.Logger;
import io.vertx.core.logging.LoggerFactory;
import io.vertx.core.net.JksOptions;
import io.vertx.core.net.NetClient;
import io.vertx.core.net.NetClientOptions;
import io.vertx.ext.mail.MailConfig;
import io.vertx.ext.mail.StartTLSOptions;

import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.Queue;
import java.util.Set;

class SMTPConnectionPool implements ConnectionLifeCycleListener {

  private static final Logger log = LoggerFactory.getLogger(SMTPConnectionPool.class);

  private final int maxSockets;
  private final boolean keepAlive;
  private final Queue<Waiter> waiters = new ArrayDeque<>();
  private final Set<SMTPConnection> allConnections = new HashSet<>();
  private final NetClient netClient;
  private final MailConfig config;
  private final Vertx vertx;
  private String hostname;
  private boolean closed = false;
  private int connCount;

  private Handler<Void> closeFinishedHandler;

  SMTPConnectionPool(Vertx vertx, MailConfig config) {
    this.config = config;
    this.vertx = vertx;
    maxSockets = config.getMaxPoolSize();
    keepAlive = config.isKeepAlive();
    NetClientOptions netClientOptions = new NetClientOptions().setSsl(config.isSsl()).setTrustAll(config.isTrustAll());
    if ((config.isSsl() || config.getStarttls() != StartTLSOptions.DISABLED) && !config.isTrustAll()) {
      // we can use HTTPS verification, which matches the requirements for SMTPS
      netClientOptions.setHostnameVerificationAlgorithm("HTTPS");
    }
    if (config.getKeyStore() != null) {
      // assume that password could be null if the keystore doesn't use one
      netClientOptions.setTrustStoreOptions(new JksOptions().setPath(config.getKeyStore())
          .setPassword(config.getKeyStorePassword()));
    }
    netClient = vertx.createNetClient(netClientOptions);
  }

  void getConnection(String hostname, Handler<AsyncResult<SMTPConnection>> resultHandler) {
    log.debug("getConnection()");
    this.hostname = hostname;
    if (closed) {
      resultHandler.handle(Future.failedFuture("connection pool is closed"));
    } else {
      getConnection0(resultHandler);
    }
  }

  void close() {
    close(null);
  }

  synchronized void close(Handler<Void> finishedHandler) {
    if (closed) {
      throw new IllegalStateException("pool is already closed");
    } else {
      closed = true;
      closeFinishedHandler = finishedHandler;
      closeAllConnections();
    }
  }

  synchronized int connCount() {
    return connCount;
  }

  // Lifecycle methods

  // Called when the send operation has finished
  public synchronized void dataEnded(SMTPConnection conn) {
    checkReuseConnection(conn);
  }

  // Called if the connection is actually closed OR the connection attempt
  // failed - in the latter case conn will be null
  public synchronized void connectionClosed(SMTPConnection conn) {
    log.debug("connection closed, removing from pool");
    connCount--;
    if (conn != null) {
      allConnections.remove(conn);
    }
    Waiter waiter = waiters.poll();
    if (waiter != null) {
      // There's a waiter - so it can have a new connection
      log.debug("creating new connection for waiter");
      createNewConnection(waiter.handler);
    }
    if (closed && connCount == 0) {
      log.debug("all connections closed, closing NetClient");
      netClient.close();
      if (closeFinishedHandler != null) {
        closeFinishedHandler.handle(null);
      }
    }
  }

  // Private methods

  private synchronized void getConnection0(Handler<AsyncResult<SMTPConnection>> handler) {
    SMTPConnection idleConn = null;
    for (SMTPConnection conn : allConnections) {
      if (!conn.isBroken() && conn.isIdle()) {
        idleConn = conn;
        break;
      }
    }
    if (idleConn == null && connCount >= maxSockets) {
      // Wait in queue
      log.debug("waiting for a free socket");
      waiters.add(new Waiter(handler));
    } else {
      if (idleConn == null) {
        // Create a new connection
        log.debug("create a new connection");
        createNewConnection(handler);
      } else {
        if (idleConn.isClosed()) {
          log.warn("idle connection is closed already, this may cause a problem");
        }
        // if we have found a connection, run a RSET command, this checks if the connection
        // is really usable. If this fails, we create a new connection. we may run over the connection limit
        // since the close operation is not finished before we open the new connection, however it will be closed
        // shortly after
        log.debug("found idle connection, checking");
        final SMTPConnection conn = idleConn;
        conn.useConnection();
        conn.getContext().runOnContext(v -> {
          new SMTPReset(conn, result -> {
            if (result.succeeded()) {
              handler.handle(Future.succeededFuture(conn));
            } else {
              conn.setBroken();
              log.debug("using idle connection failed, create a new connection");
              createNewConnection(handler);
            }
          }).start();
        });
      }
    }
  }

  private synchronized void checkReuseConnection(SMTPConnection conn) {
    if (conn.isBroken()) {
      log.debug("connection is broken, closing");
      conn.close();
    } else {
      // if the pool is disabled, just close the connection
      if (!keepAlive || closed) {
        log.debug("connection pool is disabled or pool is already closed, immediately doing QUIT");
        conn.close();
      } else {
        log.debug("checking for waiting operations");
        Waiter waiter = waiters.poll();
        if (waiter != null) {
          log.debug("running one waiting operation");
          conn.useConnection();
          waiter.handler.handle(Future.succeededFuture(conn));
        } else {
          log.debug("keeping connection idle");
          conn.setIdle();
        }
      }
    }
  }

  private void closeAllConnections() {
    Set<SMTPConnection> copy;
    if (connCount > 0) {
      synchronized (this) {
        copy = new HashSet<>(allConnections);
        allConnections.clear();
      }
      // Close outside sync block to avoid deadlock
      for (SMTPConnection conn : copy) {
        if (conn.isIdle() || conn.isBroken()) {
          conn.close();
        } else {
          log.debug("closing connection after current send operation finishes");
          conn.setDoShutdown();
        }
      }
    } else {
      if (closeFinishedHandler != null) {
        closeFinishedHandler.handle(null);
      }
    }
  }

  private void createNewConnection(Handler<AsyncResult<SMTPConnection>> handler) {
    connCount++;
    log.debug("Connection count is " + connCount);
    createConnection(result -> {
      if (result.succeeded()) {
        allConnections.add(result.result());
      }
      handler.handle(result);
    });
  }

  private void createConnection(Handler<AsyncResult<SMTPConnection>> handler) {
    SMTPConnection conn = new SMTPConnection(vertx, netClient, this);
    new SMTPStarter(conn, config, hostname, result -> {
      if (result.succeeded()) {
        handler.handle(Future.succeededFuture(conn));
      } else {
        handler.handle(Future.failedFuture(result.cause()));
      }
    }).start();
  }

  private static class Waiter {
    private final Handler<AsyncResult<SMTPConnection>> handler;

    private Waiter(Handler<AsyncResult<SMTPConnection>> handler) {
      this.handler = handler;
    }
  }
}

package com.crosshub.common;

import org.springframework.dao.CannotAcquireLockException;
import org.hibernate.exception.LockAcquisitionException;

import java.sql.SQLException;
import java.util.concurrent.Callable;

/**
 * SQLite 写库重试：Java 与 Python 共用 crosshub.db，并发时可能 SQLITE_BUSY。
 */
public final class SqliteRetry {
    private static final int MAX_ATTEMPTS = 5;
    private static final long BASE_BACKOFF_MS = 50L;

    private SqliteRetry() {
    }

    public static boolean isLockConflict(Throwable throwable) {
        Throwable current = throwable;
        while (current != null) {
            if (current instanceof CannotAcquireLockException || current instanceof LockAcquisitionException) {
                return true;
            }
            if (current instanceof SQLException sqlEx) {
                if (sqlEx.getErrorCode() == 5) {
                    return true;
                }
            }
            String message = current.getMessage();
            if (message != null && message.contains("SQLITE_BUSY")) {
                return true;
            }
            current = current.getCause();
        }
        return false;
    }

    public static void runWithRetry(Runnable action) {
        callWithRetry(() -> {
            action.run();
            return null;
        });
    }

    public static <T> T callWithRetry(Callable<T> action) {
        RuntimeException last = null;
        for (int attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
            try {
                return action.call();
            } catch (RuntimeException ex) {
                last = ex;
                if (!isLockConflict(ex) || attempt >= MAX_ATTEMPTS - 1) {
                    throw ex;
                }
                sleepQuiet(BASE_BACKOFF_MS * (attempt + 1));
            } catch (Exception ex) {
                if (ex instanceof InterruptedException interrupted) {
                    Thread.currentThread().interrupt();
                    throw new IllegalStateException("数据库写入被中断", interrupted);
                }
                RuntimeException wrapped = new IllegalStateException(ex);
                last = wrapped;
                if (!isLockConflict(ex) || attempt >= MAX_ATTEMPTS - 1) {
                    throw wrapped;
                }
                sleepQuiet(BASE_BACKOFF_MS * (attempt + 1));
            }
        }
        if (last != null) {
            throw last;
        }
        throw new IllegalStateException("数据库写入失败");
    }

    private static void sleepQuiet(long millis) {
        try {
            Thread.sleep(millis);
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("数据库写入重试被中断", ex);
        }
    }
}

/*
 * Hardware Watchdog Timer (WDT) Module — ESP32 Home Control
 * Prevents system lockup by automatically rebooting the ESP32 if the main
 * execution loop freezes or deadlocks for more than 15 seconds.
 */

#ifndef WATCHDOG_H
#define WATCHDOG_H

#include <esp_task_wdt.h>

#define WDT_TIMEOUT_SECONDS 15  // 15 seconds hardware watchdog timeout

/*
 * Initialize the hardware task watchdog timer
 */
inline void initWDT() {
#if defined(ESP_IDF_VERSION_MAJOR) && (ESP_IDF_VERSION_MAJOR >= 5)
    esp_task_wdt_config_t wdt_config = {
        .timeout_ms = WDT_TIMEOUT_SECONDS * 1000,
        .idle_core_mask = (1 << portNUM_PROCESSORS) - 1,
        .trigger_panic = true
    };
    esp_task_wdt_init(&wdt_config);
    esp_task_wdt_add(NULL); // Add current (loopTask) thread
#else
    esp_task_wdt_init(WDT_TIMEOUT_SECONDS, true);
    esp_task_wdt_add(NULL);
#endif

#if ENABLE_SERIAL_DEBUG
    Serial.println("✓ Hardware Task Watchdog (WDT) initialized (15s timeout)");
#endif
}

/*
 * Feed the watchdog to prevent reset. Call this regularly in loop().
 */
inline void feedWDT() {
    esp_task_wdt_reset();
}

#endif // WATCHDOG_H

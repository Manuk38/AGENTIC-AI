#include <stdint.h>
/* REQ: LLR-1 */
uint16_t crc16_compute(const uint8_t* data, uint32_t len, uint16_t poly, uint16_t init) {
    uint16_t crc = init;
    for (uint32_t i = 0; i < len; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t j = 0U; j < 8U; ++j) {
            if ((crc & 0x8000U) != 0U) {
                crc = (uint16_t)((crc << 1) ^ poly);
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

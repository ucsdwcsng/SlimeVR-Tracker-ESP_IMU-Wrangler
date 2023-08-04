/*
    SlimeVR Code is placed under the MIT license
    Copyright (c) 2021 Eiren Rain

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
*/
// ================================================
// See docs for configuration options and examples:
// https://docs.slimevr.dev/firmware/configuring-project.html#2-configuring-definesh
// ================================================

// Set parameters of IMU and board used
#define IMU IMU_BNO085
#define SECOND_IMU IMU
#define BOARD BOARD_WROOM32
#define IMU_ROTATION DEG_270
#define SECOND_IMU_ROTATION DEG_270
#define USE_SPI_IMU true

#define MAX_IMU_COUNT 2

// Axis mapping example
/*
#include "sensors/axisremap.h"
#define BMI160_QMC_REMAP AXIS_REMAP_BUILD(AXIS_REMAP_USE_Y, AXIS_REMAP_USE_XN, AXIS_REMAP_USE_Z, \
                                       AXIS_REMAP_USE_YN, AXIS_REMAP_USE_X, AXIS_REMAP_USE_Z)

IMU_DESC_ENTRY(IMU_BMP160, PRIMARY_IMU_ADDRESS_ONE, IMU_ROTATION, PIN_IMU_SCL, PIN_IMU_SDA, BMI160_QMC_REMAP) \
*/

#ifndef IMU_DESC_LIST
#define IMU_DESC_LIST \
        IMU_DESC_ENTRY(IMU,        PRIMARY_IMU_ADDRESS_ONE,   IMU_ROTATION,        PIN_IMU_SCL, PIN_IMU_SDA, PIN_IMU_INT  )
#endif

#define MAX_IMU_COUNT 2

// Axis mapping example
/*
#include "sensors/axisremap.h"
#define BMI160_QMC_REMAP AXIS_REMAP_BUILD(AXIS_REMAP_USE_Y, AXIS_REMAP_USE_XN, AXIS_REMAP_USE_Z, \
                                       AXIS_REMAP_USE_YN, AXIS_REMAP_USE_X, AXIS_REMAP_USE_Z)

IMU_DESC_ENTRY(IMU_BMP160, PRIMARY_IMU_ADDRESS_ONE, IMU_ROTATION, PIN_IMU_SCL, PIN_IMU_SDA, BMI160_QMC_REMAP) \
*/

#ifndef IMU_DESC_LIST
#define IMU_DESC_LIST \
        IMU_DESC_ENTRY(IMU,        PRIMARY_IMU_ADDRESS_ONE,   IMU_ROTATION,        PIN_IMU_SCL, PIN_IMU_SDA, PIN_IMU_INT  ) \
        IMU_DESC_ENTRY(SECOND_IMU, SECONDARY_IMU_ADDRESS_TWO, SECOND_IMU_ROTATION, PIN_IMU_SCL, PIN_IMU_SDA, PIN_IMU_INT_2)
#endif

// Battery monitoring options (comment to disable):
//   BAT_EXTERNAL for ADC pin, 
//   BAT_INTERNAL for internal - can detect only low battery, 
//   BAT_MCP3021 for external ADC connected over I2C
#define BATTERY_MONITOR BAT_EXTERNAL

#define PIN_IMU_SDA 21
#define PIN_IMU_SCL 22
#define PIN_IMU_INT 35
#define PIN_IMU_INT_2 25
#define PIN_BATTERY_LEVEL 36
#define LED_PIN 13
#define LED_INVERTED false

#define PIN_IMU_CS 17
#define PIN_IMU_WAK 16
#define PIN_IMU_RST 5
#define PIN_SPI_CLK 18
#define PIN_SPI_MISO 19
#define PIN_SPI_MOSI 23

// uint32_t spiPortSpeed = 100*1000;
#define SPI_PORT_SPD 100000
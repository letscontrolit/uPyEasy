# uPyEasy

uPyEasy allows you to turn an ESP and STM32 modules into a multifunction sensor and switch device. Configuration of uPyEasy is web-based. This means that after you've got the firmware loaded, the set up of the device can be done with a web browser. New sensors can be added on-the-fly as well as the configuration for your home automation solution.

Build status: **BETA**

Introduction and wiki: https://www.letscontrolit.com/wiki/index.php/uPyEasy#Introduction

This is the development branch of uPyEasy. All new untested features go into this branch. Fixes from stable branches will also be merged in this one.

Check here to learn how to use this branch and help us improving uPyEasy: http://www.letscontrolit.com/wiki/index.php/uPyEasy#Source_code_development


## Binary releases

New binary release: https://github.com/letscontrolit/uPyEasy/releases

The releases are named something like `upyeasy_v[Release]_[Date]_test_[Hardware]_[Size].bin`.

Depending on your needs, we release different types of files:

Firmware name                                    | Hardware                | Included plugins            |
-------------------------------------------------|-------------------------|-----------------------------|
upyeasy_v020_20180127_test_esp32_2048.bin        | ESP32 with 2Mb flash    | Beta                        |
upyeasy_v020_20180127_test_stm32-pybv3_1024.dfu  | STM32 with 1Mb flash    | Beta                        |

## Usage

- Download a binary from [Releases](https://github.com/letscontrolit/uPyEasy/releases).
- Use [`esptool`](https://github.com/espressif/esptool) to erase the flash.

  ```bash
  $ sudo python esptool.py --port /dev/ttyUSB0 -c esp32 erase_flash
  ```
- Now flash the binary.

  ```bash
  $ sudo python esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 upyeasy_v53_20180106_test_esp32_2048.bin
  ```
- Connect over serial to the board with a tool like `minicom`, `picocom`, `screen` or Putty to get the debug output.

For further details please check this [guide](https://www.letscontrolit.com/forum/viewtopic.php?f=22&t=3906).

## More info

Details and discussion are on the uPyEasy forum: https://www.letscontrolit.com/forum/viewtopic.php?f=20&t=3577

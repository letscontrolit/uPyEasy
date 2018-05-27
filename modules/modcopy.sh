cd unix
cp ../../../micropython/micropython-async/aswitch.py .
cp ../../../micropython/micropython-async/asyn.py .
cp ../../../micropython/micropython-lib/copy/copy.py .
cp ../../../micropython/micropython/drivers/dht/dht.py .
cp ../../../micropython/micropython/drivers/onewire/ds18x20.py .
cp ../../../micropython/micropython-lib/ffilib/ffilib.py .
cp -fR ../../../micropython/micropython-lib/json/json .
cp ../../../micropython/micropython/drivers/display/lcd160cr.py .
cp ../../../micropython/micropython-lib/logging/logging.py .
cp ../../../micropython/micropython-lib/operator/operator.py .
cp -fR ../../../micropython/picoweb/picoweb .
cp ../../../micropython/micropython-lib/pkg_resources/pkg_resources.py .
cp ../../../micropython/micropython-lib/re-pcre/re.py .
cp ../../../micropython/micropython/drivers/sdcard/sdcard.py .
cp ../../../micropython/micropython/drivers/display/ssd1306.py .
cp ../../../micropython/micropython-lib/types/types.py .
cp ../../../micropython/micropython-lib/uaiohttpclient/uaiohttpclient.py .
cp -fR ../../../micropython/modbus/uModbus .
mv -f uModbus umodbus
cp ../../../micropython/micropython/tools/upip.py .
cp ../../../micropython/micropython/tools/upip_utarfile.py .
cp ../../../micropython/micropython-lib/upysh/upysh.py .
cp ../../../micropython/micropython-lib/urequests/urequests.py .
cp -fR ../../../micropython/micropython-lib/urllib .
cp -fR ../../../micropython/utemplate/utemplate .
cp ../../../micropython/utemplate/utemplate_util.py .
mkdir collections 
cd collections
cp ../../../../micropython/micropython-lib/collections.defaultdict/collections/defaultdict.py .
cp  ../../../../micropython/micropython-lib/collections.deque/collections/deque.py .
cp  ../../../../micropython/micropython-lib/collections/collections/__init__.py .
cd ..
mkdir uasyncio
cd uasyncio
cp ../../../../micropython/micropython-lib/uasyncio.core/uasyncio/core.py .
cp ../../../../micropython/micropython-lib/uasyncio/uasyncio/__init__.py .
cp ../../../../micropython/micropython-lib/uasyncio.queues/uasyncio/queues.py .
cp ../../../../micropython/micropython-lib/uasyncio.synchro/uasyncio/synchro.py .
cd ..
mkdir umqtt
cd umqtt
cp ../../../../micropython/micropython-lib/umqtt.robust/umqtt/robust.py .
cp ../../../../micropython/micropython-lib/umqtt.simple/umqtt/simple.py .
cd ../..

cd esp32
cp ../../../micropython/micropython/drivers/dht/dht.py  .
cp ../../../micropython/micropython/drivers/onewire/ds18x20.py .
cp ../../../micropython/micropython/drivers/onewire/onewire.py .
ln -sf  ../unix/aswitch.py
ln -sf  ../unix/asyn.py
ln -sf  ../unix/copy.py
ln -sf  ../unix/collections
ln -sf  ../unix/console_sink.py
ln -sf  ../unix/filedb.py
ln -sf  ../unix/json
ln -sf  ../unix/lcd160cr.py
ln -sf  ../unix/log_config.py
ln -sf  ../unix/logging.py
ln -sf  ../unix/log_sink.py
ln -sf  ../unix/operator.py
ln -sf  ../unix/picoweb
ln -sf  ../unix/pkg_resources.py
ln -sf  ../unix/re.py
ln -sf  ../unix/sdcard.py
ln -sf  ../unix/ssd1306.py
ln -sf  ../unix/syslog_sink.py
ln -sf  ../unix/types.py
ln -sf  ../unix/uaiohttpclient.py
ln -sf  ../unix/uasyncio
ln -sf  ../unix/ulog.py
ln -sf  ../unix/umodbus
ln -sf  ../unix/umqtt
ln -sf  ../unix/upip.py
ln -sf  ../unix/upip_utarfile.py
ln -sf  ../unix/upysh.py
ln -sf  ../unix/urequests.py
ln -sf  ../unix/urllib
ln -sf  ../unix/usyslog.py
ln -sf  ../unix/utemplate
ln -sf  ../unix/utemplate_util.py
cd ..

cd stm32
cp ../../../micropython/micropython/drivers/dht/dht.py  .
cp ../../../micropython/micropython/drivers/onewire/ds18x20.py .
cp ../../../micropython/micropython/drivers/onewire/onewire.py .
ln -sf  ../unix/aswitch.py
ln -sf  ../unix/asyn.py
ln -sf  ../unix/copy.py
ln -sf  ../unix/collections
ln -sf  ../unix/console_sink.py
ln -sf  ../unix/filedb.py
ln -sf  ../unix/json
ln -sf  ../unix/lcd160cr.py
ln -sf  ../unix/log_config.py
ln -sf  ../unix/logging.py
ln -sf  ../unix/log_sink.py
ln -sf  ../unix/operator.py
ln -sf  ../unix/picoweb
ln -sf  ../unix/pkg_resources.py
ln -sf  ../unix/re.py
ln -sf  ../unix/sdcard.py
ln -sf  ../unix/ssd1306.py
ln -sf  ../unix/syslog_sink.py
ln -sf  ../unix/types.py
ln -sf  ../unix/uaiohttpclient.py
ln -sf  ../unix/uasyncio
ln -sf  ../unix/ulog.py
ln -sf  ../unix/umodbus
ln -sf  ../unix/umqtt
ln -sf  ../unix/upip.py
ln -sf  ../unix/upip_utarfile.py
ln -sf  ../unix/upysh.py
ln -sf  ../unix/urequests.py
ln -sf  ../unix/urllib
ln -sf  ../unix/usyslog.py
ln -sf  ../unix/utemplate
ln -sf  ../unix/utemplate_util.py

cd ..

chmod -fR 777 *


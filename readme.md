# MIOTY sensor tools

---

## miotysensor\.py

Konsolendienstprogramm zum Konfigurieren des Sensors und zum Übertragen von Daten

    miotysensor [--port PORT] {init,send} ...

#### optionen

##### --port

>Serial Port
>
>unterstütyte Aufnahmetypen:
>
>- COM\<index\>
>   - z.B. COM0
>- \<index\>
>   - z.B. 0
>- /dev/\<name\>
>   - z.B. /dev/ttyACM0
>
> Default Linux: /dev/ttyACM1
> Default Windows: COM6

### miotysensor init

    miotysensor init <networkKey> [--txPower [TXPOWER]] [--miotyMode [MIOTYMODE]] [--miotyProfile [MIOTYPROFILE]]

Führt die folgenden Aktionen aus:

- SATP_STACK_SELECT_STACK <= E_STACK_ID_MIOTY
- SATP_STACK_SET <= E_STACK_PARAM_ID_MIOTY_NWKKEY <= \<networkKey\>
- SATP_STACK_GET <= E_STACK_PARAM_ID_MIOTY_EUI64
- SATP_STACK_GET <= E_STACK_PARAM_ID_MIOTY_SHORT_ADDR

#### optionen

Um den Wert festlegen: --option Value
Um den Wert zu erhalten: --option

### miotysensor send

    miotysensor send <--data [DATA]> [-t TIMEOUT] [-p PERIOD] [-ld] [-sd]
    miotysensor send <--data [DATA]> [--timeout TIMEOUT] [--period PERIOD] [--save_data]

Sendet daten und wartet auf Downlink-Daten

#### optionen

##### --data

> daten, die gesendet werden
> muss als Floge von Bytes im Hexadezimalformat ohne Leerzeichen eingegeben werde
>
> z.B. a1b2c3
>
> bei angabe ohne Argument werden Daten aus der Datei "data" gelesen

##### --timeout (-t)

> zeit in Sekunden, während der Downlinllk-Daten erwartet werden

##### --period (-p)

> zeit in Sekunden zwischen den RX-Pufferprüfungen

##### --save_data (-sd)

> die empfangenen Daten in einer Datei "data" speichen

---

## satp_serial\.py

Implementierung des Kommunikation mit dem Sensor + nutzliche Function int2hex4list

### satp_serial\.MiotySerialSATP

enthält Functionen zum Senden und Empfangen von Daten

Objekterstellung:

`satp = MiotySerialSATP(baudarte=115200, port='COM6')`

#### satp_serial\.MiotySerialSATP\.send_data()

> - args
>   - api_id
>   - command_id
>   - [parameter] ***Liste mit Zahlen (0x00 - 0xff)***
>
> - return None

#### satp_serial\.MiotySerialSATP\.check_serial()

> - return
>   - True, wenn sich Daten im Eingabepuffer befinden
>   - False, wenn der Eingabepuffer leer ist

#### satp_serial\.MiotySerialSATP\.read_data()

> - return [Message1, Message2, \.\.\.]
>   - Message = (STACK_ID, API_ID, Confirmation, [data])

### satp_serial\.int2hex4list()

wandelt eine Liste von Dezimalzahlen in eine Liste von hexadezimalzahlen um

> - args
>   - int_list
>   - without_0x ***whenn True, "0x" wird nicht vor Zahlen hinzyugefügt***
>
> - return Liste mit hex Zhalen

---

## mioty_mqtt_script\.py

Wartet auf eine Nachricht von MQTT und sendet RSSI über den Downlink-Kanal zurück\.

### Einstellungen

Am Anfang des Scripts kann man mehrere Parameter konfigurieren

- DEBUG - Aktiviert oder deaktiviert die Konsolenausgabe
- MQTT_IP - MQTT Broker IP Adresse
- MQTT_PORT - MQTT Broker port

### Abhängigkeiten

- **paho-mqtt**
`pip install paho-mqtt`

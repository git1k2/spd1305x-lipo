import time
import sys
import vxi11

from datetime import datetime

instrument = vxi11.Instrument("192.168.50.237")


def teardown():
    # Turn off output
    print('Turning off channel 1.')
    instrument.ask("OUTP CH1,OFF")
    instrument.close()
    sys.exit(0)


# The SPD1305X does not seem to have implemented the *OPC? or WAI commands, so we slow down here
def send_command(command=None):
    output = instrument.ask(command)
    time.sleep(0.5)
    return output


def main():
    # Lipo max voltage
    volt = 4.2

    # Lipo mA rating
    lipo_mah = 850

    # Lipo C rating
    C = 1

    charge_current_amp = (C * lipo_mah) / 1000
    stop_amp = C / 10

    print(send_command("*IDN?"))

    # Set volt, current and output on
    send_command(f"CH1:voltage {volt}")
    send_command(f"CH1:current {charge_current_amp}")
    send_command("OUTP CH1,ON")

    print(f"Charging Lipo, will automatically stop at {stop_amp:.3f} amp. Press ctrl-c to stop.")
    print("datetime,volt,ampere")

    try:
        meas_curr = float(0)
        while meas_curr >= stop_amp:
            now = datetime.now()
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

            meas_volt = float(send_command("meas:volt?"))
            meas_curr = float(send_command("meas:curr?"))

            print(f"{dt_string},{meas_volt:.3f},{meas_curr:.3f}")
            time.sleep(5)
    except KeyboardInterrupt:
        teardown()

    print('Finished charging.')
    teardown()


if __name__ == '__main__':
    main()
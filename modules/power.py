# File: modules/power.py

from adafruit_ads1x15.ads1015 import ADS1015
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
from pijuice import PiJuice
import threading
import time
from modules.logger import logger, LogType


class PowerMonitor:
    def __init__(self):
        # Initialize I2C and ADC
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS1015(self.i2c)

        # Configure voltage divider ratio
        self.voltage_divider_ratio = 2

        # Create analog inputs
        self.panel_voltage = AnalogIn(self.ads, ADS1015.P0)
        self.panel_current = AnalogIn(self.ads, ADS1015.P1)

        # Thresholds
        self.low_voltage_threshold = 4.7

        # Start monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()

    def get_panel_power_status(self):
        """Get voltage and current readings for LED panels"""
        voltage = self.panel_voltage.voltage * self.voltage_divider_ratio
        current = self.calculate_current(self.panel_current.voltage)

        return {
            "voltage": round(voltage, 2),
            "current": round(current, 2),
            "power": round(voltage * current, 2),
            "status": "normal" if voltage > self.low_voltage_threshold else "low",
        }

    def calculate_current(self, voltage):
        """Convert ACS712 voltage to current"""
        return (voltage - 2.5) * 10  # For 20A sensor

    def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.running:
            status = self.get_panel_power_status()
            if status["status"] == "low":
                logger.log(LogType.POWER, "low_voltage_warning", status)
            time.sleep(5)  # Check every 5 seconds


class PowerManager:
    def __init__(self):
        # Initialize PiJuice
        self.pijuice = PiJuice(1, 0x14)
        self.power_monitor = PowerMonitor()

        # Initialize power sources status
        self.power_sources = {"mains": False, "battery_1": False, "battery_2": False}

        # Start power management thread
        self.running = True
        self.power_thread = threading.Thread(target=self._power_management_loop)
        self.power_thread.start()

    def get_status(self):
        """Get comprehensive power status"""
        panel_power = self.power_monitor.get_panel_power_status()
        battery_status = self.pijuice.status.GetChargeLevel()

        return {
            "panel_power": panel_power,
            "battery_level": battery_status["data"],
            "battery_status": self.pijuice.status.GetStatus()["data"],
            "power_sources": self.power_sources,
        }

    def _power_management_loop(self):
        """Main power management loop"""
        while self.running:
            try:
                # Check battery status
                battery_charge = self.pijuice.status.GetChargeLevel()["data"]
                if battery_charge < 20:
                    logger.log(
                        LogType.POWER, "low_battery_warning", {"level": battery_charge}
                    )

                # Check power input status
                power_status = self.pijuice.status.GetStatus()["data"]
                if power_status["powerInput"] != "PRESENT":
                    logger.log(LogType.POWER, "power_input_missing")

            except Exception as e:
                logger.log(LogType.ERROR, "power_check_failed", {"error": str(e)})

            time.sleep(30)  # Check every 30 seconds

    def cleanup(self):
        """Clean up resources"""
        self.running = False
        self.power_thread.join()
        self.power_monitor.running = False
        self.power_monitor.monitor_thread.join()

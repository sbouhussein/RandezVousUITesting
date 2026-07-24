import os
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "1"
os.environ["GRPC_POLL_STRATEGY"] = "poll"
import subprocess

class DeviceHelper:
    def __init__(self, driver):
        self.driver = driver

    def set_simulator_location(self, lat=41.282778, lon=-157.829444):
        print("Forcing location via Appium Driver...")
        try:
            udid = self.driver.capabilities.get('udid')
            print(f"Targeting active simulator UDID: {udid}")

            self.driver.set_location(lat, lon, 0)

            if udid:
                subprocess.run(["xcrun", "simctl", "location", udid, "clear"])
                subprocess.run(["xcrun", "simctl", "location", udid, "set", f"{lat},{lon}"])
                print("Location successfully hard-set via simctl.")

        except Exception as e:
            print(f"Failed to set location: {e}")
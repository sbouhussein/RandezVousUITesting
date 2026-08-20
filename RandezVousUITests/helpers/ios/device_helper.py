import os
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "1"
os.environ["GRPC_POLL_STRATEGY"] = "poll"
# Silences gRPC's C-core INFO logging (e.g. "FD from fork parent still in poll
# list"), which fires when subprocess.run() forks a process that has
# firebase_admin/gRPC already initialized.
os.environ["GRPC_VERBOSITY"] = "ERROR"
import subprocess

RV_BUNDLE_ID = os.getenv("RV_BUNDLE_ID", "sbouhussein.github.io-rvsite.RandezVous")

class DeviceHelper:
    def __init__(self, driver):
        self.driver = driver

    def fast_reset_to_signed_out(self, bundle_id=RV_BUNDLE_ID):
        # Firebase's session lives in the Keychain, so clearing app data alone won't sign the user out.
        print("Fast-resetting app to signed-out state...")
        self.driver.execute_script('mobile: clearKeychains')
        # Must terminate before reactivating, or Firebase Auth's in-memory session survives the Keychain clear.
        self.driver.terminate_app(bundle_id)
        self.driver.activate_app(bundle_id)
        print("App relaunched in pre-auth state.")

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
import os
import subprocess

# gRPC (via firebase_admin) logs "FD from fork parent still in poll list" whenever
# subprocess.run() forks; these must be set before gRPC initializes.
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "1"
os.environ["GRPC_POLL_STRATEGY"] = "poll"
os.environ["GRPC_VERBOSITY"] = "ERROR"

from helpers.common.device_helper_base import DeviceHelperBase

RV_BUNDLE_ID = os.getenv("RV_BUNDLE_ID", "sbouhussein.github.io-rvsite.RandezVous")
# In range of test-automation-quest's location activity.
DEFAULT_SIM_LOCATION = (37.6255291, -77.5144256)


class DeviceHelper(DeviceHelperBase):
    default_app_id = RV_BUNDLE_ID

    def fast_reset_to_signed_out(self, bundle_id=RV_BUNDLE_ID):
        # Firebase keeps its session in the Keychain.
        print("Fast-resetting app to signed-out state...")
        self.driver.execute_script('mobile: clearKeychains')
        # Terminate first, or the in-memory session survives.
        self.driver.terminate_app(bundle_id)
        # Not activate_app: it drops the session's launch args (App Check token, intro skip).
        process_arguments = self.driver.capabilities.get('processArguments') or {}
        self.driver.execute_script('mobile: launchApp', {
            'bundleId': bundle_id,
            'arguments': process_arguments.get('args', []),
            'environment': process_arguments.get('env', {}),
        })
        print("App relaunched in pre-auth state.")

    def set_simulator_location(self, lat=DEFAULT_SIM_LOCATION[0], lon=DEFAULT_SIM_LOCATION[1]):
        print("Forcing location via Appium Driver...")
        try:
            udid = self.driver.capabilities.get('udid')
            print(f"Targeting active simulator UDID: {udid}")

            self.driver.set_location(lat, lon, 0)

            if udid:
                # No "clear" first: it applies asynchronously and can land after this "set".
                subprocess.run(["xcrun", "simctl", "location", udid, "set", f"{lat},{lon}"])
                print("Location successfully hard-set via simctl.")

        except Exception as e:
            print(f"Failed to set location: {e}")
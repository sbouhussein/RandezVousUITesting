#!/usr/bin/env bash
# Installs everything android_chrome_driver needs: Android command-line tools, the
# SDK (platform-tools/adb, emulator, a Google Play system image), and an AVD.
# Idempotent -- safe to re-run; anything already installed is skipped.
# Called from setup.sh. Large download (several GB): set SKIP_ANDROID=1 to skip it.

set -u

cd "$(dirname "$0")/.." || exit 1

API_LEVEL=34                  # Android 14 -- matches ANDROID_PLATFORM_VERSION=14 in .env.example
AVD_DEVICE="pixel_8"
# Standard Android Studio location on macOS; conftest.py defaults ANDROID_HOME here too.
SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}}"

# Must match the host CPU or the emulator can't use hardware acceleration.
case "$(uname -m)" in
    arm64|aarch64) ABI="arm64-v8a" ;;
    *)             ABI="x86_64" ;;
esac
# google_apis_playstore ships a real Chrome (plain AOSP images don't) -- see README.
SYSTEM_IMAGE="system-images;android-${API_LEVEL};google_apis_playstore;${ABI}"

# AVD name comes from .env (ANDROID_DEVICE_NAME) so the emulator we create is the one tests ask for.
AVD_NAME=$(grep -m1 '^ANDROID_DEVICE_NAME=' .env 2>/dev/null | cut -d= -f2- | tr -d '"')
AVD_NAME="${AVD_NAME:-Pixel_8_API_34}"

echo "Android setup: SDK at $SDK_ROOT, image $SYSTEM_IMAGE, AVD '$AVD_NAME'"

# 1. Java (sdkmanager/avdmanager need a JDK)
if ! java -version >/dev/null 2>&1; then
    if command -v brew >/dev/null 2>&1; then
        echo "Installing a JDK via Homebrew..."
        brew install --cask temurin@17 || { echo "⚠️  Could not install a JDK -- install one manually."; exit 1; }
    else
        echo "⚠️  No JDK found and Homebrew isn't installed -- install a JDK (17+), then re-run ./setup.sh."
        exit 1
    fi
fi

# 2. Android command-line tools (sdkmanager / avdmanager)
find_tool() {
    command -v "$1" 2>/dev/null || { [ -x "$SDK_ROOT/cmdline-tools/latest/bin/$1" ] && echo "$SDK_ROOT/cmdline-tools/latest/bin/$1"; }
}
SDKMANAGER=$(find_tool sdkmanager)
if [ -z "$SDKMANAGER" ]; then
    if command -v brew >/dev/null 2>&1; then
        echo "Installing Android command-line tools via Homebrew..."
        brew install --cask android-commandlinetools || { echo "⚠️  Homebrew install failed."; exit 1; }
        SDKMANAGER=$(find_tool sdkmanager)
    fi
fi
if [ -z "$SDKMANAGER" ]; then
    echo "⚠️  sdkmanager not found. Install Homebrew (https://brew.sh) and re-run ./setup.sh, or install Android Studio."
    exit 1
fi

# avdmanager derives its SDK root from where *it* is installed (ignoring ANDROID_HOME), so
# Homebrew's copy can't see system images in $SDK_ROOT. Install cmdline-tools into the SDK
# itself and use that copy for everything from here on.
mkdir -p "$SDK_ROOT"
if [ ! -x "$SDK_ROOT/cmdline-tools/latest/bin/avdmanager" ]; then
    echo "Installing cmdline-tools into $SDK_ROOT..."
    yes | "$SDKMANAGER" --sdk_root="$SDK_ROOT" --licenses >/dev/null 2>&1
    "$SDKMANAGER" --sdk_root="$SDK_ROOT" "cmdline-tools;latest" \
        || { echo "⚠️  Could not install cmdline-tools into the SDK."; exit 1; }
fi
SDKMANAGER="$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager"
AVDMANAGER="$SDK_ROOT/cmdline-tools/latest/bin/avdmanager"

# 3. SDK components: adb, emulator, platform, Google Play system image
mkdir -p "$SDK_ROOT"
if [ ! -x "$SDK_ROOT/platform-tools/adb" ] || [ ! -x "$SDK_ROOT/emulator/emulator" ] \
   || [ ! -d "$SDK_ROOT/system-images/android-${API_LEVEL}/google_apis_playstore/${ABI}" ]; then
    echo "Accepting Android SDK licenses and installing SDK components (large download)..."
    yes | "$SDKMANAGER" --sdk_root="$SDK_ROOT" --licenses >/dev/null 2>&1
    "$SDKMANAGER" --sdk_root="$SDK_ROOT" \
        "platform-tools" "emulator" "platforms;android-${API_LEVEL}" "$SYSTEM_IMAGE" \
        || { echo "⚠️  sdkmanager failed to install SDK components."; exit 1; }
else
    echo "Android SDK components already installed."
fi

# 4. The AVD itself
export ANDROID_HOME="$SDK_ROOT" ANDROID_SDK_ROOT="$SDK_ROOT"
if "$AVDMANAGER" list avd -c 2>/dev/null | grep -qx "$AVD_NAME"; then
    echo "AVD '$AVD_NAME' already exists."
else
    echo "Creating AVD '$AVD_NAME'..."
    echo "no" | "$AVDMANAGER" create avd -n "$AVD_NAME" -k "$SYSTEM_IMAGE" -d "$AVD_DEVICE" \
        || { echo "⚠️  Could not create AVD '$AVD_NAME'."; exit 1; }
fi

# Software-rendered GPU: the default (hw.gpu.enabled=no on freshly created AVDs) leaves Chrome
# spamming "GpuControl.CreateCommandBuffer" failures on Intel Macs. Idempotent.
AVD_CFG="${ANDROID_AVD_HOME:-$HOME/.android/avd}/${AVD_NAME}.avd/config.ini"
if [ -f "$AVD_CFG" ]; then
    sed -i '' -e 's/^hw.gpu.enabled=.*/hw.gpu.enabled=yes/' -e 's/^hw.gpu.mode=.*/hw.gpu.mode=swiftshader_indirect/' "$AVD_CFG"
    grep -q '^hw.gpu.mode=' "$AVD_CFG" || echo 'hw.gpu.mode=swiftshader_indirect' >> "$AVD_CFG"
fi

# 5. Make sure an existing .env has the Android keys (setup.sh only copies .env.example when .env is missing)
if [ -f ".env" ] && [ -f ".env.example" ]; then
    for key in ANDROID_DEVICE_NAME ANDROID_PLATFORM_VERSION RV_ANDROID_PACKAGE; do
        if ! grep -q "^${key}=" .env; then
            grep -m1 "^${key}=" .env.example >> .env && echo "Added ${key} to .env."
        fi
    done
fi

echo "Android setup done. Boot the emulator before running Android tests:"
echo "  $SDK_ROOT/emulator/emulator -avd $AVD_NAME -no-snapshot -no-audio"

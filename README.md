# Home Assistant Integration: Davey Lifeguard

![image](ressources/logo.png)

## Project Summary:
This project is a custom integration for Home Assistant, designed to leverage and control data from a Davey Lifeguard device, a connected pool management system.

This is an unofficial integration, developed by an independent developer, with the aim of centralizing pool-related data and actions within the Home Assistant home automation interface.

## Main Features of the Integration:

### 🔍 Real-time Sensor Monitoring:
* Water pH
* ORP (Oxidation-Reduction Potential)
* Water Temperature
* Salinity
* Chlorine Production Rate
* VSD Pump Speed

![image](ressources/sensors.png)

### ✅ Equipment Status and Diagnostics:
* Connection status of various probes (temperature, pH, ORP, salt)
* Device status
* Error detection (flow, ORP, pH, salt)

![image](ressources/diagnostic.png)

### 🛠️ Equipment Control (via Home Assistant entities):
* Activation/deactivation of **operating modes**: manual, boost
* Selection of the **pH setpoint**
* Selection of the **ORP setpoint**
* Adjustment of the **VSD pump speed**

![image](ressources/control.png)

## 🛠️ Technical Architecture:
* Utilizes a `DataUpdateCoordinator` to centralize API requests and synchronize entities.
* Communication with the Davey cloud API (no local access).
* Authentication via token / refresh token, stored in `config_entry`.
* Grouped and optimized API requests using `asyncio.gather`.
* Use of `translations` to manage names based on the user's language.
* Organization of entities by type: `sensor`, `binary_sensor`, `switch`, `select`.
* Multilingual support (fr, en).

## 🌍 Target Audience:
* Home Assistant users who own a **Davey Lifeguard system**.
* Home automation administrators looking to centralize their pool management.
* Developers interested in improving the integration or contributing.

## 🚧 Project Status:
* 🧪 First functional version
* 💡 Under development
* ✅ Already successfully tested on a real Davey Lifeguard system

## 📝 Technical Specifications & Remarks:
* Requires Home Assistant ≥ 2023.x
* **UI-first** integration: no YAML configuration is necessary.
* The integration relies on the official API used by the Davey mobile application.
* ⚠️ **No local access currently possible**: depends on the Davey cloud.

## 💾 Installation:

As this is a custom integration, it needs to be added to your Home Assistant instance manually. Here's how:

1.  **Access your Home Assistant configuration directory.** This is the directory where your `configuration.yaml` file is located.

2.  **Create a new directory named `custom_components`** within your configuration directory if it doesn't already exist.

3.  **Inside the `custom_components` directory, create another new directory named `davey_lifeguard`.**

4.  **Download the files for this integration** from the repository (once it is public) and place them inside the `custom_components/davey_lifeguard/` directory. The file structure should look like this:
    ```
    <your_config_directory>/
    └── custom_components/
        └── davey_lifeguard/
            ├── __init__.py
            ├── config_flow.py
            ├── sensor.py
            ├── switch.py
            └── ... (other integration files)
    ```

5.  **Restart your Home Assistant server.**

6.  **Configure the integration:**
    * After the restart, go to "Settings" > "Devices & Services".
    * Click the "+ Add Integration" button in the bottom right corner.
    * Search for "Davey Lifeguard" and click on it.
    * Follow the on-screen instructions to enter your Davey Lifeguard account credentials (likely the email and password used for the Davey mobile app).

## 🤝 Possible Contributions:
* Optimization of Python code.
* Addition of an advanced configuration interface.
* Addition of new sensors or entities.
* Additional translations (es, de, etc.).
* Preparation for HACS (structure + release).

## Important Disclaimer Regarding This Initial Release:

Given that this is my very first Home Assistant integration, it is crucial to emphasize that **improvements are certainly necessary**.

Consequently, it is highly likely that **bugs may be present** in this initial version. Your patience and feedback will be invaluable in identifying and correcting these potential issues.

Furthermore, please note that **not all described features are yet available** in this first iteration. Development is ongoing, and new capabilities will be added progressively as needed/suggested.

Thank you for your understanding and leniency during this initial development phase. Your testing and constructive comments will be of great help in evolving this integration.
# 5Genesis Portal

## Requirements

 - [Python 3.7.x](https://www.python.org) (see requirements.txt for a detailed view of required packages)
 - [ELCM](https://github.com/5genesis/ELCM) Version 2.4.0 (22/12/2020)
 - [Dispatcher](https://github.com/5genesis/Dispatcher) Commit 2c05c28e812fb712f73b51ab78c1d190c0f50d0e (04/01/2021)

### Optional integrations:

 - [Grafana](https://grafana.com/) (tested with version 5.4)

## Deployment

### Pre-requisites

The Portal requires connectivity with running instances of the Dispatcher (user authentication and NS onboarding)
and ELCM (facility registry and experiment execution).

> Additional dependencies may be needed depending on your environment. For example, older Windows version may require
certain Visual C++ redistributables to be installed, and the following packages are known to be required on many Ubuntu
distributions: `gcc python3.7 python3.7-venv python3.7-dev`. Fixes for specific issues are usually easy to find on 
Internet.

### Installation procedure

This repository includes two sets of scripts for use on Linux (`.sh`) and Windows (`.ps1`) machines. In general
these scripts should be able to perform most of the actions required for instantiating the Portal, however, depending
on the deployment environment some actions may fail or require additional tweaking. The contents of the scripts can
be used as a guide for manual installation, and a description of the actions performed by the scripts is included below
for use as reference.

1. Ensure that Python 3.7.x is installed. For environments with multiple Python versions note the correct alias.
   > For example, older Ubuntu distributions refer to Python 2.x by default when invoking `python`, and reference 
   > Python 3.7 as `python3` or `python3.7`. Use the `--version` parameter to check the version number.
2. Clone the repository to a known folder
3. Run `install.sh <python_alias>` or `install.ps1 <python_alias>` (depending on your OS). The script will:
  - Display the Python version in use (ensure that this is 3.7.x)
  - Create a [Python virtual environment](https://virtualenv.pypa.io/en/stable/) for exclusive use of the Portal.
  - Install the required Python packages (using [pip](https://pypi.org/project/pip/))
  > Most issues occur during this step, since it is highly dependent on the environment. In case of error, note the 
  > name of the package that could not be installed, the error message and your OS distribution. Performing an Internet 
  > search with this information usually yields a solution. Once solved you may re-run the script (delete the `venv` 
  > folder that was created by the script if necessary) until all packages are correctly installed.
  - Initialize the Portal database
4. Run `start.sh` or `start.ps1` (depending on your OS). This will create an empty configuration file (`config.yml`).
   If necessary, press ctrl+c (or your OS equivalent) in order to close the server.
5. Ensure that the `config.yml` is available in the Portal folder and customize its contents. The Portal needs
   information about how to connect with the Dispatcher and ELCM components (more information about all the possible 
   configuration values can be found below).
6. Customize the `.flaskenv` file. Replace the `__REPLACEWITHSECRETKEY__` label with a random string (for more info 
   see [this answer](https://stackoverflow.com/a/22463969).)

### Starting the Portal

Once configured, the Portal can be started by running `start.sh <port_number>` or `start.ps1 <port_number>`. If not
specified, the server will listen on port 5000. In order to stop the server, press ctrl+c (or your OS equivalent) in
the terminal where the server is running.

### Minimal integration tests

In order to test that the connections with the Dispatcher and ELCM are working properly, perform the following actions:

1. Check the log messages (in the log file or console output) that appear when starting the Portal. The Portal tries to
   retrieve the facility configuration from the ELCM when starting, and displays the number of registered test cases,
   UEs, scenarios and slice descriptors. If these correspond to the ones configured in the ELCM, then the connection
   is working properly.
   > If you do not see any messages, check the `Logging` section of the configuration file (`config.yml`). Ensure that
   > the levels are set to `DEBUG` or `INFO`
1. Open the Portal using a web browser. 
2. Register a new user (top right, `Register` tab). If no errors are reported after pressing the `Register` button at 
   the bottom then the connection with the Dispatcher is working properly.
   > Note that newly registered users are not "active", and cannot log in to the Portal until their registration has 
   > been validated by the platform administrator(s). For information about the user activation procedure refer to the 
   > Dispatcher (Authenticator) documentation.

## Configuration

The Portal instance can be configured by editing the `config.yml` file.

- Logging:
    - Folder: Folder where the log files will be saved. Defaults to `./Logs`.
    - AppLevel: Minimum message level to display in the terminal output (one of `CRITICAL`, `ERROR`, `WARNING`,
      `INFO`, `DEBUG`). Defaults to `INFO`.
    - LogLevel: Minimum message level to write in the log files. Defaults to `DEBUG`.
- Dispatcher:
    - Host: Location of the machine where the Dispatcher is running (localhost by default).
    - Port: Port where the Dispatcher is listening for connections (5001 by default).
    - TokenExpiry: Time (in seconds) to consider that an authentication token has expired, should be slightly shorter
    (30/60 seconds) than the real expiration time configured on the Dispatcher.
- ELCM:
    - Host: Location of the machine where the ELCM is running (localhost by default).
    - Port: Port where the ELCM is listening for connections (5001 by default).
- Grafana URL: Base URL of Grafana Dashboard to display Execution results.
- Platform: Platform name. Will be displayed in the Portal and will identify the platform during distributed
  experiments.
- Description: Short textual description of the platform. Will be displayed in the Portal.
- PlatformDescriptionPage: HTML file that contains a more detailed description of the platform. The HTML written in
  this file will be inserted in the 'Info' page of the Portal. Defaults to `platform.html`. This file is included in
  this repository, and can be customized or used as reference.
- EastWest: Configuration for distributed experiments.
    - Enabled: Boolean value indicating if the East/West interfaces are available. Defaults to `False`.
    - Remotes: Dictionary containing the connection configuration for each remote platform's Portal, with each key
      containing 'Host' and 'Port' values in the same format as in the `ELCM` section. Defaults to an empty
      dictionary (`{}`).

#### Portal notices

It's possible to display system-wide notices in the Portal by creating a file named `notices.yml` in the root folder
of the Portal. The format of this file shall be as follows:

```yaml
Notices:
  - Example notice 1
  - Example notice 2
```
The list may include as many notices as necessary.

## Authors

* **Gonzalo Chica Morales**
* **[Bruno Garcia Garcia](https://github.com/NaniteBased)**

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   > <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

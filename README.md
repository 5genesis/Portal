# 5Genesis Portal

## Requirements

 - [Python 3.7.x](https://www.python.org)
 - [Optional] [Grafana](https://grafana.com/) (tested on version 5.4)
 - [Optional] [Grafana reporter](https://github.com/IzakMarais/reporter) 
 (tested on version 2.1.0, commit 41b38a0, see ELCM readme for more information)
 
## Interoperability with other components

The following information specifies the version that most closely match the expected behavior when this package interacts
with others developed internally in 5 Genesis (i.e. the version that was available during the development and that was 
used while testing this component). It's possible that most (or all) features work with some previous versions, and most
probably there will be no issues when using more recent versions.

 - [ELCM](https://gitlab.fokus.fraunhofer.de/5genesis/elcm) Version 1.1.0 (02/10/2019)

## Installing (development)
> A video detailing the deployment procedure of the Portal (and ELCM) can be seen [in BSCW](https://bscw.fokus.fraunhofer.de/bscw/bscw.cgi/d3208170/Coordinationlayer_call20190422.mp4)

> It is recommended, but not required, to run the Portal in a [Python virtual environment](https://virtualenv.pypa.io/en/stable/).
> If you are not using virtual environments, skip steps 3 and 4.

1. Clone the repository to a known folder, e.g. in `c:\5gPortal` 
2. Enter the folder
```bash
cd c:/5gPortal
```
3. Create a new Python virtualenv:
```bash
pip install virtualenv
virtualenv venv
```
4. Activate the virtual environment:
- For Windows:
```powershell
venv\Scripts\Activate.bat
```
- For Linux:
```bash
source venv/bin/activate
```
5. Install Python dependencies:
```bash
pip install -r requirements.txt
```

6. Upgrade (initialize) the database to the latest version:
> The portal is configured for creating an SQLite database automatically (`app.db`) if no other database backend is configured.
> If the deployment will use a different backend it might be wise to set it before running this command. See the Configuration section for more information. 

```bash
flask db upgrade
```

7. Start the development server:
```bash
flask run
```
The app will generate a default configuration file (`config.yml`) and start listening for requests on port 5000.
Refer to the Configuration section for information about customizing the default values.
Press `Control+C` to stop the development server.

## Deployment (production)

This repository includes a `Vagrantfile` that can be used to automatically deploy a virtual machine
that includes the Portal instance (running under `Gunicorn`) and an `nginx`. This file can also be 
used as an example of how to deploy the Portal on an existing Linux machine or using Docker containers,
since most of the commands executed are valid in many other environments.

In order to deploy using `Vagrant`:

1. Install [Vagrant](https://www.vagrantup.com/downloads.html) and [Virtualbox](https://www.virtualbox.org/wiki/Downloads).
2. Navigate to the Portal folder.
3. Create the virtual machine:
```bash
vagrant up
```  

This will create and start a virtual machine named `5genesis-portal` and bind port 80 of the host machine to the Portal instance.
> If you cannot bind the Portal to port 80 you can use a different port by setting other value in the Vagrantfile (`config.vm.network "forwarded_port"`).

The default deployment does not use https. In order to enable it you will need to provide the necessary certificates and customize the nginx configuration. This repository includes an example configuration file (`Vagrant/nginx_ssl.conf`) that can be used as a base.

## Configuration

The Portal instance can be configured by setting environment variables and by editing the `config.yml` file. The Portal uses `python-dotenv`, so it's possible to save the environment variables in the `.flaskenv` file.

The environment variables that can be set are:
* SECRET_KEY: **Set this value to a RANDOM string** (the default value is not random enough). See [this answer](https://stackoverflow.com/a/22463969).
* FLASK_RUN_PORT: Port where the portal will listen (5000 by default)
* SQLALCHEMY_DATABASE_URI: Database instance that will be used by the Portal. Depending on the backend it's possible that additional Python packages will need to be installed, for example, MySQL requires `pymysql`. See [Dialects](https://docs.sqlalchemy.org/en/latest/dialects/index.html)
* UPLOAD_FOLDER: Folder path where the uploaded files will be stored.

> Currently unused:
> * MAIL_SERVER: Mail server location (localhost by default)
> * MAIL_PORT: Mail server port (8025 by default)

The values that can be configured on `config.yml` are:
* Dispatcher:
    * Host: Location of the machine where the Dispatcher is running (localhost by default).
    * Port: Port where the Dispatcher is listening for connections (5001 by default).
    * TokenExpiry: Time (in seconds) to consider that an authentication token has expired, should be slightly shorter
    (30/60 seconds) than the real expiration time on the Dispatcher.
* ELCM:
    * Host: Location of the machine where the ELCM is running (localhost by default).
    * Port: Port where the ELCM is listening for connections (5001 by default).
> Direct communication with the ELCM is still needed
* Platform: Platform name/location.
* TestCases: List of TestCases supported by the platform.
* UEs: Dictionary that contains information about the UEs available in the platform. Each element key defines the unique
ID of the UE, while the value contains a dictionary with extra data about the UE (currently the operating system).
> The list of TestCases and UEs selected for each experiment will be sent to the Dispatcher (and ELCM) on every 
execution request. The ELCM uses these values in order to customize the campaign execution (via the Composer and the 
Facility Registry).
* Slices: List of available Network Slices.
> This information is not currently used by the ELCM (as of 3/6/2019)
* Grafana URL: Base URL of Grafana Dashboard to display Execution results.
* Description: Description of the platform.
* PlatformDescriptionPage: HTML file that contains the description of the platform. The HTML written in this file 
will be inserted in the 'Info' page of the Portal 
* Logging: Parameters for storing application logs.

### Portal Notices

It's possible to display system-wide notices in the Portal by including a file named `notices.yml` in the root folder.
The format of this file is as follows:

```yaml
Notices:
  - Example notice 1
  - Example notice 2
```
The list may include as many notices as necessary.

### REST API

Information about the current REST API of the Portal (and ELCM) can be seen [in BSCW](https://bscw.fokus.fraunhofer.de/bscw/bscw.cgi/d3228781/OpenAPIv1.docx).

## Authors

* **Gonzalo Chica Morales**
* **Bruno Garcia Garcia**

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



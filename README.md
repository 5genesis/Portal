# 5Genesis Portal

## Requirements

[Python 3.7.x](https://www.python.org)

## Installing (development)
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
> The Dispatcher does not currently exist as a separate entity, so this information refers to the ELCM during Release A.
* Platform: Platform name/location.
* TestCases: List of TestCases supported by the platform.
* UEs: Dictionary that contains information about the UEs available in the platform. Each element key defines the unique
ID of the UE, while the value contains a dictionary with extra data about the UE (currently the operating system).
> The list of TestCases and UEs selected for each experiment will be sent to the Dispatcher (and ELCM) on every 
execution request. The ELCM uses these values in order to customize the campaign execution (via the Composer and the 
Facility Registry). This functionality is no yet included in the ELCM (as of 22/03/2019).
* Slices: List of available Network Slices.
* Grafana URL: Base URL of Grafana Dashboard to display Execution results.
* Description: Description of the platform.
* Logging: Parameters for storing application logs.
## Authors

* **Gonzalo Chica Morales**
* **Bruno Garcia Garcia**

## License

TBD


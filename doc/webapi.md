# GIMX API v1
---
Route prefix: **gimx/api/v1**

All responses are in JSON format.

# /status
Supported: **GET**
### GET
Gives info about gimx process status. Response can have three values:

* **status_code** (int): 
	- 0: No gimx process exists;
	- 1: Gimx is initialized but not fully working yet.
	- 2: if is running and working normally;
* **messages** (string): GIMX stdout. (Exists only if parameter **get_output**="true")
* **error_messages** (string): GIMX stderr. (Exists only if parameter **get_output**="true")

# /configfile
Supported: **GET**, **POST**.
### GET
Gets a list of all configuration files. Response have only one value:

* conf_files (string-list): A list of strings (can be empty) with each xml configuration file.

### POST
Uploads a configuration file.
#### Parameters
|  **Name** | **Required** |                              **Description**                             | Default value | **Example** |
|:---------:|:------------:|:------------------------------------------------------------------------:|---------------|:-----------:|
| file      | required     | The file                                                                 |               |             |
| overwrite | optional     | {true,false} - if true, the file can overwrite an existing one  | false         | true        |

#### Response
* **return_code** (int): returns 0 on success, otherwise:
	- 1: No file specified
	- 2: File name not allowed
	- 3: File already exists
* **message** (string): If an error occurs, an error message is given here. (Exists only if **return_code** is not 0).

# /start
Supported: **POST**

### POST
Starts/Initializes GIMX process by calling [gimx command line binary](http://gimx.fr/wiki/index.php?title=Command_line) using specified parameters.
On normal execution, this changes the gimx state from 0 (OFF) to 1 (Initializing). If successfully initialized, then it changes to state 2 (Running).
See [**/status**](#status) for more details. Note that normally, after making this request, gimx is not fully running yet.
You have two options to check GIMX status:
* Polling requests to **/status** until GIMX is fully running or goes OFF (an error occurs) or
* Register for GIMX changed status events (see [/streamStatus](streamStatus)).

#### Parameters
Has only one parameter:

* **options** (string): the options used on the gimx command line binary (see [http://gimx.fr/wiki/index.php?title=Command_line]). Example: "options"="-c file_name -p /dev/ttyUSB0"

#### Response
* **return_code** (int): returns 0 on success, otherwise:
	- 1: GIMX is already initialized!
	- 2: Unable to start GIMX! (And we don't known why)
	- 3: Missing parameter "options"
* **message** (string): If an error occurs, an error message is given here. (Exists only if **return_code** is not 0).

# /stop
Supported: **GET**, **POST**

Both **GET** and **POST** requests do the same procedure: Stops GIMX if it is running. Currently this works by simply making a _shift+ESC_ event.

Response only returns one value:

* **return_code** (int): returns 0 on success.

# /version
Supported: **GET**

### GET
Returns the current version of this Web Server and the version of the installed GIMX.
#### Response
* **gimxWebAPI-version** (string): Version of the Web Server.
* **gimx-version** (string): Installed GIMX version (Obtained via `gimx --version`).

# /update
Supported: **POST**

### POST
Updates the GIMX Web API using specified installer (see parameters).
#### Parameters
* **file** (file): must be a '.tar.gz' file that contains a 'install.sh' script. You can build this file by running `make installer.tar.gz` in the GIMX-WebAPI installed directory.

#### Response
* **return_code** (int): 0 if no error occurred.


# /streamStatus
Applications can register to receive event notifications when GIMX status is changed. Responses events are returned with mime-type=text/event-stream. The only data returned is an integer representing the GIMX status (see [**/status**](#status)).



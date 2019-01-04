# GIMX API v1
---
Route prefix: **gimx/api/v1**

# /status
Supported: **GET**
### GET
Gives info about gimx process status. Response can have three values:

* **status_code** (int): 
	- 0: No gimx process exists;
	- 1: if is running and working normally;
	- 2: Gimx is initialized but not fully working yet.
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
* **return_code** (int): returns 0 if on sucess, otherwise:
	- 1: No file specified
	- 2: File name not allowed
	- 3: File already exists
* **message** (string): If an error occurs, an error message is given here. (Exists only if **return_code** is not 0).

# /start
Supported: **POST**

### POST
Starts/Initializes Gimx process by calling [gimx command line binary](http://gimx.fr/wiki/index.php?title=Command_line) using specified parameters.
On normal execution, this changes the gimx state from 0 (OFF) to 2 (Initializing). If successfully initialized, then it changes to state 1 (Running).
See [Section /status](#/status) for more details. Note that normally, after making this request, gimx is not fully running yet. 
You should make pooling **/status** requests until GIMX is fully running or completly goes OFF (an error occurs).

#### Parameters
Has only one parameter:

* **options** (string): the options used on the gimx command line binary (see [http://gimx.fr/wiki/index.php?title=Command_line]). Example: "options"="-c file_name -p /dev/ttyUSB0"

#### Response
* **return_code** (int): returns 0 on success, otherwise:
	- 1: GIMX is already initialized!
	- 2: Unable to start GIMX! (And we don't known why)
	- 4: Missing parameter "options"
* **message** (string): If an error occurs, an error message is given here. (Exists only if **return_code** is not 0).

# /stop
Supported: **GET**, **POST**

Both **GET** and **POST** requests do the same procedure: Stops Gimx if it is running. Currently this works by simply making a _shift+ESC_ event.

Response only returns one value:

* **return_code** (int): returns 0 on success or gimx is already OFF.

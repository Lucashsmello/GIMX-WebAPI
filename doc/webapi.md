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
* **messages** (string): GIMX stdout.
* **error_messages** (string): GIMX stderr.

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

#### Return
* **return_code** (int): returns 0 if operation was successful, otherwise:
	- 1: No file specified
	- 2: File name not allowed
	- 3: File already exists
* **message** (string): If an error occurs, an error message is given here. (Exists only if **return_code** is 0).
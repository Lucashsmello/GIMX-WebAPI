# GIMX API v1
Route preffix: **gimx/api/v1**
## /status
Supported: **GET**
> ### GET
Gives info about gimx process status. Response can have three values:

>
* **status_code** (int): **0** if no gimx process exists; **1** if is initialized but not fully running yet; **2** if is running normally.
* **messages** (string): GIMX stdout.
* **error_messages** (string): GIMX stderr.

## /configfile

Supported: **GET**, **POST**.
> ### GET
Gets a list of all configuration files. Response have only one value:

>
* conf_files (string-list): A list of strings (can be empty) with each xml configuration file.

> ### POST
Uploads a configuration file.
> #### Parameters
|  **Name** | **Required** |                              **Description**                             | Default value | **Example** |
|:---------:|:------------:|:------------------------------------------------------------------------:|---------------|:-----------:|
| file      | required     | The file                                                                 |               |             |
| overwrite | optional     | {true,false} - if true, the file can overwrite an existing one  | false         | true        |
# filelist-api

### Introduction

This is a simple python script which uses a headless browser to update your public IP in FL profile.

### How to build

```shell
docker build -t myregistry.example.com/filelist-api-whitelist:1
```

## How to run

### docker-compose.yml

1. Create secrets:

``` shell
echo "myUsername" | docker secret create my_username -
echo "myPassword" | docker secret create my_password -
```

2. docker-compose.yml

```
version: '3.2'
services:
    changedetection:
      image: myregistry.example.com/filelist-api-whitelist:1 .
      container_name: filelist-api
      environment:
        - FL_USERNAME=/run/secrets/my_username
        - FL_PASSWORD=/run/secrets/my_password
        - CHECK_INTERVAL=10 #in minutes I suggest putting more than 5 minutes.
        - DRIVER=chrome # container_name of browserless port is always 3000
      restart: unless-stopped

    browserless-chrome:
      container_name: chrome
      image: browserless/chrome
      restart: unless-stopped
```

### Quick and dirty (NOT RECOMMENDED)

There is a reson why have to do this so plese don't keep username/passwords in plain text.

But if you know what you are doing... here you go.

Compose file
```
version: '3.2'
services:
    changedetection:
      image: myregistry.example.com/filelist-api-whitelist:1 .
      container_name: filelist-api
      environment:
        - FL_USERNAME=YOUR_USER
        - FL_PASSWORD=YOUR_PASSWORD
        - CHECK_INTERVAL=10 # in minutes I suggest putting more than 5 minutes.
        - DRIVER=chrome # container_name of browserless port is always 3000
      restart: unless-stopped

    browserless-chrome:
      container_name: chrome
      image: browserless/chrome
      restart: unless-stopped
```

## Contributing

Feel free to contribute or report bugs.

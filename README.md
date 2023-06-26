# ETL pipelines


### NOTES and CRITICAL POINTS: 
- the default chromium coming along with ```pyppeteer ``` does not correctly support file downloads in 
```headless``` now, ao I need to install newest ```google-chrome``` version in my docker. Note 
```buildoutcfg
    browser = await launch(
        # headless=False,
        executablePath=config.chrome_path,
        # downloadsPath=config.temp_store_path,
        args=[
            '--no-sandbox',  # Disable the sandbox for security reasons
            '--headless=new'  # note the headless here and uses new!
            # f"""--user-data-dir="{config.user_data_dir}" """
        ],
    )
```
 using ```'--headless=new'``` as one of ```args```. This seems to be a known problem with files downloads 
in ```pyppeteer```

- this replacement of default ```chromium``` with latest ```google-chrome``` as above also solves the problem of 
  ```timeout``` when running dockerised code using ```pyppeteer```
  
- Airflow docker container used in this ETL comes with the historical files download -- however persisting in a docker image is
not a very good idea, I would not do it in PROD. I would prefer either use NFS (which does not come w/o some issues regarding
providing users from within dockers to access to NFS mounts) or consider using redis (in its own container, restricted 
to access only from withing ETL's own docker network) for persisting the data -- I started implementation 
of the second approach but cancelled it as ```redis``` may not be in your current stack and NFS in principle is ok.

- Source code for the project is installed inside Airflow docker container, also can be accessed via
```buildoutcfg
git clone https://github.com/VDV80/dvol_etl.git
```
- [Dash server with visualisation at localhost:8081](localhost:8081) should totally not be Airflow container, but in a 
  standalone docker also included into docker-compose 
  (since it needs to be on the same docker network as postgress with loaded data).
  This current set up is just to simplify the build a bit.

# Installation
The source ia currently available on github, so can be installed 
```buildoutcfg
git clone https://github.com/VDV80/dvol_etl.git
cd dvol_etl
python setup.py install
```
but it is already in the airflow docker image specified in the [Dockerfile](./gme_etl/Dockerfile).
NOTE that configs availabe for non-contenerised installation would need to be changed, as well some infastructure around it 
(eg historical data dump needs to be aquired, postrgres launched etc)



# Design and Aritecture

Each ETL pipeline (module in ```data_collector``` project) is supposed to be deployed in its own 
[docker container](./gme_etl/Dockerfile) build from [Ariflow's own docker container](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
-- note that the latter one is a simplified version for demo purposes mostly. 
This would not be ideal solution for PROD (at the very least that would imply running multiple instances of Ariflow in their own containers), 

I would prefer the Airflow to be run on the host as a single non-dockerise instance and run each individual ETL in its individual 
container, but as I am delivering the solution in most isolated manner, the Airflow itself is running on docker, and to my knowledge there is 
no easy way toprovide it access either to host's docker demon, or to raise one in airflow own docker for 
```airflow``` user to run the containers for ETLs.

# Tests
Only simple unit test for now -- as in [here](./tests).

Ideally should also have integration, performance and regression/backward compatibility test.

# Formatting and PEP8, type checks
Please use [Black](https://pypi.org/project/black/) to ensure PEP* compliance.

Please use and [Pylint](https://pypi.org/project/pylint/) for type checks.
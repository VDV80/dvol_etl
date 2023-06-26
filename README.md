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
  
- Airflow docker container used in this ETL comes with the historical files download in ```~/Downloads```-- however persisting this dump in a docker image is
not a very good idea, I would not do it in PROD. I would prefer either to use NFS (which does not come w/o some issues regarding
providing users from within dockers to access NFS mounts) or to use redis (in its own container, restricted 
to access only from withing ETL's own docker network); I started implementation 
of the second approach but cancelled it as ```redis``` may not be in your current stack and NFS in principle is ok.

- Source code for the project is installed (actually just cpoied, I had dependancies issues preventing proper install) inside Airflow docker container in ```~```
- , the code also can be accessed via
```buildoutcfg
git clone https://github.com/VDV80/dvol_etl.git
```
- [Dash server with visualisation at localhost:8081](localhost:8081) should totally not be in Airflow container, but in a 
  standalone docker also included into docker-compose 
  (since it needs to be on the same docker network as postgress with loaded data).
  This current set up is just to simplify the build a bit.

# Installation
The source ia currently available on github, so can be installed 
```buildoutcfg
git clone https://github.com/VDV80/dvol_etl.git
cd dvol_etl
python setup.py install # note the installation fails
```
but it is already in the airflow docker image specified in the [Dockerfile](./Dockerfile).
NOTE1 that [config.py](./gme_etl/config.py) for non-containerised installation would need to be changed, as well some infrastructure around it 
(eg historical data dump needs to be aquired, postrgres launched etc).
NOTE2 that ```python setup.py install``` does not work because of some versions(?) conflicts, hence silly 
```buildoutcfg
RUN pip install pandas pyppeteer redis plotly dash sqlalchemy==1.4.48 psycopg2-binary
```
which should not be there, als ```sys.path``` had to be appended in the code in imports section, which is really a bad parctice, but at least safe for
dockerised code.



# Design and Architecture

Each ETL pipeline (module in ```data_collector``` project) is deployed in its own 
[docker container](./Dockerfile) build from [Ariflow's own docker container](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
-- note that the latter one is a simplified version for demo purposes mostly. 
This would not be an ideal solution for prod (at the very least that would imply running multiple instances of Airflow in their own containers)...

I would prefer the Airflow to be run on the host as a single non-dockerised instance and run each individual ETL in its individual 
container, but as I am delivering the solution in most isolated manner, the Airflow itself is currently running on docker, and to my knowledge there is 
no easy way to provide it with access to either to host's docker demon, or to raise one in airflow's own docker for 
```airflow``` user (also it is possible to map sockets from host to docker, but it also runs  into that airflow user can not use this mapping).

# Tests
Only simple unit test for now -- as in [here](./gme_etl/tests).

Ideally should also have integration, performance and regression/backward compatibility test.

# Formatting and PEP8, type checks
Please use [Black](https://pypi.org/project/black/) to ensure PEP* compliance.

Please use and [Pylint](https://pypi.org/project/pylint/) for type checks.

NOTE --removed extras in setup.py when attempting to fix the conflicts preventing normal setup (now have to butcher the code by appending 
```sys.path``` which at least is safe for docker container)

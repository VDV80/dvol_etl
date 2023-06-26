# ETL pipelines


### NOTES and CRITICAL POINTS: 
- the default chromium that comes along with ```pyppeteer ``` does not correctly support file downloads in 
```headless``` now. Therefore, I need to install the newest ```google-chrome``` version in my docker. Please
note the folwing code snippet:  
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
I am using ```'--headless=new'``` as one of ```args```. This issue with file downloads is a known problem
in ```pyppeteer```

- this replacement of default ```chromium``` with latest ```google-chrome``` as above also solves the problem of 
  ```timeout``` when running dockerised code using ```pyppeteer```
  
- The Airflow Docker container used in this ETL comes with historical files downloaded to ```~/Downloads```. However, persisting this dump in a Docker image is not recommended for production. Instead, I would prefer to use NFS (which may have some issues regarding user access from within Docker containers) or use Redis in its own container, restricted to be accessed only from within the ETL's Docker network. I started implementing the second approach but canceled it as ```redis``` may not be part of your current stack, and using NFS is generally acceptable.

- The source code for the project is installed (actually just copied) inside the Airflow Docker container at ```~```.
 You can also access the code via the following command:
```buildoutcfg
git clone https://github.com/VDV80/dvol_etl.git
```
- The [Dash server with visualisation at localhost:8081](localhost:8081) sshould not be included in the Airflow container. It should be a standalone Docker container included in the Docker Compose configuration, as it needs to be on the same Docker network as Postgres with the loaded data. The current setup is just for simplifying the build process.

# Installation
The source code is currently available on GitHub, so you can install it using the following commands:
```buildoutcfg
git clone https://github.com/VDV80/dvol_etl.git
cd dvol_etl
python setup.py install # note the installation fails
```
However, the source code is already included in the Airflow Docker image specified in the  [Dockerfile](./Dockerfile).
 Note that if you want to perform a non-containerized installation, you would need to make changes to [config.py](./gme_etl/config.py) and other related infrastructure (e.g., acquiring historical data dump, launching Postgres, etc.). Also, please be aware that  ```python setup.py install``` may not work due to conflicts with certain versions. As a temporary workaround, the following packages were installed using the following command (which is not ideal): 
```buildoutcfg
RUN pip install pandas pyppeteer redis plotly dash sqlalchemy==1.4.48 psycopg2-binary
```
Additionally, ```sys.path``` had to be appended in the code's imports section, which is considered bad practice. However, it is at least safe for Dockerized code.



# Design and Architecture

Each ETL pipeline (module in ```data_collector``` project) is deployed in its own 
[docker container](./Dockerfile) build from [Ariflow's own docker container](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).
Please note that the latter one is a simplified version primarily intended for demo purposes.
This approach would not be an ideal solution for production, as it would require running multiple instances of Airflow in their own containers.

Ideally, I would prefer to run Airflow on the host as a single non-dockerized instance and have each individual ETL run in its own container. However, since I am delivering the solution in the most isolated manner, the Airflow itself is currently running in a Docker container. To my knowledge, there is no easy way to provide it with access to the host's Docker daemon or to set up a Docker daemon within Airflow's own Docker environment for the airflow user. Although it is possible to map sockets from the host to the Docker container, it presents the challenge that the airflow user cannot use this mapping.

# Tests
Currently, only simple unit tests are available, as shown [here](./gme_etl/tests).

Ideally, the testing suite should also include integration, performance, and regression/backward compatibility tests.

# Formatting and PEP8, type checks
Please use [Black](https://pypi.org/project/black/) to ensure PEP* compliance.

Please use and [Pylint](https://pypi.org/project/pylint/) for type checks.

NOTE --removed extras in setup.py when attempting to fix the conflicts preventing normal setup (now have to butcher the code by appending 
```sys.path``` which at least is safe for docker container)

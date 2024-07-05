# Text_Guru_Website

This is a small flask application that takes the whatsapp chat export as data to analyze the sentiments of the conversation as well as give some interesting highlight.In future want to add more complex models to do an accurate emotional and relationship index of the conversations


## Demo & Screenshots

Home Screen
![App Screenshot](https://i.imgur.com/v7fj3WK.png)

User needs to export whatsapp chat and upload it.

Result Screen
![App Screenshot](https://i.imgur.com/6zZ2RDp.png)

Result and Insights are seen on this screen.



## Installation

Deploy my project in Cloud using Docker

```bash
Build Docker Image
docker build -t python-docker . 

Run docker container from image
docker container run -dit -p 443:443 python-docker

Delete all image,container and volumes
docker system prune -a --volumes
```

Run locally

```bash
Conda create a virtual environment
conda create -n myenv python=3.9

Activate conda environment
conda activate myenv

Install requirements packages
pip install -r requirements.txt 

Run app.py
python app.py
```

## Roadmap

- Add more complex sentiment models and make the outputs more meaningfull about personality traits and the type of person.

- Add more integrations with SQL database to give the personality traits from multiple conversation for a profile.

- Add sign in and profile pages and also add a social integration.


## License

MIT License
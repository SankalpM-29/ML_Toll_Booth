# ML_Toll_Booth


## Run Locally

1. After installing packages run 
```bash
uvicorn main:app --reload 
```

2. To test apis, visit the route /docs in your browser 

## Api Calls

| Route | description | body |
|:---:|:---:|:---:|
|/add_user|new users can register into the database|tag_id, number, plate|
|/send_message|send message to a user based on the tag id|tag_id|

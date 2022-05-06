import json
import os
import uvicorn
import requests
import cv2 
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
from object_detection.utils import config_util
from PIL import Image
from google.cloud import vision
import io
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './translation-322819-fd44443f9785.json'

configs = config_util.get_configs_from_pipeline_file("./ANPR_centernet_resnet50_model/pipeline.config")
detection_model = model_builder.build(model_config=configs['model'], is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join("./ANPR_centernet_resnet50_model/checkpoint", 'ckpt-0')).expect_partial()

@tf.function
def detect_fn(image):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections

category_index = label_map_util.create_category_index_from_labelmap("./label_map.pbtxt")

app = FastAPI()


@app.post("/get_plate")
async def get_data(request: Request):
    form = await request.form()
    upload_file = form["imageFile"]  # starlette.datastructures.UploadFile - not used here, but just for illustrative purposes
    filename = form["imageFile"].filename  # str
    contents = await form["imageFile"].read()  # bytes
    with open('image.jpg', 'wb') as f:
        f.write(contents)
    IMAGE_PATH = 'image.jpg'

    img = cv2.imread(IMAGE_PATH)
    image_np = np.array(img)

    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
              for key, value in detections.items()}
    detections['num_detections'] = num_detections

    detection_threshold = 0.3

    scores = list(filter(lambda x: x> detection_threshold, detections['detection_scores']))
    boxes = detections['detection_boxes'][:len(scores)]
    classes = detections['detection_classes'][:len(scores)]

    width = image_np.shape[1]
    height = image_np.shape[0]
    try:
        for idx, box in enumerate(boxes):
            roi = box*[height, width, height, width]
            region = image_np[int(roi[0]):int(roi[2]),int(roi[1]):int(roi[3])]
        
        color_coverted = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)
        
        cropped_image = Image.fromarray(region)

        cropped_image.save("cropped_image.jpg")

        cropped_image_path = "./cropped_image.jpg"

        client = vision.ImageAnnotatorClient()

        with io.open(cropped_image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations

        if response.error.message:
            raise Exception(
                    '{}\nFor more info on error messages, check: '
                    'https://cloud.google.com/apis/design/errors'.format(
                        response.error.message))

        full_text = texts[0].description
        # print(texts)
        # print(full_text)
        if full_text.count('\n') == 1:
            plate1 = full_text.replace('\n', '')
            # print(plate1)
        # print(texts)

        if full_text.count('\n') > 1:
            rectangle_size = response.full_text_annotation.pages[0].width*response.full_text_annotation.pages[0].height
            # print(rectangle_size)
            region_threshold = 0.05
            plate = [] 
            for result in texts[1:]:
                length = np.sum(np.subtract(result.bounding_poly.vertices[1].x, result.bounding_poly.vertices[0].x))
                height = np.sum(np.subtract(result.bounding_poly.vertices[3].y, result.bounding_poly.vertices[0].y))

                # print((length*height) / rectangle_size)    
                if ((length*height) / rectangle_size) > region_threshold:
                    plate.append(result.description) 

            plate1 = ''.join(plate)
            # print(plate1)

        plate1 = plate1.replace('\n', '')
        plate1 = plate1.replace(' ', '')
        

        url = "http://enigmatic-thicket-80643.herokuapp.com/api/vehicle/vehiclePlate"
        print("Image Detected")
        image = {"plate": plate1}
        x = requests.post(url, json = image)

        return "Sent Successfully"
        
    except:
        print("Image not detected")
        return "Image is not proper!!!!!"

@app.post("/get_number")
async def create_upload_files(request: Request):

    form = await request.form()
    contents = await form["files"].read()
    with open('image1.jpg', 'wb') as f:
        f.write(contents)

    IMAGE_PATH = 'image1.jpg'

    img = cv2.imread(IMAGE_PATH)
    image_np = np.array(img)

    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor)

    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy()
              for key, value in detections.items()}
    detections['num_detections'] = num_detections

    detection_threshold = 0.3

    scores = list(filter(lambda x: x> detection_threshold, detections['detection_scores']))
    boxes = detections['detection_boxes'][:len(scores)]
    classes = detections['detection_classes'][:len(scores)]

    width = image_np.shape[1]
    height = image_np.shape[0]

    for idx, box in enumerate(boxes):
        roi = box*[height, width, height, width]
        region = image_np[int(roi[0]):int(roi[2]),int(roi[1]):int(roi[3])]

    color_coverted = cv2.cvtColor(region, cv2.COLOR_BGR2RGB)

    cropped_image = Image.fromarray(color_coverted)

    cropped_image.save("cropped_image1.jpg")

    cropped_image_path = "./cropped_image1.jpg"

    client = vision.ImageAnnotatorClient()

    with io.open(cropped_image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)

    if response.error.message:
        raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

    texts = response.text_annotations
    full_text = texts[0].description
    # print(texts)
    # print(full_text)
    if full_text.count('\n') == 1:
        plate1 = full_text.replace('\n', '')
        # print(plate1)
    # print(texts)

    if full_text.count('\n') > 1:
        rectangle_size = response.full_text_annotation.pages[0].width*response.full_text_annotation.pages[0].height
        # print(rectangle_size)
        region_threshold = 0.05
        plate = [] 
        for result in texts[1:]:
            length = np.sum(np.subtract(result.bounding_poly.vertices[1].x, result.bounding_poly.vertices[0].x))
            height = np.sum(np.subtract(result.bounding_poly.vertices[3].y, result.bounding_poly.vertices[0].y))


            # print((length*height) / rectangle_size)    
            if ((length*height) / rectangle_size) > region_threshold:
                plate.append(result.description) 

        plate1 = ''.join(plate)
        # print(plate1)

    plate1 = plate1.replace('\n', '')
    plate1 = plate1.replace(' ', '')
    image = {"plate": plate1}
    content = f"""
            <h1>{image}</h1>
        """
    return HTMLResponse(content=content)


@app.get("/upload_file")
async def main():
    content = """
<body>
<form action="/get_number" enctype="multipart/form-data" method="post">
<input name="files" type="file">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
    

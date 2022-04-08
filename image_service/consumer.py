import asyncio
import shutil
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Request, UploadFile, File
import base64
import datetime
import io
import os
from PIL import Image
import numpy as np
import cv2
import json
from confluent_kafka import Consumer
from producer import SendImageUrlProducer
from models import ImagesModel
from pathlib import Path
from PIL import ImageFile
import database
import nest_asyncio
nest_asyncio.apply()

BASE_DIR = Path(__file__).resolve().parent.parent

get_db = database.get_db


async def upload_image(id,
                       save_image,
                       image_name,
                       file: UploadFile = File(...),
                       db: Session = Depends(get_db)
                       ):

    file = save_image
    file_location = f"media/{file.filename}"

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    object = ImagesModel(image=file_location)
    db.add(object)
    db.commit()
    db.refresh()

    print("Image Uploaded SuccessFully!")

consumer = Consumer(
    {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'IMAGE-ID',
        'auto.offset.reset': 'latest',
        'enable.auto.commit': 'false',
        'max.poll.interval.ms': '86400000'
    }
)

consumer.subscribe(['dater-image', ])

while True:
    msg = consumer.poll(1.0)
    print(msg)
    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    objects = msg.value().decode('utf8')  # decode Json
    obj = json.loads(objects)  # converts "" into '' with loads
    my_img = obj['image']  # assign the image dict to my_img
    my_image = base64.b64decode(my_img)  # base64 decode to the image object

    # converts image str bas64 to np array form using buffer
    image_arr = np.frombuffer(my_image, dtype=np.uint8)

    # uses python-cv to decode the image array into original form
    image_dat = cv2.imdecode(image_arr, flags=1)

    directory_name = "media"
    if os.path.isdir(directory_name):
        pass
    else:
        os.makedirs(directory_name)

    try:
        image_path_user = os.path.join(BASE_DIR, 'media/user')
    except:
        dir = os.path.join(BASE_DIR, 'media/user')
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
        image_path_user = dir

    image_name = str(datetime.datetime.now().strftime(
        "%Y_%m_%d_%H_%M_""%S_%f") + ".png")

    if obj['type'] == 'Image':
        image = Image.open(io.BytesIO(image_arr))

        save_image = image.save(os.path.join(
            image_path_user, image_name))

        print("Done")
        # asyncio.run(upload_image(obj['id'], save_image, image_name))

        # try:
        #     ImagesModel.objects.get(user_id=obj['id'])

        # image = Image.open(io.BytesIO(image_arr))

        # save_image = image.save(os.path.join(
        #     image_path_user, image_name))

        #     my_image = ImagesModel.objects.get(user_id=obj['id'])
        #     my_image.user_img = ImageFile(
        #         open('media/user/' + image_name, "rb"))
        #     my_image.save()

        #     # delete the local image file
        #     try:
        #         os.remove(os.path.join(image_path_user, image_name))
        #     except Exception as e:
        #         print(str(e))

        #     print('Updated image with success')

        # except:

        #     image = Image.open(io.BytesIO(image_arr))

        #     save_image = image.save(os.path.join(image_path_user, image_name))

        #     img1 = ImagesModel.objects.create(title=obj['title'],
        #                                      user_img=ImageFile(
        #         open('media/user/' + image_name, "rb")),
        #         type=obj['type'],
        #         user_id=obj['id'])

        #     img_obj = ImagesModel.objects.get(pk=img1.id)
        #     image_id = img_obj.id
        #     image_user_id = img_obj.user_id

        #     # delete the local image file
        #     try:
        #         os.remove(os.path.join(image_path_user, image_name))
        #     except Exception as e:
        #         print(str(e))

        #     print('wrote image with success')

        #     producer = SendImageUrlProducer()
        #     my_obj = {
        #         "image_id": str(image_id),
        #         "user_id": str(image_user_id),
        #         "image_type": "Image"
        #     }
        #     producer.send_msg_async(json.dumps(my_obj))

    else:

        print("You are suspicious!")

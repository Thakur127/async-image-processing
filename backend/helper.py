import pandas as pd
from PIL import Image
import requests
import os
from io import BytesIO

from crud import crud
from schema.file import FileRequest

DOMAIN_NAME = "http://localhost:8000"


def validate_file(content):
    try:
        df = pd.read_csv(BytesIO(content))
        if set(df.columns) != {"product_name", "serial_no", "input_image_urls"}:
            return False
        return True
    except:
        return False


def process_file(db, content, request_id: str):

    # read buffer content into pandas dataframe
    df = pd.read_csv(BytesIO(content))

    request_output_directory = os.path.join("static", "images", request_id)

    if not os.path.exists(request_output_directory):
        os.makedirs(request_output_directory)

    output_image_urls = []

    for index, row in df.iterrows():
        serial_no = row["serial_no"]
        input_image_urls = row["input_image_urls"].split(",")

        serial_output_directory = os.path.join(request_output_directory, str(serial_no))

        if not os.path.exists(serial_output_directory):
            os.makedirs(serial_output_directory)

        image_url_string = ""

        # process each image urls
        for idx, image_url in enumerate(input_image_urls):
            image_url = image_url.strip()
            try:
                response = requests.get(image_url)

                # Check if the request was successful
                response.raise_for_status()

                img = Image.open(BytesIO(response.content))

                # Convert to RGB mode to handle different image formats
                img = img.convert("RGB")

                # Save the image with 50% quality
                width, height = img.width // 2, img.height // 2
                img = img.resize((width, height))
                img_path = os.path.join(serial_output_directory, f"{idx}.jpg")
                img.save(img_path, "JPEG", quality=50, optimize=True)
                print(f"Saved {img_path}")

                # prepare output image url to add into new column
                if image_url_string == "":
                    image_url_string += DOMAIN_NAME + "/" + img_path
                else:
                    image_url_string += ", " + DOMAIN_NAME + "/" + img_path

            except requests.exceptions.RequestException as e:
                print(f"Error fetching image {image_url}: {e}")
            except Exception as e:
                print(f"Error processing image {image_url}: {e}")

        output_image_urls.append(image_url_string)

    # save processed image to new column
    df["output_image_urls"] = output_image_urls

    # save new updated file to storage
    csv_file_directory = os.path.join("static", "csv")
    if not os.path.exists(csv_file_directory):
        os.makedirs(csv_file_directory)

    new_csv_path = os.path.join("static", "csv", f"{request_id}.csv")
    df.to_csv(new_csv_path, index=False)

    # change processing status
    db_request: FileRequest = crud.get_request(db, request_id=request_id)
    if db_request:
        print("updating status for request id: ", db_request.request_id)
        crud.update_request(db, request_id=request_id, status="completed")
        print("update successfull")

        print("saving file path into the database")
        crud.create_file(
            db, request_id=request_id, file_path=DOMAIN_NAME + "/" + new_csv_path
        )
        print("file saved successfully")

import numpy as np
import easyocr
import pytesseract
from database_con import dbEntry
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
def filter_text(region, ocr_result, region_threshold):
    rectangle_size = region.shape[0] * region.shape[1]
    plate = []
    for result in ocr_result:
        length = np.sum(np.subtract(result[0][1], result[0][0]))
        height = np.sum(np.subtract(result[0][2], result[0][1]))
        if length * height / rectangle_size > region_threshold:
            plate.append(result[1])
    return plate

def ocr_it(image, detections, detection_threshold, region_threshold):
    # detection_threshold1=0.9
    # plate = []
    scores = list(filter(lambda x: x > detection_threshold , detections['detection_scores']))
    boxes = detections['detection_boxes'][:len(scores)]
    classes = detections['detection_classes'][:len(scores)]
    width = image.shape[1]
    height = image.shape[0]
    for idx, box in enumerate(boxes):
        roi = box * [height, width, height, width]
        region = image[int(roi[0]):int(roi[2]), int(roi[1]):int(roi[3])]
        reader = easyocr.Reader(['en'],gpu=True , verbose=False)
        # ocr_result = pytesseract.image_to_string(region)
        # print(ocr_result)
        ocr_result = reader.readtext(region)
        text = filter_text(region, ocr_result, region_threshold)
        # plate.append(ocr_result)
        # print(plate[0])
        # return ocr_result
        return text
        
def save_results(number_plate):
    if not number_plate :
        pass
    else:
        # num_plate = ""
        # for i in  number_plate :
        #     num_plate += i
        dbEntry(number_plate)

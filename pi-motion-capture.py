import cv2, os.path

config = {
    'captureDevice': 0,
    'minContourArea': 5000,
    'backgroundSubtractionAlgorithm': cv2.createBackgroundSubtractorMOG2(),
    'frameWidth': 1640,
    'frameAspectRatio': 4/3,
    'cropX1Fraction': 0.4,
    'cropX2Fraction': 0.6,
    'cropY1Fraction': 0.4,
    'cropY2Fraction': 0.6,
    'boxColour': {
        'r': 255,
        'g': 0,
        'b': 0
    },
    'boxThickness': 2,
    'imgOutDir': 'web/images',
    'imgFileNamePrefix': 'cam'
}

frame_width = config['frameWidth']
frame_height = int(config['frameWidth'] / config['frameAspectRatio'])

capture = cv2.VideoCapture(config['captureDevice'])
capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

cropY1 = int(frame_height * config['cropY1Fraction'])
cropY2 = int(frame_height * config['cropY2Fraction'])
cropX1 = int(frame_width * config['cropX1Fraction'])
cropX2 = int(frame_width * config['cropX2Fraction'])

box_colour = (config['boxColour']['b'], config['boxColour']['g'], config['boxColour']['r'])

if not capture.isOpened:
    print('Unable to open capture')
    exit(1)

img_index = 1
while True:
    ret, colour_frame = capture.read()
    if colour_frame is None:
        break

    cropped_colour_frame = colour_frame[cropY1:cropY2, cropX1:cropX2]
    gray_frame = cv2.cvtColor(cropped_colour_frame.copy(), cv2.COLOR_BGR2GRAY)
    foreground_mask = config['backgroundSubtractionAlgorithm'].apply(gray_frame)
    contours = cv2.findContours(foreground_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    for contour in contours:
        if cv2.contourArea(contour) < config['minContourArea']:
            continue
        print(img_index, 'box', cv2.contourArea(contour), cv2.boundingRect(contour))
        (x, y, w, h) = cv2.boundingRect(contour)
        cropped_colour_frame = cv2.rectangle(cropped_colour_frame, (x, y), (x + w, y + h), box_colour, config['boxThickness'])
        img_file_name = os.path.join(config['imgOutDir'], '{}{:06d}.jpg'.format(config['imgFileNamePrefix'], img_index))
        cv2.imwrite(img_file_name, colour_frame)
        img_index += 1

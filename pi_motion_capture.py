import cv2, os.path, threading


class MotionCapture:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.worker_thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._run)
            self.worker_thread.start()

    def _run(self):
        frame_width = self.config['frameWidth']
        frame_height = int(self.config['frameWidth'] / self.config['frameAspectRatio'])

        capture = cv2.VideoCapture(self.config['captureDevice'])
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

        cropY1 = int(frame_height * self.config['cropY1Fraction'])
        cropY2 = int(frame_height * self.config['cropY2Fraction'])
        cropX1 = int(frame_width * self.config['cropX1Fraction'])
        cropX2 = int(frame_width * self.config['cropX2Fraction'])

        box_colour = (self.config['boxColour']['b'], self.config['boxColour']['g'], self.config['boxColour']['r'])

        if not capture.isOpened:
            print('Unable to open capture')
            exit(1)

        img_index = 1

        print('Starting motion capture')
        while self.running:
            ret, colour_frame = capture.read()
            if colour_frame is None:
                break

            cropped_colour_frame = colour_frame[cropY1:cropY2, cropX1:cropX2]
            gray_frame = cv2.cvtColor(cropped_colour_frame.copy(), cv2.COLOR_BGR2GRAY)
            foreground_mask = self.config['backgroundSubtractionAlgorithm'].apply(gray_frame)
            contours = cv2.findContours(foreground_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

            for contour in contours:
                if cv2.contourArea(contour) < self.config['minContourArea']:
                    continue
                print(img_index, 'box', cv2.contourArea(contour), cv2.boundingRect(contour))
                (x, y, w, h) = cv2.boundingRect(contour)
                cropped_colour_frame = cv2.rectangle(cropped_colour_frame, (x, y), (x + w, y + h), box_colour, self.config['boxThickness'])
                img_file_name = os.path.join(self.config['imageDir'], '{}{:06d}.jpg'.format(self.config['imgFileNamePrefix'], img_index))
                cv2.imwrite(img_file_name, colour_frame)
                img_index += 1

        print('Stopping motion capture')

    def stop(self):
        self.running = False

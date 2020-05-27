import cv2, os.path, threading


class MotionCapture:
    TASK_CAPTURE = 'capture'
    TASK_SNAPSHOT = 'snapshot'
    TASK_CONFIG = 'config'
    TASK_STOP = 'stop'

    def __init__(self, config, queue):
        self.config = config
        self.queue = queue
        self.capture = None
        self.running = False
        self.worker_thread = None
        self.take_snapshot = False
        self.image_index = 1

    def start(self):
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._process_queue)
            self.worker_thread.start()
            self.queue.put(MotionCapture.TASK_CONFIG)
            self.queue.put(MotionCapture.TASK_CAPTURE)

    def _process_queue(self):
        while self.running:
            task = self.queue.get()

            if task == MotionCapture.TASK_CAPTURE:
                self._do_capture()

            elif task == MotionCapture.TASK_SNAPSHOT:
                self._do_snapshot()

            elif task == MotionCapture.TASK_CONFIG:
                self._do_config()

            elif task == MotionCapture.TASK_STOP:
                break

            else:
                print('Unknown task:', task)

    def _do_config(self):
        frame_width = self.config['frameWidth']
        frame_height = int(self.config['frameWidth'] / self.config['frameAspectRatio'])

        self.capture = cv2.VideoCapture(self.config['captureDevice'])
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

        self.cropY1 = int(frame_height * self.config['cropY1Fraction'])
        self.cropY2 = int(frame_height * self.config['cropY2Fraction'])
        self.cropX1 = int(frame_width * self.config['cropX1Fraction'])
        self.cropX2 = int(frame_width * self.config['cropX2Fraction'])

        self.box_colour = (self.config['boxColour']['b'], self.config['boxColour']['g'], self.config['boxColour']['r'])

    def _do_capture(self):
        self.queue.put(MotionCapture.TASK_CAPTURE)
        ret, colour_frame = self.capture.read()

        if colour_frame is None:
            return

        cropped_colour_frame = colour_frame[self.cropY1:self.cropY2, self.cropX1:self.cropX2]
        gray_frame = cv2.cvtColor(cropped_colour_frame.copy(), cv2.COLOR_BGR2GRAY)
        foreground_mask = self.config['backgroundSubtractionAlgorithm'].apply(gray_frame)
        contours = cv2.findContours(foreground_mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

        for contour in contours:
            if cv2.contourArea(contour) < self.config['minContourArea']:
                continue
            print(self.image_index, 'box', cv2.contourArea(contour), cv2.boundingRect(contour))
            (x, y, w, h) = cv2.boundingRect(contour)
            cropped_colour_frame = cv2.rectangle(cropped_colour_frame, (x, y), (x + w, y + h), self.box_colour, self.config['boxThickness'])
            img_file_name = os.path.join(self.config['imageDir'], '{}{:06d}.jpg'.format(self.config['imgFileNamePrefix'], self.image_index))
            cv2.imwrite(img_file_name, cv2.cvtColor(colour_frame, cv2.COLOR_RGB2BGR))
            self.image_index += 1

    def _do_snapshot(self):
        ret, snapshot_frame = self.capture.read()
        snapshot_frame = cv2.rectangle(snapshot_frame.copy(), (self.cropX1, self.cropY1), (self.cropX2, self.cropY2), self.box_colour, self.config['boxThickness'])
        snapshot_file_name = os.path.join(self.config['imageDir'], self.config['snapshotFile'])
        cv2.imwrite(snapshot_file_name, cv2.cvtColor(snapshot_frame, cv2.COLOR_RGB2BGR))

    def stop(self):
        self.queue.put(MotionCapture.TASK_STOP)



from pathlib import Path

import cv2 as cv
import numpy as np
from google.cloud import storage


class Task:
    bucket_name: str = "mfa-compute-demo"
    source_path: str = "data"

    def __init__(self):
        self.client = storage.Client()

    def run(self):
        for name in self.list_files():
            fn = self.download(name)
            print("process", fn)
            out_fn = self.compute(fn)
            self.upload(out_fn, prefix="results")
            self.move(fn)

    def list_files(self):
        blobs = self.client.list_blobs(self.bucket_name, prefix=self.source_path)
        for blob in blobs:
            yield blob.name

    def download(self, file_name):
        path = Path(self.source_path)
        path.mkdir(exist_ok=True)

        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(file_name)
        fn = path / Path(file_name).name
        blob.download_to_filename(str(fn))
        return fn

    def upload(self, file_name, prefix):
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.bucket_name)
        blob = bucket.blob(f"{prefix}/" + file_name.name)
        blob.upload_from_filename(str(file_name))

    def move(self, file_name):
        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(str(file_name))
        bucket.rename_blob(blob, "done/" + file_name.name)

    def compute(self, file_name):
        # code from https://docs.opencv.org/4.x/d8/dbc/tutorial_histogram_calculation.html
        src = cv.imread(cv.samples.findFile(str(file_name)))
        bgr_planes = cv.split(src)
        histSize = 256
        histRange = (0, histSize)
        b_hist = cv.calcHist(
            bgr_planes, [0], None, [histSize], histRange, accumulate=False
        )
        g_hist = cv.calcHist(
            bgr_planes, [1], None, [histSize], histRange, accumulate=False
        )
        r_hist = cv.calcHist(
            bgr_planes, [2], None, [histSize], histRange, accumulate=False
        )
        hist_w = 512
        hist_h = 400
        bin_w = int(round(hist_w / histSize))
        histImage = np.zeros((hist_h, hist_w, 3), dtype=np.uint8)
        cv.normalize(b_hist, b_hist, alpha=0, beta=hist_h, norm_type=cv.NORM_MINMAX)
        cv.normalize(g_hist, g_hist, alpha=0, beta=hist_h, norm_type=cv.NORM_MINMAX)
        cv.normalize(r_hist, r_hist, alpha=0, beta=hist_h, norm_type=cv.NORM_MINMAX)
        for i in range(1, histSize):
            cv.line(
                histImage,
                (bin_w * (i - 1), hist_h - int(b_hist[i - 1])),
                (bin_w * (i), hist_h - int(b_hist[i])),
                (255, 0, 0),
                thickness=2,
            )
            cv.line(
                histImage,
                (bin_w * (i - 1), hist_h - int(g_hist[i - 1])),
                (bin_w * (i), hist_h - int(g_hist[i])),
                (0, 255, 0),
                thickness=2,
            )
            cv.line(
                histImage,
                (bin_w * (i - 1), hist_h - int(r_hist[i - 1])),
                (bin_w * (i), hist_h - int(r_hist[i])),
                (0, 0, 255),
                thickness=2,
            )
        path = Path("results")
        path.mkdir(exist_ok=True)
        fn = path / file_name.name
        cv.imwrite(str(fn), histImage)
        return fn


if __name__ == "__main__":
    t = Task()
    t.run()

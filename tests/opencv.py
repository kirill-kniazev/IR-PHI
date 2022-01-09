import numpy as np
import cv2
import time

cv2.namedWindow('img', cv2.WINDOW_NORMAL)

start = time.time()
for i in range(5000):
    A = np.random.randn(100,100)
    cv2.imshow("img", A)
    cv2.waitKey(1)  # it's needed, but no problem, it won't pause/wait
print(time.time() - start)

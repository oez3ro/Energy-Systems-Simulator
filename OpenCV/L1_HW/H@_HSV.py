import cv2

img = cv2.imread('landscape.png', 1)

hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.imshow('img_hsv', hsv_img)
cv2.imwrite('lndscpsv.png', hsv_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
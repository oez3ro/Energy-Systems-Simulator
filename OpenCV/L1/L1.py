import cv2

img = cv2.imread('image.png', cv2.IMREAD_COLOR)
cv2.imshow('Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

imgbw = cv2.imread('image.png', 0)
cv2.imshow('B&W Image', imgbw)
cv2.imwrite('B&W.png', imgbw)
cv2.waitKey(0)
cv2.destroyAllWindows()
import cv2

#Overlayed
img_b = cv2.imread('image_berry.png', 1)
img_l = cv2.imread('image_leaf.png', 1)
img_l = cv2.resize(img_l, (img_b.shape[1], img_b.shape[0]))
wghtdsum = cv2.addWeighted(img_b, 0.5, img_l, 0.4, 0)

cv2.imshow('weightedimage', wghtdsum)
cv2.waitKey(0)
cv2.destroyAllWindows()


#Subtracted
sub = cv2.subtract(img_b, img_l)
cv2.imshow('subtractedimage', sub)

cv2.waitKey(0)
cv2.destroyAllWindows()
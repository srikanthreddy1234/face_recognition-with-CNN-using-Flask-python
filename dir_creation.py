import employee as em
import cv2
import importlib
import sys

def dir(name,uid,email):
    try:
        emp_id,emp_name=em.employee_entry(name,uid,email)
        count = 1
        path=em.dir_create(emp_id)
        print("your data is taken")
        cap=cv2.VideoCapture(0)      
        while True:
            ret,test_img=cap.read()
            if not ret :
                continue
            cv2.imwrite(path+"/"+"%d.jpg" % count, test_img)     # save frame as JPG file
            count += 1
            resized_img = cv2.resize(test_img, (1000, 700))
            print("your data is taken2")
            cv2.imshow(emp_id,resized_img)
            print("your data is taken3")
            if cv2.waitKey(10) == ord('q') or count == 200:#wait until 'q' key is pressed
                print("thank you we will train my system please wait.")
                cap.release()
                cv2.destroyAllWindows()
                break
        
        print("your data is taken")
    except:
        print("contact your ")

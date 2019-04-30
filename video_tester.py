from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import tensorflow as tf
from scipy import misc
import cv2
import numpy as np
import facenet
import detect_face
import os
import time
import pickle
import employee as em
import datetime
import csv



db=em.db_connect()
emp=db.employee
att=db.att_test
modeldir = './model/20170511-185253.pb'
classifier_filename = './class/classifier.pkl'
npy='./npy'
train_img="./static/people_photo/train_img"
now = datetime.datetime.now()
date=str(now.strftime("%Y-%m-%d"))
flag=0
flag1=0

with tf.Graph().as_default():
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
    with sess.as_default():
        pnet, rnet, onet = detect_face.create_mtcnn(sess, npy)

        minsize = 20  # minimum size of face
        threshold = [0.6, 0.7, 0.7]  # three steps's threshold
        factor = 0.709  # scale factor
        margin = 44
        frame_interval = 3
        batch_size = 1000
        image_size = 182
        input_image_size = 160
        
        Emp_id = os.listdir(train_img)
        Emp_id.sort()

        print('Loading Modal')
        facenet.load_model(modeldir)
        images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        embedding_size = embeddings.get_shape()[1]


        classifier_filename_exp = os.path.expanduser(classifier_filename)
        with open(classifier_filename_exp, 'rb') as infile:
            (model, class_names) = pickle.load(infile)

        # video_capture = cv2.VideoCapture('http://192.168.31.38:8081/')
        video_capture = cv2.VideoCapture(0)

        c = 0


        print('Start Recognition')
        prevTime = 0
        while True:
            ret, frame = video_capture.read()

            frame = cv2.resize(frame, (0,0), fx=1.0, fy=0.9)    #resize frame (optional)

            curTime = time.time()+1    # calc fps
            timeF = frame_interval

            if (c % timeF == 0):
                find_results = []

                if frame.ndim == 2:
                    frame = facenet.to_rgb(frame)
                frame = frame[:, :, 0:3]
                bounding_boxes, _ = detect_face.detect_face(frame, minsize, pnet, rnet, onet, threshold, factor)
                nrof_faces = bounding_boxes.shape[0]
                print('Detected_FaceNum: %d' % nrof_faces)

                if nrof_faces > 0:
                    det = bounding_boxes[:, 0:4]
                    img_size = np.asarray(frame.shape)[0:2]

                    cropped = []
                    scaled = []
                    scaled_reshape = []
                    bb = np.zeros((nrof_faces,4), dtype=np.int32)

                    for i in range(nrof_faces):
                        emb_array = np.zeros((1, embedding_size))

                        bb[i][0] = det[i][0]
                        bb[i][1] = det[i][1]
                        bb[i][2] = det[i][2]
                        bb[i][3] = det[i][3]

                        # inner exception
                        if bb[i][0] <= 0 or bb[i][1] <= 0 or bb[i][2] >= len(frame[0]) or bb[i][3] >= len(frame):
                            print('Face is very close!')
                            continue

                        cropped.append(frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :])
                        cropped[i] = facenet.flip(cropped[i], False)
                        scaled.append(misc.imresize(cropped[i], (image_size, image_size), interp='bilinear'))
                        scaled[i] = cv2.resize(scaled[i], (input_image_size,input_image_size),
                                               interpolation=cv2.INTER_CUBIC)
                        scaled[i] = facenet.prewhiten(scaled[i])
                        scaled_reshape.append(scaled[i].reshape(-1,input_image_size,input_image_size,3))
                        feed_dict = {images_placeholder: scaled_reshape[i], phase_train_placeholder: False}
                        emb_array[0, :] = sess.run(embeddings, feed_dict=feed_dict)
                        predictions = model.predict_proba(emb_array)
                        print(predictions)
                        best_class_indices = np.argmax(predictions, axis=1)
                        best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
                        # print("predictions")
                        print(best_class_indices,' with accuracy ',best_class_probabilities)

                        # print(best_class_probabilities)
                        if best_class_probabilities>0.63:
                            cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (79, 79,47), 2)    #boxing face

                            #plot result idx under box
                            text_x = bb[i][0]
                            text_y = bb[i][3] + 20
                            att_x = bb[i][0]
                            att_y = bb[i][3]+40
                            print('Result Indices: ', best_class_indices[0])
                            print(Emp_id)
                            for E_i in Emp_id:
                                if Emp_id[best_class_indices[0]] == E_i:
                                    result_id = Emp_id[best_class_indices[0]]
                                    result_id=str(result_id)
                                    empl=emp.find({"emp_id":result_id})
                                    for emp_name in empl:    
                                        predicted_name=emp_name["name"]
                                        Email_id=emp_name["Email_id"]
                                    if flag==0:
                                        cv2.putText(frame,predicted_name, (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                    1, (0, 0, 255), thickness=1, lineType=2)
                                    else:
                                        predicted_att=" your attendance has taken"
                                        cv2.putText(frame,predicted_att , (att_x, att_y), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                    1, (0, 0, 255), thickness=1, lineType=2)
                                        cv2.putText(frame,predicted_name , (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                                    1, (0, 0, 255), thickness=1, lineType=2)
                                    emp_count=att.find({"date":date,"emp_id":result_id}).count()
                                    if emp_count==0:
                                        name=predicted_name
                                        time1=now.strftime("%H:%M")
                                        month=now.strftime("%m")
                                        employee={"emp_id":result_id,
                                                  "name":name,
                                                  "date":date,
                                                  "month":month,
                                                  "In_time":time1,
                                                  "out_time":""
                                                }
                                        result=att.insert_one(employee)
                                        if result.acknowledged:
                                            print("inserted your details")
                                            print("your attendence is taken")
                                            subjt="Attendence "+date+" "+name
                                            msg="Dear "+name+",\n Your attendence has logged as present for "+str(date)+" :"+str(time1)
                                            em.emailToEmp(Email_id,msg,subjt)
                                    else:
                                        flag=1
                else:
                    print('Alignment Failure')
            # c+=1
            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            timeH=str(now.strftime("%H:%M"))
            print(timeH)
            emp_listT=[]
            if flag1==1:
                continue
            else:
                if timeH == "17:28":
                    emp_list=att.find({"date":date},{"_id":False,"month":False,"out_time":False})
                    print(type(emp_list))
                    for x in emp_list:    
                        emp_listT.append(x)
                    print(emp_listT)

                    with open('temp.csv', 'w') as outfile:
                        fields = ['emp_id', 'name', 'date', 'In_time']
                        write = csv.DictWriter(outfile, fieldnames=fields)
                        write.writeheader()
                        for empls  in emp_listT:
                            write.writerow(empls)
                    subjt="Attendence of "+date
                    msg="Dear Admin,\n Here is today attendence"
                    em.emailToAdmin("hanmanthreddy1221@gmail.com",msg,subjt)
                    flag1=1



        video_capture.release()
        cv2.destroyAllWindows()
